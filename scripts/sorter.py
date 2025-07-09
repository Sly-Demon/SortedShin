import asyncio
import aiohttp
from pathlib import Path
import re
import time
import random
from urllib.parse import urlparse

# ------------ CONFIG ------------ #
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"
HTML_DIR = DATA_DIR / "html_pages"
HTML_DIR.mkdir(parents=True, exist_ok=True)

VALID_THINGS = ["flora", "fauna", "minerals"]


# -------------------------------- #


def get_all_links():
    all_urls = []
    for thing in VALID_THINGS:
        base_path = DATA_DIR / thing
        if not base_path.exists():
            continue

        for folder in base_path.iterdir():
            if not folder.is_dir():
                continue

            link_file = folder / "_links.txt"
            if link_file.exists():
                try:
                    lines = link_file.read_text(encoding="utf-8").splitlines()
                    urls = [line.strip() for line in lines if line.strip()]
                    all_urls.extend(urls)
                except Exception as e:
                    print(f"⚠️ Error reading {link_file}: {e}")
    return all_urls


def normalize_filename(url):
    parsed = urlparse(url)
    name = Path(parsed.path).stem
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name.lower())
    return name + ".html"


async def fetch_and_save(session, url, semaphore):
    async with semaphore:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    filename = normalize_filename(url)
                    with open(HTML_DIR / filename, "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"✅ {filename}")
                else:
                    print(f"❌ Failed ({resp.status}) → {url}")
        except Exception as e:
            print(f"💥 Error fetching {url}: {e}")


async def download_all(urls, concurrency=3):
    print(f"🌐 Starting scrape for {len(urls)} URLs...")
    semaphore = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_save(session, url, semaphore) for url in urls]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    urls = get_all_links()

    if not urls:
        print("🚫 No URLs found in any _links.txt files!")
    else:
        asyncio.run(download_all(urls, concurrency=3))
        print(f"🎉 Done! HTML saved to: {HTML_DIR}")
