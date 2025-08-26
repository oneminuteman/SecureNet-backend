from ..header_tools.header_parser import analyze_header

def parse_email_header(raw_header):
    """
    Parse email header using the existing header parser.
    
    Args:
        raw_header (str): Raw email header text
        
    Returns:
        dict: Parsed header information
    """
    try:
        return analyze_header(raw_header)
    except Exception as e:
        return {
            "error": f"Failed to parse header: {str(e)}",
            "parsed_headers": {},
            "dns_checks": {},
            "ip_info": {}
        } 