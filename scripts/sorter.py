import os
import time
import requests
import threading
from queue import Queue
from urllib.parse import urlparse

# ======================== CONFIG ========================
BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
DELAY_START = 0.10
MIN_DELAY = 0.01
DELAY_STEP = 0.005
MAX_ROUNDS = 5
HTML_DIR = "./html"
THREAD_COUNT = 2  # Starts at 1 as per request
DEBUG = True
# ========================================================

def debug_log(msg):
    if DEBUG:
        print(msg, flush=True)

def collect_links():
    all_links = set()
    for root, dirs, files in os.walk(BASE_PATH):
        for file in files:
            if file.endswith("_links.txt"):
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8") as f:
                    links = [line.strip() for line in f if line.strip()]
                    all_links.update(links)
    return list(all_links)

def get_filename_from_url(url):
    path = urlparse(url).path
    return os.path.basename(path) + ".html"

def fetch_worker(q, results, delay):
    debug_log("🧵 Worker started.")
    while True:
        try:
            url = q.get_nowait()
        except:
            break  # Queue empty

        try:
            debug_log(f"🌐 Fetching: {url} (delay={delay:.3f}s)")
            debug_log("⏳ Sleeping...")
            time.sleep(delay)
            debug_log("🛌 Done sleeping")

            response = requests.get(url, timeout=10)
            status_code = response.status_code

            debug_log(f"✅ [{status_code}] {url}")

            results.append({
                'url': url,
                'status_code': status_code,
                'content': response.text if status_code == 200 else None,
                'error': None if status_code == 200 else f"HTTP {status_code}"
            })

        except requests.exceptions.Timeout:
            debug_log(f"⏱️ Timeout while fetching {url}")
            results.append({
                'url': url,
                'status_code': None,
                'content': None,
                'error': "Timeout"
            })

        except Exception as e:
            debug_log(f"💥 Error fetching {url}: {e}")
            results.append({
                'url': url,
                'status_code': None,
                'content': None,
                'error': str(e)
            })

        finally:
            q.task_done()

def run_round(links, delay, thread_count):
    q = Queue()
    results = []

    for url in links:
        q.put(url)

    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=fetch_worker, args=(q, results, delay))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return results

def save_successes(results):
    os.makedirs(HTML_DIR, exist_ok=True)
    for r in results:
        if r['status_code'] == 200:
            filename = get_filename_from_url(r['url'])
            with open(os.path.join(HTML_DIR, filename), "w", encoding="utf-8") as f:
                f.write(r['content'])

def adaptive_fetcher():
    print("🧠 Adaptive Shinseina HTML Fetcher Initialized")

    links = collect_links()
    total_links = len(links)
    print(f"🌐 Total unique URLs: {total_links}")

    if total_links == 0:
        print("❌ No links found.")
        return

    delay = DELAY_START
    round_num = 1
    remaining = links.copy()

    while remaining and round_num <= MAX_ROUNDS:
        print(f"\n🌀 Round {round_num}: {len(remaining)} URLs | Delay: {delay:.3f}s | Concurrency: {THREAD_COUNT}")
        results = run_round(remaining, delay, THREAD_COUNT)

        successes = [r for r in results if r['status_code'] == 200]
        failures = [r for r in results if r['status_code'] != 200]

        save_successes(successes)

        if len([r for r in failures if r['status_code'] == 429]) > 25:
            delay += DELAY_STEP
            print(f"⚠️  Too many 429s, increasing delay to {delay:.3f}s")
        else:
            delay = max(MIN_DELAY, delay - DELAY_STEP)

        remaining = [r['url'] for r in failures if r['status_code'] == 429]
        round_num += 1

    print("\n🎉 All links processed!")

if __name__ == "__main__":
    adaptive_fetcher()
