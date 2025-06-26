
import os
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from django.conf import settings


def capture_site(url, save_dir="screenshots"):
    """
    Captures a screenshot of the given URL and saves it under media/screenshots/.
    Returns the relative path to the screenshot for media serving.
    """
    # Ensure screenshot directory exists inside MEDIA_ROOT
    screenshot_root = os.path.join(settings.MEDIA_ROOT, save_dir)
    os.makedirs(screenshot_root, exist_ok=True)

    # Clean domain for filename
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace(":", "_")
    filename = f"{domain}.png"
    save_path = os.path.join(screenshot_root, filename)

    # Set up headless Chrome browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    try:
        driver.set_window_size(1280, 720)
        driver.get(url)
        time.sleep(2)  # Allow time for page to load
        driver.save_screenshot(save_path)
        print(f"[✅] Screenshot saved at: {save_path}")

        return os.path.join(save_dir, filename)  # Relative path: screenshots/filename.png
    except Exception as e:
        print("[❌] Screenshot failed:", e)
        return None
    finally:
        driver.quit()
