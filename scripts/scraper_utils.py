import math
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def chunk_links(links, preferred_chunks=50, fallback_max=75):
    total = len(links)
    if total <= fallback_max:
        return [links]  # No need to split

    # Try to split into preferred_chunks (50)
    per_chunk = math.ceil(total / preferred_chunks)
    if per_chunk <= fallback_max:
        chunks = [links[i:i + per_chunk] for i in range(0, total, per_chunk)]
    else:
        # fallback: just use 75 max per chunk
        chunks = [links[i:i + fallback_max] for i in range(0, total, fallback_max)]

    print(f"🔀 Split {total} links into {len(chunks)} chunks ({len(chunks[0])} in first chunk)")
    return chunks


def get_selenium_driver():
    chrome_options = Options()
    chrome_options.headless = True

    # 🚫 Block extra resources for speed
    chrome_prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2,
        "profile.managed_default_content_settings.cookies": 2,
        "profile.managed_default_content_settings.popups": 2
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--log-level=3")

    service = Service()  # Uses system ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(20)
    return driver


def scroll_to_bottom(driver, delay=1):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(delay)  # Give lazy-loaded tags a second to show up


def extract_tags_from_page(driver, timeout=10):
    try:
        # Wait for ANY anchor tag with the right class and path
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/world-book/tags/')]"))
        )

        tag_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/world-book/tags/')]")
        return [tag.get_attribute("href") for tag in tag_elements]

    except Exception as e:
        print(f"    💥 Tag extract error: {e}")
        return []