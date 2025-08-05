import os
from urllib.parse import urlparse
from django.conf import settings

from .crawler import capture_site
from .compare import get_html_signature, html_similarity
from .domain_check import (
    get_domain_reputation,
    check_google_safe_browsing,
    check_domain_age_fallback,
)
from .virustotal import check_virustotal
from securanet.models import KnownSite, ScanLog


def detect_clone(candidate_url):
    """
    Detects if a candidate website is malicious or a clone using:
    ✅ 1. Domain reputation (WhoisXML or fallback)
    ✅ 2. Google Safe Browsing
    ✅ 3. VirusTotal
    ✅ 4. Screenshot capture
    ✅ 5. HTML similarity to known sites
    """

    # Extract domain
    parsed = urlparse(candidate_url)
    domain = parsed.netloc

    result = {
        "status": "safe",
        "screenshot": None,
        "reason": "",
        "method": "",
    }

    # ✅ STEP 1: Domain reputation (WhoisXML first)
    if settings.WHOISXML_API_KEY:
        reputation = get_domain_reputation(domain)
        if reputation == "unknown":
            reputation = check_domain_age_fallback(candidate_url)
    else:
        # Skip WhoisXML and use fallback directly
        reputation = check_domain_age_fallback(candidate_url)
        
    result["reputation"] = reputation

    if reputation == "malicious":
        result.update({
            "status": "flagged",
            "reason": "Bad domain reputation",
            "method": "domain",
            "screenshot": get_clean_screenshot_path(candidate_url)
        })
        return result

    # ✅ STEP 2: Google Safe Browsing
    gsb_result = check_google_safe_browsing(candidate_url)
    result["google_safebrowsing"] = gsb_result
    if gsb_result["status"] == "flagged":
        result.update({
            "status": "flagged",
            "reason": "Google Safe Browsing flagged the site",
            "method": "google_safebrowsing",
            "screenshot": get_clean_screenshot_path(candidate_url)
        })
        return result

    # ✅ STEP 3: VirusTotal
    vt_result = check_virustotal(candidate_url)
    result["virustotal"] = vt_result
    if vt_result["status"] == "flagged":
        result.update({
            "status": "flagged",
            "reason": "VirusTotal flagged the site",
            "method": "virustotal",
            "screenshot": get_clean_screenshot_path(candidate_url)
        })
        return result

    # ✅ STEP 4: Screenshot capture
    result["screenshot"] = get_clean_screenshot_path(candidate_url)

    # ✅ STEP 5: HTML Signature Extraction
    candidate_signature = get_html_signature(candidate_url)
    if not candidate_signature:
        result.update({
            "status": "error",
            "reason": "Could not retrieve HTML from candidate site"
        })
        return result

    # ✅ STEP 6: Compare with KnownSite signatures
    for legit in KnownSite.objects.all():
        if not legit.html_signature:
            continue

        score = html_similarity(candidate_signature, legit.html_signature)
        if score > 0.85:
            result.update({
                "status": "flagged",
                "reason": f"HTML similarity to {legit.domain} ({round(score * 100, 2)}%)",
                "method": "html"
            })
            return result

    # ✅ STEP 7: All clear
    result["message"] = "No significant similarity detected."
    return result


def get_clean_screenshot_path(url):
    screenshot_path = capture_site(url, save_dir="screenshots")
    if screenshot_path:
        return f"screenshots/{os.path.basename(screenshot_path)}"
    return None