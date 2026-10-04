"""Shared Firefox screenshot support for browser based downloaders."""

import io
import logging
import time

from PIL import Image


def capture_page(url, wait_seconds=7, page_load_timeout=30, wait_for_video=False):
    """Return a page screenshot as an RGB PIL image, or None on failure."""
    try:
        # Import on use so still-image chains do not require Selenium at startup.
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait

        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        options.page_load_strategy = 'eager'
        options.set_preference('media.autoplay.default', 0)
        options.set_preference('media.volume_scale', '0.0')
        options.set_preference('dom.webnotifications.enabled', False)

        with webdriver.Firefox(options=options) as driver:
            driver.set_window_size(1920, 1080)
            driver.set_page_load_timeout(page_load_timeout)
            driver.get(url)
            if wait_for_video:
                WebDriverWait(driver, wait_seconds).until(
                    lambda browser: browser.execute_script(
                        "return !!document.querySelector('video') && "
                        "document.querySelector('video').readyState >= 2"
                    )
                )
            else:
                time.sleep(wait_seconds)
            with Image.open(io.BytesIO(driver.get_screenshot_as_png())) as screenshot:
                return screenshot.convert('RGB')
    except Exception:
        logging.exception('Browser screenshot failed')
        return None
