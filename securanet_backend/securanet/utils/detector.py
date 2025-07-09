# securanet/utils/detector.py

import os
from django.conf import settings

from .crawler import capture_site
from .compare import get_html_signature, html_similarity
from .domain_check import get_domain_reputation
from .virustotal import check_virustotal  # ✅ VirusTotal check
from securanet.models import KnownSite


def detect_clone(candidate_url):
    """
    Detects if a candidate website is a clone of a known legitimate one.
    Applies detection using:
    ✅ 1. Domain reputation
    ✅ 2. VirusTotal scan
    ✅ 3. HTML structure similarity
    ✅ 4. Screenshot capture
    """

    result = {
        "status": "safe",
        "screenshot": None,
        "reason": "",
        "method": "",
        "reputation": get_domain_reputation(candidate_url),
    }

    # ✅ STEP 1: Domain reputation check
    if result["reputation"] == "malicious":
        result.update({
            "status": "flagged",
            "reason": "Bad domain reputation",
            "method": "domain",
        })
        screenshot_path = capture_site(candidate_url, save_dir="screenshots")
        if screenshot_path:
            result["screenshot"] = screenshot_path
        return result

    # ✅ STEP 2: VirusTotal scan
    vt_result = check_virustotal(candidate_url)
    result["virustotal"] = vt_result
    if vt_result["status"] == "flagged":
        result.update({
            "status": "flagged",
            "reason": "VirusTotal flagged the site",
            "method": "virustotal",
        })
        screenshot_path = capture_site(candidate_url, save_dir="screenshots")
        if screenshot_path:
            result["screenshot"] = screenshot_path
        return result

    # ✅ STEP 3: Screenshot capture
    screenshot_path = capture_site(candidate_url, save_dir="screenshots")
    if screenshot_path:
        result["screenshot"] = screenshot_path

    # ✅ STEP 4: HTML Signature Extraction
    candidate_signature = get_html_signature(candidate_url)
    if not candidate_signature:
        result.update({
            "status": "error",
            "reason": "Could not retrieve HTML from candidate site",
        })
        return result

    # ✅ STEP 5: Compare against known legitimate sites
    for legit in KnownSite.objects.all():
        score = html_similarity(candidate_signature, legit.html_signature or "")
        if score > 0.85:
            result.update({
                "status": "flagged",
                "reason": f"HTML similarity to {legit.domain} ({round(score * 100, 2)}%)",
                "method": "html"
            })
            return result

    # ✅ STEP 6: All clear
    result["message"] = "No significant similarity detected."
    return result
