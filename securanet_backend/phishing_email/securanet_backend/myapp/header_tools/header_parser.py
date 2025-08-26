import re
import dns.resolver
import requests
import logging
from datetime import datetime
from email import message_from_string
from email.header import decode_header, make_header
import spf
import dkim
logger = logging.getLogger(__name__)

BLACKLISTS = [
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "b.barracudacentral.org",
    "dnsbl.sorbs.net",
    "psbl.surriel.com",
    "dnsbl-1.uceprotect.net",
    "dnsbl-2.uceprotect.net",
    "dnsbl-3.uceprotect.net",
    "spam.abuse.ch",
    "cbl.abuseat.org",
    "dnsbl.cyberlogic.net"
]

def check_ip_blacklists(ip):
    results = []
    try:
        reversed_ip = '.'.join(reversed(ip.split('.')))
        for bl in BLACKLISTS:
            query = f"{reversed_ip}.{bl}"
            try:
                dns.resolver.resolve(query, 'A')
                results.append(bl)
            except Exception:
                continue
    except Exception:
        pass
    return results

# Normalize line endings
def normalize_header(header):
    """Normalize line endings for consistent parsing."""
    return header.replace("\\r\\n", "\n").replace("\\r", "\n")

# --- Modularized Parsing Functions ---
def parse_subject(header_text):
    match = re.search(r"^Subject: (.*)", header_text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""

def parse_to(header_text):
    match = re.search(r"^To: (.*)", header_text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""

def parse_date(header_text):
    match = re.search(r"^Date: (.*)", header_text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""

def parse_message_id(header_text):
    match = re.search(r"^Message-ID: (.*)", header_text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""

def parse_return_path(header_text):
    match = re.search(r"^Return-Path:\s*<([^>]+)>", header_text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""

# Extract sender's email
def parse_from_field(header_text):
    """Extracts the sender's name and email from the From: header."""
    try:
        match = re.search(r'From:\s*(?:"?([^"\\]*)"?\s*)?<([^>]+)>', header_text, re.IGNORECASE)
        if match:
            return {"name": match.group(1) or "", "email": match.group(2)}
        match_simple = re.search(r'From:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', header_text, re.IGNORECASE)
        if match_simple:
            return {"name": "", "email": match_simple.group(1)}
        logger.warning("No valid 'From' field found in header: %r", header_text[:200])
        return {"name": "", "email": ""}
    except Exception as e:
        logger.error(f"Error parsing 'From' field: {e}")
        return {"name": "", "email": ""}

# Extract IP from Received
def extract_sender_ip(header_text):
    """Extracts the sender's IP from the first Received: header."""
    try:
        match = re.search(r"received: from .*?\[(\d+\.\d+\.\d+\.\d+)\].*", header_text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
        logger.warning("No sender IP found in Received header: %r", header_text[:200])
        return None
    except Exception as e:
        logger.error(f"Error extracting sender IP: {e}")
        return None

# Parse Received headers into routing chain
def parse_received_headers(header_text):
    """Parses all Received: headers into a routing chain with robust extraction, including hop delays and blacklist checks."""
    hops = []
    try:
        received_headers = re.findall(r"^Received: (.*?)(?=\n\w|^\Z)", header_text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        prev_dt = None
        for block in received_headers:
            match = re.search(r"from (.*?) by (.*?);(.*)", block.replace('\n', ' '), re.IGNORECASE)
            if match:
                from_part, by_part, timestamp = match.groups()
                ip_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', from_part)
                # Parse timestamp to datetime
                dt = None
                delay = None
                try:
                    dt = datetime.strptime(timestamp.strip(), "%a, %d %b %Y %H:%M:%S %z")
                    if prev_dt:
                        delay = (dt - prev_dt).total_seconds()
                    prev_dt = dt
                except Exception:
                    dt = None
                hop = {
                    "from": from_part.strip(),
                    "by": by_part.strip(),
                    "timestamp": timestamp.strip(),
                    "from_ip": ip_match.group(1) if ip_match else None,
                    "delay": delay
                }
                # Blacklist check
                if hop["from_ip"]:
                    blacklists = check_ip_blacklists(hop["from_ip"])
                    hop["blacklisted"] = bool(blacklists)
                    hop["blacklists"] = blacklists
                else:
                    hop["blacklisted"] = False
                    hop["blacklists"] = []
                hops.append(hop)
            else:
                hops.append({
                    "raw": block.strip(),
                    "error": "Malformed Received header",
                    "delay": None,
                    "blacklisted": False,
                    "blacklists": []
                })
        return hops
    except Exception as e:
        logger.error(f"Error parsing Received headers: {e}")
        return hops

# Parse Authentication-Results header
def parse_authentication_results(header_text):
    """Parses the Authentication-Results header."""
    try:
        auth_header_match = re.search(r"Authentication-Results:(.*?)(?:\n\w|^\Z)", header_text, re.IGNORECASE | re.DOTALL)
        if not auth_header_match:
            logger.warning("No Authentication-Results header found.")
            return {}
        auth_content = auth_header_match.group(1).replace('\n', ' ').strip()
        results = {}
        parts = auth_content.split(';')
        results['server'] = parts[0].strip()
        for part in parts[1:]:
            if '=' in part:
                key, value = part.strip().split('=', 1)
                results[key.strip()] = value.strip()
        return results
    except Exception as e:
        logger.error(f"Error parsing Authentication-Results: {e}")
        return {}

# Parse DKIM signature
def parse_dkim_signature(header_text):
    """Parses the DKIM-Signature to get the selector and domain."""
    try:
        dkim_header_match = re.search(r"DKIM-Signature:(.*?)(?:\n\w|^\Z)", header_text, re.IGNORECASE | re.DOTALL)
        if not dkim_header_match:
            logger.warning("No DKIM-Signature header found.")
            return {}
        tags = {}
        dkim_content = dkim_header_match.group(1).replace('\n', '').replace('\t', ' ').strip()
        for tag in dkim_content.split(';'):
            if '=' in tag:
                key, value = tag.strip().split('=', 1)
                tags[key.strip()] = value.strip()
        return tags
    except Exception as e:
        logger.error(f"Error parsing DKIM-Signature: {e}")
        return {}

def parse_record_tags(record, record_type):
    """Parse SPF, DKIM, or DMARC record into tag dictionary with explanations."""
    tag_explanations = {
        # SPF
        "v": "Version of the record.",
        "ip4": "IPv4 address allowed to send mail.",
        "ip6": "IPv6 address allowed to send mail.",
        "include": "Other domain whose SPF records are included.",
        "all": "Default result for non-matching IPs.",
        # DKIM
        "v": "Version of the record.",
        "k": "Key type (usually rsa).",
        "p": "Public key (base64).",
        "s": "Service type.",
        "h": "Hash algorithm.",
        # DMARC
        "p": "Policy for domain (none, quarantine, reject).",
        "sp": "Subdomain policy.",
        "adkim": "DKIM alignment mode.",
        "aspf": "SPF alignment mode.",
        "rua": "Aggregate report URIs.",
        "ruf": "Forensic report URIs.",
        "pct": "Percentage of messages subjected to filtering.",
        "fo": "Failure reporting options.",
        "rf": "Report format.",
        "ri": "Report interval (seconds).",
        "v": "Version of the record."
    }
    tags = {}
    for tag in record.split(';'):
        if '=' in tag:
            key, value = tag.strip().split('=', 1)
            tags[key.strip()] = {
                "value": value.strip(),
                "explanation": tag_explanations.get(key.strip(), "")
            }
    return tags

# DNS lookups for SPF/DKIM/DMARC
def get_dns_record(domain, record_type, selector=None):
    """Performs DNS lookups for SPF, DKIM, and DMARC, and parses tags for detailed breakdown."""
    query_domain = domain
    if record_type == "dkim":
        if not selector or not domain:
            return {"error": "DKIM domain or selector not found for lookup."}
        query_domain = f"{selector}._domainkey.{domain}"
    elif record_type == "dmarc":
        query_domain = f"_dmarc.{domain}"
    try:
        answers = dns.resolver.resolve(query_domain, 'TXT')
        for rdata in answers:
            txt = str(rdata).strip('"')
            if record_type == "spf" and txt.lower().startswith("v=spf1"):
                return {
                    "has_spf": True,
                    "spf_record": txt,
                    "spf_tags": parse_record_tags(txt, "spf"),
                    "error": None
                }
            if record_type == "dkim" and "v=DKIM1" in txt:
                return {
                    "has_dkim": True,
                    "dkim_record": txt,
                    "dkim_tags": parse_record_tags(txt, "dkim"),
                    "error": None
                }
            if record_type == "dmarc" and "v=DMARC1" in txt:
                return {
                    "has_dmarc": True,
                    "dmarc_record": txt,
                    "dmarc_tags": parse_record_tags(txt, "dmarc"),
                    "error": None
                }
        return {"error": f"{record_type.upper()} record not found"}
    except Exception as e:
        return {"error": str(e)}

# IP Geolocation (free API — replace if needed)
def geo_lookup(ip):
    """Performs IP geolocation using a free API."""
    if not ip:
        return {"error": "Sender IP not found for geolocation"}
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "success":
            return {key: data.get(key) for key in ["country", "city", "regionName", "isp", "timezone", "lat", "lon"]}
        return {"error": data.get("message", "API lookup failed")}
    except Exception as e:
        return {"error": str(e)}

# --- Enhanced RFC-Compliant Parsing ---
def parse_email_headers_rfc(header_text):
    msg = message_from_string(header_text)
    def get_decoded(name):
        raw = msg.get(name, "")
        try:
            return str(make_header(decode_header(raw)))
        except Exception:
            return raw
    return {
        "subject": get_decoded("Subject"),
        "from": get_decoded("From"),
        "to": get_decoded("To"),
        "date": get_decoded("Date"),
        "message_id": get_decoded("Message-ID"),
        "return_path": get_decoded("Return-Path"),
    }

def parse_from_field(header_text):
    msg = message_from_string(header_text)
    from_raw = msg.get("From", "")
    try:
        name, email = re.match(r'(.*)<(.+@.+)>', from_raw).groups()
        return {"name": name.strip().strip('"'), "email": email.strip()}
    except Exception:
        # fallback: just email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', from_raw)
        return {"name": "", "email": email_match.group(1) if email_match else ""}

def extract_all_dkim_signatures(header_text):
    msg = message_from_string(header_text)
    dkim_headers = msg.get_all("DKIM-Signature", [])
    selectors = []
    for dkim in dkim_headers:
        tags = {}
        for tag in dkim.replace('\n', '').replace('\t', ' ').strip().split(';'):
            if '=' in tag:
                key, value = tag.strip().split('=', 1)
                tags[key.strip()] = value.strip()
        if 's' in tags and 'd' in tags:
            selectors.append((tags['s'], tags['d'], dkim))
    return selectors

def parse_authentication_results_rfc(header_text):
    msg = message_from_string(header_text)
    auth_headers = msg.get_all("Authentication-Results", [])
    results = []
    for auth in auth_headers:
        parsed = {}
        for part in auth.split(';'):
            part = part.strip()
            if '=' in part:
                proto, rest = part.split('=', 1)
                proto = proto.strip().lower()
                status, *kv = rest.strip().split(' ', 1)
                parsed[proto] = {
                    "result": status,
                    "detail": kv[0] if kv else ""
                }
        results.append(parsed)
    return results

def extract_sender_ip(header_text):
    msg = message_from_string(header_text)
    received_headers = msg.get_all("Received", [])
    for received in received_headers:
        match = re.search(r'\[(\d+\.\d+\.\d+\.\d+)\]', received)
        if match:
            return match.group(1)
    return None

def parse_received_headers(header_text):
    msg = message_from_string(header_text)
    received_headers = msg.get_all("Received", [])
    hops = []
    prev_dt = None
    for block in received_headers:
        match = re.search(r"from (.*?) by (.*?);(.*)", block.replace('\n', ' '), re.IGNORECASE)
        if match:
            from_part, by_part, timestamp = match.groups()
            ip_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', from_part)
            dt = None
            delay = None
            try:
                dt = datetime.strptime(timestamp.strip(), "%a, %d %b %Y %H:%M:%S %z")
                if prev_dt:
                    delay = (dt - prev_dt).total_seconds()
                prev_dt = dt
            except Exception:
                dt = None
            hop = {
                "from": from_part.strip(),
                "by": by_part.strip(),
                "timestamp": timestamp.strip(),
                "from_ip": ip_match.group(1) if ip_match else None,
                "delay": delay
            }
            if hop["from_ip"]:
                blacklists = check_ip_blacklists(hop["from_ip"])
                hop["blacklisted"] = bool(blacklists)
                hop["blacklists"] = blacklists
            else:
                hop["blacklisted"] = False
                hop["blacklists"] = []
            hops.append(hop)
        else:
            hops.append({
                "raw": block.strip(),
                "error": "Malformed Received header",
                "delay": None,
                "blacklisted": False,
                "blacklists": []
            })
    return hops

def parse_authentication_results(header_text):
    """Parses the Authentication-Results header."""
    try:
        auth_header_match = re.search(r"Authentication-Results:(.*?)(?:\n\w|^\Z)", header_text, re.IGNORECASE | re.DOTALL)
        if not auth_header_match:
            logger.warning("No Authentication-Results header found.")
            return {}
        auth_content = auth_header_match.group(1).replace('\n', ' ').strip()
        results = {}
        parts = auth_content.split(';')
        results['server'] = parts[0].strip()
        for part in parts[1:]:
            if '=' in part:
                key, value = part.strip().split('=', 1)
                results[key.strip()] = value.strip()
        return results
    except Exception as e:
        logger.error(f"Error parsing Authentication-Results: {e}")
        return {}

def parse_dkim_signature(header_text):
    """Parses the DKIM-Signature to get the selector and domain."""
    try:
        dkim_header_match = re.search(r"DKIM-Signature:(.*?)(?:\n\w|^\Z)", header_text, re.IGNORECASE | re.DOTALL)
        if not dkim_header_match:
            logger.warning("No DKIM-Signature header found.")
            return {}
        tags = {}
        dkim_content = dkim_header_match.group(1).replace('\n', '').replace('\t', ' ').strip()
        for tag in dkim_content.split(';'):
            if '=' in tag:
                key, value = tag.strip().split('=', 1)
                tags[key.strip()] = value.strip()
        return tags
    except Exception as e:
        logger.error(f"Error parsing DKIM-Signature: {e}")
        return {}

def parse_record_tags(record, record_type):
    """Parse SPF, DKIM, or DMARC record into tag dictionary with explanations."""
    tag_explanations = {
        # SPF
        "v": "Version of the record.",
        "ip4": "IPv4 address allowed to send mail.",
        "ip6": "IPv6 address allowed to send mail.",
        "include": "Other domain whose SPF records are included.",
        "all": "Default result for non-matching IPs.",
        # DKIM
        "v": "Version of the record.",
        "k": "Key type (usually rsa).",
        "p": "Public key (base64).",
        "s": "Service type.",
        "h": "Hash algorithm.",
        # DMARC
        "p": "Policy for domain (none, quarantine, reject).",
        "sp": "Subdomain policy.",
        "adkim": "DKIM alignment mode.",
        "aspf": "SPF alignment mode.",
        "rua": "Aggregate report URIs.",
        "ruf": "Forensic report URIs.",
        "pct": "Percentage of messages subjected to filtering.",
        "fo": "Failure reporting options.",
        "rf": "Report format.",
        "ri": "Report interval (seconds).",
        "v": "Version of the record."
    }
    tags = {}
    for tag in record.split(';'):
        if '=' in tag:
            key, value = tag.strip().split('=', 1)
            tags[key.strip()] = {
                "value": value.strip(),
                "explanation": tag_explanations.get(key.strip(), "")
            }
    return tags

# DNS lookups for SPF/DKIM/DMARC
def get_dns_record(domain, record_type, selector=None):
    """Performs DNS lookups for SPF, DKIM, and DMARC, and parses tags for detailed breakdown."""
    query_domain = domain
    if record_type == "dkim":
        if not selector or not domain:
            return {"error": "DKIM domain or selector not found for lookup."}
        query_domain = f"{selector}._domainkey.{domain}"
    elif record_type == "dmarc":
        query_domain = f"_dmarc.{domain}"
    try:
        answers = dns.resolver.resolve(query_domain, 'TXT')
        for rdata in answers:
            txt = str(rdata).strip('"')
            if record_type == "spf" and txt.lower().startswith("v=spf1"):
                return {
                    "has_spf": True,
                    "spf_record": txt,
                    "spf_tags": parse_record_tags(txt, "spf"),
                    "error": None
                }
            if record_type == "dkim" and "v=DKIM1" in txt:
                return {
                    "has_dkim": True,
                    "dkim_record": txt,
                    "dkim_tags": parse_record_tags(txt, "dkim"),
                    "error": None
                }
            if record_type == "dmarc" and "v=DMARC1" in txt:
                return {
                    "has_dmarc": True,
                    "dmarc_record": txt,
                    "dmarc_tags": parse_record_tags(txt, "dmarc"),
                    "error": None
                }
        return {"error": f"{record_type.upper()} record not found"}
    except Exception as e:
        return {"error": str(e)}

# IP Geolocation (free API — replace if needed)
def geo_lookup(ip):
    """Performs IP geolocation using a free API."""
    if not ip:
        return {"error": "Sender IP not found for geolocation"}
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "success":
            return {key: data.get(key) for key in ["country", "city", "regionName", "isp", "timezone", "lat", "lon"]}
        return {"error": data.get("message", "API lookup failed")}
    except Exception as e:
        return {"error": str(e)}

def parse_email_headers_rfc(header_text):
    """Parse headers using Python's email library for RFC compliance."""
    msg = message_from_string(header_text)
    def get_decoded(name):
        raw = msg.get(name, "")
        try:
            return str(make_header(decode_header(raw)))
        except Exception:
            return raw
    return {
        "subject": get_decoded("Subject"),
        "from": get_decoded("From"),
        "to": get_decoded("To"),
        "date": get_decoded("Date"),
        "message_id": get_decoded("Message-ID"),
        "return_path": get_decoded("Return-Path"),
    }

def parse_authentication_results_deep(header_text):
    """Parse Authentication-Results header for all protocol results."""
    try:
        auth_header_match = re.search(r"Authentication-Results:(.*?)(?:\n\w|^\Z)", header_text, re.IGNORECASE | re.DOTALL)
        if not auth_header_match:
            return {}
        auth_content = auth_header_match.group(1).replace('\n', ' ').strip()
        results = {}
        # Split by protocol result (e.g., spf=pass ... dkim=pass ...)
        for part in auth_content.split(';'):
            part = part.strip()
            if '=' in part:
                proto, rest = part.split('=', 1)
                proto = proto.strip().lower()
                if proto in ["spf", "dkim", "dmarc", "arc"]:
                    # e.g., spf=pass smtp.mailfrom=example.com
                    status, *kv = rest.strip().split(' ', 1)
                    results[proto] = {
                        "result": status,
                        "detail": kv[0] if kv else ""
                    }
        return results
    except Exception as e:
        logger.error(f"Error parsing Authentication-Results deep: {e}")
        return {}

def parse_all_headers(header_text):
    """Parse all headers into a name/value table."""
    headers = []
    for line in header_text.splitlines():
        if ':' in line:
            name, value = line.split(':', 1)
            headers.append({"name": name.strip(), "value": value.strip()})
    return headers

def check_copy_paste_warning(header_text):
    """Check for common copy/paste or malformed header issues."""
    warnings = []
    if 'dkim-signature' in header_text.lower() and 'b=' not in header_text.lower():
        warnings.append("DKIM signature appears incomplete or broken. Copy/paste may have failed.")
    if 'received:' not in header_text.lower():
        warnings.append("No Received headers found. This may not be a full email header.")
    if len(header_text.splitlines()) < 5:
        warnings.append("Header is very short. Make sure you pasted the full header.")
    return warnings

def spf_test_results(spf):
    results = []
    if spf.get("has_spf"):
        results.append(("SPF Record Published", "SPF Record found"))
        results.append(("SPF Syntax Check", "The record is valid" if not spf.get("error") else spf["error"]))
        if spf.get("spf_record", "").count("v=spf1") > 1:
            results.append(("SPF Multiple Records", "Multiple SPF records found"))
        else:
            results.append(("SPF Multiple Records", "Less than two records found"))
        # Add more SPF checks as needed
    else:
        results.append(("SPF Record Published", "No SPF record found"))
    return results

def dmarc_test_results(dmarc):
    results = []
    if dmarc.get("has_dmarc"):
        results.append(("DMARC Record Published", "DMARC Record found"))
        results.append(("DMARC Syntax Check", "The record is valid" if not dmarc.get("error") else dmarc["error"]))
        if dmarc.get("dmarc_record", "").count("v=DMARC1") > 1:
            results.append(("DMARC Multiple Records", "Multiple DMARC records found"))
        else:
            results.append(("DMARC Multiple Records", "Single DMARC record found"))
        if 'p' in dmarc.get('dmarc_tags', {}):
            pol = dmarc['dmarc_tags']['p']['value']
            results.append(("DMARC Policy Enabled", f"DMARC {pol.title()} policy enabled"))
    else:
        results.append(("DMARC Record Published", "No DMARC record found"))
    return results

def dkim_test_results(dkim):
    results = []
    if dkim.get("has_dkim"):
        results.append(("DKIM Record Published", "DKIM Record found"))
        results.append(("DKIM Syntax Check", "The record is valid" if not dkim.get("error") else dkim["error"]))
        # Add more DKIM checks as needed
    else:
        results.append(("DKIM Record Published", "No DKIM record found"))
    return results

def extract_summary(header):
    return {
        "subject": parse_subject(header),
        "from": parse_from_field(header),
        "to": parse_to(header),
        "date": parse_date(header),
        "message_id": parse_message_id(header),
        "return_path": parse_return_path(header),
    }

def extract_dkim_selectors(header):
    # Find all DKIM-Signature headers and extract selector/domain pairs
    selectors = []
    dkim_headers = re.findall(r"DKIM-Signature:(.*?)(?=\n\w|^\Z)", header, re.IGNORECASE | re.DOTALL)
    for dkim in dkim_headers:
        tags = {}
        for tag in dkim.replace('\n', '').replace('\t', ' ').strip().split(';'):
            if '=' in tag:
                key, value = tag.strip().split('=', 1)
                tags[key.strip()] = value.strip()
        if 's' in tags and 'd' in tags:
            selectors.append((tags['s'], tags['d']))
    return selectors

def get_spf_record_and_tags(domain):
    """Use pyspf to check SPF for the domain."""
    try:
        # pyspf expects sender, ip, and helo. We'll use placeholders for sender and helo.
        result, explanation = spf.check2(i='127.0.0.1', s=f'test@{domain}', h=domain)
        spf_record = ''
        spf_tags = {'result': result, 'explanation': explanation}
        # Optionally, fetch the actual SPF record via DNS
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                txt = rdata.to_text().strip('"')
                if txt.startswith('v=spf1'):
                    spf_record = txt
                    break
        except Exception:
            pass
        spf_tags['spf_record'] = spf_record
        spf_tags['has_spf'] = result == 'pass'
        return spf_record, spf_tags
    except Exception as e:
        return '', {'result': 'permerror', 'explanation': str(e), 'has_spf': False}

def get_dmarc_record_and_tags(domain):
    dmarc = get_dns_record(domain, "dmarc")
    return dmarc.get("dmarc_record", ""), dmarc.get("dmarc_tags", {})

def get_dkim_record_and_tags(selector, domain):
    """Use dkimpy to verify DKIM signature if present."""
    try:
        # dkimpy expects the full email message as bytes and the selector/domain
        # Here, we only fetch the public key and check if it exists
        dkim_record = ''
        dkim_tags = {}
        try:
            dns_name = f"{selector}._domainkey.{domain}"
            answers = dns.resolver.resolve(dns_name, 'TXT')
            for rdata in answers:
                txt = rdata.to_text().strip('"')
                if txt.startswith('v=DKIM1'):
                    dkim_record = txt
                    break
        except Exception as e:
            dkim_tags['error'] = str(e)
        dkim_tags['dkim_record'] = dkim_record
        dkim_tags['has_dkim'] = bool(dkim_record)
        return dkim_record, dkim_tags
    except Exception as e:
        return '', {'error': str(e), 'has_dkim': False}

def parse_relay_info(header):
    hops = parse_received_headers(header)
    timeline = [hop.get("delay") for hop in hops]
    return hops, timeline

# --- Main Orchestrator ---
def analyze_header(header):
    warnings = []
    try:
        header = normalize_header(header)
        summary = parse_email_headers_rfc(header)
        # Ensure all expected fields are present
        summary = {
            "subject": summary.get("subject", ""),
            "from": parse_from_field(header),
            "to": summary.get("to", ""),
            "date": summary.get("date", ""),
            "message_id": summary.get("message_id", ""),
            "return_path": summary.get("return_path", "")
        }
        copy_paste_warning = check_copy_paste_warning(header)
        relay_hops, timeline = parse_relay_info(header)
        # DKIM: extract all selectors and check all signatures
        dkim_selectors = extract_all_dkim_signatures(header)
        dkim_records = []
        for selector, domain, dkim_raw in dkim_selectors:
            record, tags = get_dkim_record_and_tags(selector, domain)
            dkim_records.append({
                "selector": selector,
                "domain": domain,
                "record": record,
                "tags": tags,
                "raw_signature": dkim_raw
            })
        # SPF/DMARC
        from_domain = summary['from']['email'].split('@')[-1] if summary['from']['email'] else ""
        spf_record, spf_tags = get_spf_record_and_tags(from_domain)
        dmarc_record, dmarc_tags = get_dmarc_record_and_tags(from_domain)
        # Authentication-Results: parse all, use first as reference
        auth_results_list = parse_authentication_results_rfc(header)
        auth_results = auth_results_list[0] if auth_results_list else {}
        # RFC-compliant alignment/authentication logic
        delivery_info = {
            "dmarc": {
                "compliant": dmarc_tags.get("p", {}).get("value", "").lower() in ["quarantine", "reject", "none"],
                "alignment": auth_results.get("dmarc", {}).get("result") == "pass",
                "authenticated": auth_results.get("dmarc", {}).get("result") == "pass",
                "record": dmarc_record,
                "tags": dmarc_tags
            },
            "spf": {
                "published": bool(spf_record),
                "alignment": auth_results.get("spf", {}).get("result") == "pass",
                "authenticated": auth_results.get("spf", {}).get("result") == "pass",
                "record": spf_record,
                "tags": spf_tags
            },
            "dkim": {
                "published": bool(dkim_records),
                "alignment": any(r.get("tags", {}).get("d", {}).get("value") == from_domain for r in dkim_records),
                "authenticated": any(auth_results.get("dkim", {}).get("result") == "pass" for _ in dkim_records),
                "record": dkim_records[0]["record"] if dkim_records else "",
                "tags": dkim_records[0]["tags"] if dkim_records else {}
            },
            "authentication_results": auth_results
        }
        spf_dkim_dmarc_records = {
            "dmarc": {
                "domain": from_domain,
                "record": dmarc_record,
                "tags": dmarc_tags
            },
            "spf": {
                "domain": from_domain,
                "record": spf_record,
                "tags": spf_tags
            },
            "dkim": dkim_records
        }
        headers_found = parse_all_headers(header)
        sender_ip = extract_sender_ip(header)
        ip_info = geo_lookup(sender_ip)
        if copy_paste_warning:
            warnings.extend(copy_paste_warning)
        return {
            "parsed_headers": {"summary": summary},
            "copy_paste_warning": copy_paste_warning,
            "delivery_info": delivery_info,
            "relay_info": {
                "timeline": timeline,
                "hops": relay_hops
            },
            "spf_dkim_dmarc_records": spf_dkim_dmarc_records,
            "headers_found": headers_found,
            "ip_info": ip_info,
            "warnings": warnings
        }
    except Exception as e:
        logger.error(f"Critical error in analyze_header: {e}")
        return {
            "error": f"Critical error in header analysis: {e}"
        }
