def run_dns_checks(parsed_header):
    """
    Extract DNS check results from parsed header.
    
    Args:
        parsed_header (dict): Parsed header information
        
    Returns:
        dict: DNS check results
    """
    try:
        return parsed_header.get("dns_checks", {})
    except Exception as e:
        return {
            "error": f"Failed to extract DNS checks: {str(e)}",
            "spf": {"error": "DNS check failed"},
            "dkim": {"error": "DNS check failed"},
            "dmarc": {"error": "DNS check failed"}
        } 