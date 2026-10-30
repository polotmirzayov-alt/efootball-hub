import json
import re
import time
import html
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

BASE = "https://pesdb.net/efootball/players/"
HEADERS = {
    "User-Agent": "eFootballHubResearch/1.0 (polite public-page exporter)",
    "Accept": "text/html",
}

TYPES = [
    "epic",
    "big_time",
    "show_time",
    "highlight",
    "trending",
    "legendary",
    "standard",
]

def get_page(url):
    for attempt in range(5):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=25) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read().decode("utf-8", "replace")

        except urllib.error.HTTPError as error:
            if error.code == 429:
                wait = min(60 * (attempt + 1), 300)
                print(f"HTTP 429. {wait} soniya kutamiz.")
                time.sleep(wait)
                continue
            raise

    raise RuntimeError("5 urinishdan keyin ham sahifa ochilmadi.")

def extract_urls(source):
    pattern = (
        r'<a\b[^>]*href=["\']([^"\']*/efootball/players/'
        r'[^"\']+)["\'][^>]*>(.*?)</a>'
    )
    result = set()

    for href, label in re.findall(pattern, source, re.I | re.S):
        href = html.unescape(href)
        path = urlparse(href).path

        if re.search(r"/efootball/players/[^/]+-\d+/?$", path):
            if re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", label)).strip():
                result.add(urljoin(BASE, href))

    return result

def next_page(source, current_url, card_type):
    links = re.findall(
        r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>\s*Next\s*</a>',
        source,
        re.I,
    )

    for link in links:
        candidate = urljoin(BASE, html.unescape(link))
        query = parse_qs(urlparse(candidate).query)

        if query.get("type", [None])[0] == card_type:
            if candidate != current_url:
                return candidate

    return None

def main():
    inventory = {}

    for card_type in TYPES:
        print(f"\n=== {card_type.upper()} ===")
        url = BASE + "?" + urlencode({"type": card_type})
        visited = set()
        cards = set()
        page_count = 0

        while url and url not in visited and page_count < 100:
            visited.add(url)

            try:
                source = get_page(url)
            except Exception as error:
                print("To‘xtadi:", error)
                break

            page_count += 1
            found = extract_urls(source)
            cards.update(found)

            print(
                f"{card_type}: {page_count}-sahifa, "
                f"{len(found)} ta havola, jami {len(cards)} ta"
            )

            url = next_page(source, url, card_type)

            inventory[card_type] = sorted(cards)

            with open(
                "pesdb_card_urls.json", "w", encoding="utf-8"
            ) as file:
                json.dump(inventory, file, ensure_ascii=False, indent=2)

            if url:
                time.sleep(5)

        print(f"{card_type} yakuniy hisob: {len(cards)} ta havola")

    print("\nKatalog fayli: pesdb_card_urls.json")
    print("Server bazasiga hech narsa yozilmadi.")

if __name__ == "__main__":
    main()
