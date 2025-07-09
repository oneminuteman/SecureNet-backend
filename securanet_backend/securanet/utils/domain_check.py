import whois  # ✅ correct usage
from urllib.parse import urlparse
from datetime import datetime

def get_domain_reputation(url):
    try:
        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Perform WHOIS lookup
        info = whois(domain)

        # Extract creation date
        created = info.creation_date
        if isinstance(created, list):
            created = created[0]

        if not created:
            return "Domain age unknown"

        # Calculate domain age
        age_days = (datetime.now() - created).days

        # Simple rules
        if age_days < 60:
            return f"{domain} - 🚨 New Domain (Age: {age_days} days)"
        elif age_days < 365:
            return f"{domain} - ⚠️ Fairly New (Age: {age_days} days)"
        else:
            return f"{domain} - ✅ Established (Age: {age_days} days)"
    
    except Exception as e:
        print("WHOIS error:", e)
        return "WHOIS lookup failed"

