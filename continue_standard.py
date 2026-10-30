import json
import re
import html
import time
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

FILE = Path("pesdb_card_urls.json")
BASE = "https://pesdb.net/efootball/players/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
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

def extract_cards(page):
    pattern = r'<a\b[^>]*href=["\']([^"\']+)["\']'
    found = set()

    for href in re.findall(pattern, page, re.I):
        href = html.unescape(href)
        path = urlparse(href).path
        if re.search(r"/efootball/players/[^/]+-\d+/?$", path):
            found.add(urljoin(BASE, href))
    return found

def find_next(page, current):
    links = re.findall(
        r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>\s*Next\s*</a>',
        page, re.I
    )
    for link in links:
        candidate = urljoin(BASE, html.unescape(link))
        q = parse_qs(urlparse(candidate).query)
        if q.get("type", [None])[0] == "standard" and candidate != current:
            return candidate
    return None

def save(data):
    temp = FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    temp.replace(FILE)

def main():
    if not FILE.exists():
        raise SystemExit("Katalog fayli topilmadi.")

    data = json.loads(FILE.read_text(encoding="utf-8"))
    cards = set(data.get("standard", []))
    url = BASE + "?type=standard&page=1164"
    visited = set()
    page_no = 1164

    print("Standard katalogi 1164-sahifadan davom etadi.")
    print("To‘xtatish uchun Ctrl+C bosish mumkin.")

    try:
        while url and url not in visited:
            visited.add(url)
            page = fetch(url)
            found = extract_cards(page)

            if not found:
                print(f"{page_no}-sahifada karta URL topilmadi. To‘xtadik.")
                break

            before = len(cards)
            cards.update(found)
            added = len(cards) - before

            data["standard"] = sorted(cards)
            save(data)

            print(
                f"{page_no}-sahifa: {len(found)} URL; "
                f"+{added} yangi; jami {len(cards)}"
            )

            next_url = find_next(page, url)
            if not next_url:
                print("Keyingi sahifa havolasi topilmadi.")
                break

            url = next_url
            page_no += 1
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nTo‘xtatildi. Oxirgi katalog saqlangan.")
    except Exception as e:
        print("\nUlanish yoki sahifa xatosi:", e)
        print("Oxirgi katalog saqlangan.")

    print("\nStandard URL jami:", len(data.get("standard", [])))
    print("Render bazasiga hech narsa yozilmadi.")

if __name__ == "__main__":
    main()
