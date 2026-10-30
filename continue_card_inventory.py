import json
import re
import time
import html
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

BASE = "https://pesdb.net/efootball/players/"
FILE = Path("pesdb_card_urls.json")
TYPES = ["highlight", "trending", "standard"]

HEADERS = {
    "User-Agent": "eFootballHubResearch/1.0 (polite public-page exporter)",
    "Accept": "text/html",
}

def get_page(url):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 60 * (attempt + 1)
                print(f"HTTP 429 — {wait} soniya kutamiz.")
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("5 urinishdan keyin sahifa ochilmadi.")

def extract_urls(source):
    pattern = (
        r'<a\b[^>]*href=["\']([^"\']*/efootball/players/'
        r'[^"\']+)["\'][^>]*>(.*?)</a>'
    )
    found = set()

    for href, label in re.findall(pattern, source, re.I | re.S):
        href = html.unescape(href)
        path = urlparse(href).path
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", label)).strip()

        if text and re.search(r"/efootball/players/[^/]+-\d+/?$", path):
            found.add(urljoin(BASE, href))

    return found

def next_page(source, current_url, card_type):
    links = re.findall(
        r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>\s*Next\s*</a>',
        source, re.I
    )

    for link in links:
        candidate = urljoin(BASE, html.unescape(link))
        query = parse_qs(urlparse(candidate).query)

        if query.get("type", [None])[0] == card_type:
            if candidate != current_url:
                return candidate

    return None

def save(data):
    temp = FILE.with_suffix(".tmp")
    temp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    temp.replace(FILE)

def main():
    if not FILE.exists():
        raise SystemExit("XATO: pesdb_card_urls.json topilmadi.")

    data = json.loads(FILE.read_text(encoding="utf-8"))

    for card_type in TYPES:
        cards = set(data.get(card_type, []))
        url = BASE + "?" + urlencode({
            "type": card_type,
            "page": 101
        })
        visited = set()
        page_count = 0

        print(f"\n=== {card_type.upper()} — 101-sahifadan ===")

        while url and url not in visited:
            visited.add(url)

            try:
                source = get_page(url)
            except Exception as e:
                print("XATO:", e)
                print("Mavjud katalog saqlangan. Keyin davom ettirish mumkin.")
                save(data)
                return

            page_count += 1
            found = extract_urls(source)

            if not found:
                print("Karta havolalari topilmadi. To‘xtatildi.")
                break

            old_count = len(cards)
            cards.update(found)
            added = len(cards) - old_count

            data[card_type] = sorted(cards)
            save(data)

            print(
                f"{card_type}: {page_count}-yangi sahifa; "
                f"+{added} URL; jami {len(cards)}"
            )

            url = next_page(source, url, card_type)

            if url:
                time.sleep(5)

        if url is None:
            print(f"{card_type.upper()}: keyingi sahifa havolasi topilmadi.")

    print("\nKatalog yangilandi:", FILE)
    print("Server bazasiga hech narsa yozilmadi.")

if __name__ == "__main__":
    main()
