
import difflib
import requests
from bs4 import BeautifulSoup
from django.utils.html import strip_spaces_between_tags


def get_html_signature(url):
    """
    Fetches and normalizes the HTML structure of a website.
    Removes scripts and styles, and formats the structure consistently.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style tags to avoid noise
        for tag in soup(['script', 'style']):
            tag.decompose()

        # Use prettify for consistent formatting
        html_pretty = soup.prettify()

        # Normalize HTML by stripping excess whitespace
        html_clean = strip_spaces_between_tags(html_pretty)

        return html_clean

    except Exception as e:
        print(f"[Error] Could not get HTML for {url}: {e}")
        return ""


def html_similarity(html1, html2):
    """
    Returns a similarity score (0.0 to 1.0) between two HTML signatures.
    Uses difflib's SequenceMatcher for structure-based comparison.
    """
    if not html1 or not html2:
        return 0.0

    return difflib.SequenceMatcher(None, html1, html2).ratio()
