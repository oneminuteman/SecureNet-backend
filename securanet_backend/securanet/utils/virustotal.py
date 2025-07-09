# securanet/utils/virustotal.py

import os
import base64
import requests

# Get VirusTotal API key from environment variables
VT_API_KEY = os.getenv("VT_API_KEY")

def check_virustotal(url):
    if not VT_API_KEY:
        return {"status": "unknown", "message": "No VirusTotal API key set"}

    headers = {
        "x-apikey": VT_API_KEY,
    }

    # Base64-encode the URL for lookup
    try:
        url_bytes = url.encode("utf-8")
        b64_url = base64.urlsafe_b64encode(url_bytes).decode().rstrip("=")

        # Try GET lookup first (works for free API tier)
        lookup_url = f"https://www.virustotal.com/api/v3/urls/{b64_url}"
        lookup_resp = requests.get(lookup_url, headers=headers)

        if lookup_resp.status_code == 200:
            data = lookup_resp.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)

            if malicious > 0:
                return {"status": "flagged", "message": f"Detected {malicious} malicious report(s)"}
            else:
                return {"status": "clean", "message": "No malicious reports found"}
        else:
            print("[VT Notice] GET lookup failed. Trying POST submission...")

        # Fallback: try POST if GET lookup fails and API allows
        scan_endpoint = "https://www.virustotal.com/api/v3/urls"
        submit_resp = requests.post(scan_endpoint, headers=headers, data={"url": url})
        submit_resp.raise_for_status()
        scan_id = submit_resp.json()["data"]["id"]

        # Fetch analysis results using scan_id
        result_url = f"{scan_endpoint}/{scan_id}"
        result_resp = requests.get(result_url, headers=headers)
        result_resp.raise_for_status()
        analysis = result_resp.json()

        stats = analysis.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        malicious_count = stats.get("malicious", 0)

        if malicious_count > 0:
            return {
                "status": "flagged",
                "message": f"{malicious_count} engines flagged this URL"
            }
        else:
            return {
                "status": "clean",
                "message": "No engines flagged this URL"
            }

    except Exception as e:
        print("[VirusTotal Error]", e)
        return {"status": "error", "message": str(e)}
