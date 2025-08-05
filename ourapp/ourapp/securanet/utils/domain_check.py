import requests
import whois  # python-whois
from urllib.parse import urlparse
from datetime import datetime
from django.conf import settings

# === WHOISXML Domain Reputation API =======================================

def get_domain_reputation(domain):
    """
    Uses WhoisXML Domain Reputation API to evaluate a domain.
    Returns: 'malicious', 'suspicious', 'safe', or 'unknown'
    """
    try:
        url = "https://reputation.whoisxmlapi.com/api/v1"
        params = {
            "apiKey": settings.WHOISXML_API_KEY,
            "domainName": domain,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        print("[WhoisXML] Domain reputation result:", data)

        score = data.get("reputationScore", 100)
        if score < 30:
            return "malicious"
        elif score < 70:
            return "suspicious"
        return "safe"

    except Exception as e:
        print(f"[WhoisXML Error] {e}")
        return "unknown"

# === Google Safe Browsing API Integration =================================

def check_google_safe_browsing(url):
    """
    Checks a URL using the Google Safe Browsing API.
    Returns a dictionary with status and additional info.
    """
    endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    payload = {
        "client": {
            "clientId": "securanet-ai",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(
            f"{endpoint}?key={settings.GOOGLE_SAFE_BROWSING_API_KEY}",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        matches = response.json().get("matches")

        if matches:
            return {
                "status": "flagged",
                "reason": "Google Safe Browsing flagged this URL",
                "matches": matches
            }

        return {"status": "safe", "message": "No threats found"}

    except Exception as e:
        print("[Google Safe Browsing Error]", e)
        return {"status": "error", "message": str(e)}

# === WHOIS Fallback: Domain Age-Based Reputation ==========================

def check_domain_age_fallback(url):
    """
    Fallback method using python-whois if WhoisXML fails.
    Returns 'malicious', 'suspicious', or 'safe' based on domain age.
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        info = whois.whois(domain)
        created = info.creation_date
        if isinstance(created, list):
            created = created[0]

        if not created:
            return "unknown"

        age_days = (datetime.now() - created).days

        if age_days < 60:
            return "malicious"
        elif age_days < 365:
            return "suspicious"
        else:
            return "safe"

    except Exception as e:
        print("[WHOIS fallback error]", e)
        return "unknown"