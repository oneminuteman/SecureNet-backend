from ..header_tools.risk_scoring import score_risk

def score_risk_wrapper(parsed_header, dns_checks):
    """
    Score risk using the existing risk scoring function.
    
    Args:
        parsed_header (dict): Parsed header information from analyze_header
        dns_checks (dict): DNS check results (not used, DNS info is in parsed_header)
        
    Returns:
        dict: Risk score and reasons
    """
    try:
        # Extract the data in the format expected by score_risk
        parsed_headers = parsed_header.get("parsed_headers", {})
        ip_info = parsed_header.get("ip_info", {})
        
        # Extract DNS information from the parsed header structure
        spf_dkim_dmarc_records = parsed_header.get("spf_dkim_dmarc_records", {})
        delivery_info = parsed_header.get("delivery_info", {})
        
        # Convert to the format expected by score_risk
        dns_checks = {
            "spf": {
                "has_spf": delivery_info.get("spf", {}).get("published", False),
                "spf_record": spf_dkim_dmarc_records.get("spf", {}).get("record", "")
            },
            "dkim": {
                "has_dkim": delivery_info.get("dkim", {}).get("published", False),
                "dkim_record": spf_dkim_dmarc_records.get("dkim", [{}])[0].get("record", "") if spf_dkim_dmarc_records.get("dkim") else ""
            },
            "dmarc": {
                "has_dmarc": delivery_info.get("dmarc", {}).get("compliant", False),
                "dmarc_record": spf_dkim_dmarc_records.get("dmarc", {}).get("record", "")
            }
        }
        
        return score_risk(parsed_headers, dns_checks, ip_info)
    except Exception as e:
        return {
            "risk_score": 10,  # High risk if scoring fails
            "level": "High Risk 🚨",
            "reasons": [f"Risk scoring failed: {str(e)}"]
        } 