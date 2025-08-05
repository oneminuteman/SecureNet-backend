import difflib
import requests
from bs4 import BeautifulSoup
from django.utils.html import strip_spaces_between_tags
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_html_signature(url):
    """
    Attempts to fetch HTML using Selenium (JS-rendered pages), falls back to requests+BeautifulSoup.
    Cleans and normalizes HTML for comparison by removing scripts/styles and whitespace.
    Uses html5lib parser instead of lxml for better Windows compatibility.
    """
    try:
        # Try using headless Chrome for JavaScript-rendered sites
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        html = driver.page_source
        driver.quit()

        # Use html5lib parser instead of lxml
        soup = BeautifulSoup(html, 'html5lib')

    except Exception as selenium_error:
        print(f"[Selenium Fallback] {selenium_error}")
        try:
            # Fallback: Use requests for basic HTML
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/114.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            # Use html5lib parser instead of lxml
            soup = BeautifulSoup(response.text, 'html5lib')
        except Exception as requests_error:
            print(f"[HTML Error] Could not get HTML for {url}: {requests_error}")
            return ""

    # Clean HTML: Remove script/style and prettify
    for tag in soup(['script', 'style']):
        tag.decompose()

    html_pretty = soup.prettify()
    html_clean = strip_spaces_between_tags(html_pretty)

    return html_clean


def html_similarity(html1, html2):
    """
    Returns a similarity score (0.0 to 1.0) between two HTML signatures.
    Uses difflib.SequenceMatcher for structural comparison.
    """
    if not html1 or not html2:
        return 0.0

    return difflib.SequenceMatcher(None, html1, html2).ratio()