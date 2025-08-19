import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import os
import time

BASE_URL = "https://fomin-clinic.ru/"
OUTPUT_DIR = "site_html"
VISITED_FILE = "visited.txt"

visited = set()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    )
}

def save_page(url, html):
    parsed = urlparse(url)
    path = parsed.path

    if not path or path.endswith("/"):
        path = path + "index.html"
    elif "." not in os.path.basename(path):
        path = path.rstrip("/") + "/index.html"

    local_path = os.path.join(OUTPUT_DIR, path.lstrip("/"))
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with open(local_path, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)

    print(f"Сохранено: {local_path}")


def log_visited(url):
    with open(VISITED_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def crawl(url, domain=BASE_URL):
    if url in visited:
        return
    visited.add(url)
    time.sleep(1) 
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return

    if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type", ""):
        return

    save_page(url, r.text)
    log_visited(url)

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        href, _ = urldefrag(href)
        if href.startswith(domain) and href not in visited:
            crawl(href, domain)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    open(VISITED_FILE, "w", encoding="utf-8").close()
    crawl(BASE_URL)
    print("Готово")
