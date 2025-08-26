import re

def score_risk(parsed_headers, dns_checks, ip_info):
    score = 0
    reasons = []

    # 1. Missing From email
    from_email = parsed_headers.get("summary", {}).get("from", {}).get("email", "")
    if not from_email or '@' not in from_email:
        score += 2
        reasons.append("Missing or invalid 'From' address.")

    # 2. SPF
    spf = dns_checks.get("spf", {})
    if not spf.get("has_spf"):
        score += 2
        reasons.append("No SPF record found.")
    elif spf.get("spf_record", "").strip().endswith("-all"):
        score += 3
        reasons.append("SPF policy is strict '-all'.")

    # 3. DKIM
    dkim = dns_checks.get("dkim", {})
    if not dkim.get("has_dkim"):
        score += 2
        reasons.append("No DKIM record found.")

    # 4. DMARC
    dmarc = dns_checks.get("dmarc", {})
    if not dmarc.get("has_dmarc"):
        score += 2
        reasons.append("No DMARC policy found.")

    # 5. IP geolocation unknown
    if not ip_info or ip_info.get("country") in (None, "Unknown", ""):
        score += 1
        reasons.append("Sender IP location unknown or invalid.")

    # 6. Suspicious keywords in subject or headers
    subject = parsed_headers.get("summary", {}).get("subject", "")
    suspicious_keywords = [
        "urgent", "suspended", "verify", "update", "password", "account", "login", "click", "confirm", "security", "alert", "reset", "invoice", "payment", "bank", "limited", "immediately", "action required"
    ]
    if any(word in subject.lower() for word in suspicious_keywords):
        score += 2
        reasons.append("Suspicious keyword(s) found in subject.")

    # 7. Sender/Return-Path mismatch (if available)
    return_path = parsed_headers.get("return_path", "")
    if return_path and from_email and return_path.lower() != from_email.lower():
        score += 2
        reasons.append("Return-Path and From address mismatch.")

    # 8. Routing anomalies (e.g., private IPs, too many hops)
    routing = parsed_headers.get("routing", [])
    private_ip_pattern = re.compile(r"^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)")
    private_hops = [hop for hop in routing if hop.get("from_ip") and private_ip_pattern.match(hop["from_ip"])]
    if private_hops:
        score += 1
        reasons.append("Private IP(s) found in routing chain.")
    if len(routing) > 5:
        score += 1
        reasons.append("Unusually long routing chain (possible relay obfuscation).")

    # 9. Placeholder for threat intelligence (future integration)
    # Example: if is_blacklisted_ip(ip_info.get("ip")): ...
    # score += 3
    # reasons.append("Sender IP/domain is blacklisted.")

    # Risk level
    if score <= 2:
        level = "Low Risk ✅"
    elif score <= 5:
        level = "Medium Risk ⚠️"
    else:
        level = "High Risk 🚨"

    return {
        "risk_score": score,
        "level": level,
        "reasons": reasons
    } 