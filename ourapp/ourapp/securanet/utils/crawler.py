import os
import time
import datetime
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.conf import settings


def capture_site(url, save_dir="screenshots"):
    """
    Captures a screenshot of the given URL and saves it under media/screenshots/.
    Returns the relative media URL like '/media/screenshots/example.com_timestamp.png' for frontend use.
    """

    # Ensure screenshot directory exists inside MEDIA_ROOT
    try:
        screenshot_root = os.path.join(settings.MEDIA_ROOT, save_dir)
        os.makedirs(screenshot_root, exist_ok=True)
    except Exception as e:
        print(f"[Error] Failed to create screenshot directory: {e}")
        return f"{settings.MEDIA_URL}{save_dir}/{filename}"

    # Parse domain from URL and sanitize for filename
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace(":", "_").replace("/", "_")

    # Add timestamp to prevent overwrite
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{domain}_{timestamp}.png"
    save_path = os.path.join(screenshot_root, filename)

    try:
        # Try using headless Chrome for JavaScript-rendered sites
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Initialize Chrome WebDriver with error handling
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except Exception as e:
            print(f"[Chrome Error] Failed to initialize Chrome: {e}")
            
            # Create a simple placeholder file if screenshot fails
            with open(save_path, 'w') as f:
                f.write("Placeholder for screenshot - Chrome initialization failed")
            
            return f"{settings.MEDIA_URL}{save_dir}/{filename}"

        # Capture screenshot
        driver.set_window_size(1280, 720)
        driver.get(url)
        time.sleep(2)  # Allow page to load
        driver.save_screenshot(save_path)
        print(f"[✅] Screenshot saved at: {save_path}")
        driver.quit()

        # Return relative media URL for frontend
        return f"{settings.MEDIA_URL}{save_dir}/{filename}"
    except Exception as e:
        print("[❌] Screenshot failed:", e)
        
        # Create a placeholder file if screenshot fails
        with open(save_path, 'w') as f:
            f.write(f"Placeholder for screenshot - Error: {e}")
        
        return f"{settings.MEDIA_URL}{save_dir}/{filename}"