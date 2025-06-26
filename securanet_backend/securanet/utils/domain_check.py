
import whois
from datetime import datetime

def get_domain_reputation(url):
    try:
        domain = url.split("//")[-1].split("/")[0]
        info = whois.whois(domain)

        created = info.creation_date
        if isinstance(created, list):
            created = created[0]
        if not created:
            return "Unknown"

        age = (datetime.now() - created).days
        return f"{domain} - Age: {age} days"
    except Exception as e:
        print("WHOIS error:", e)
        return "Unavailable"
