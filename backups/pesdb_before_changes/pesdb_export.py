import argparse
import html
import json
import re
import time
import urllib.request
from urllib.parse import urljoin, urlparse, parse_qs

BASE = "https://pesdb.net"
LIST_URL = BASE + "/efootball/players/"
HEADERS = {
    "User-Agent": "eFootballHubResearch/1.0 (polite public-page exporter)",
    "Accept": "text/html",
}

def get_html(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=25) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {url}")
        return response.read().decode("utf-8", "replace")

def clean(value):
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()

def first(pattern, text, default=""):
    match = re.search(pattern, text, re.I | re.S)
    return clean(match.group(1)) if match else default

def extract_cards(page):
    found = []
    pattern = (
        r'<a\b[^>]*href=["\']([^"\']*/efootball/players/'
        r'[^"\']+)["\'][^>]*>(.*?)</a>'
    )
    for href, label in re.findall(pattern, page, re.I | re.S):
        href = html.unescape(href)
        path = urlparse(href).path
        if path.rstrip("/") == "/efootball/players":
            continue
        if not re.search(r"/efootball/players/[^/]+-\d+/?$", path):
            continue
        if not clean(label):
            continue
        url = urljoin(BASE, href)
        if url not in found:
            found.append(url)
    return found

def parse_player(url):
    page = get_html(url)

    title = first(r"<title[^>]*>(.*?)</title>", page)
    name = first(r'<h1[^>]*id=["\']player-name["\'][^>]*>(.*?)</h1>', page)
    if not name:
        name = title.split(" - ")[0].strip()

    description = first(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        page
    )
    # Description values provide an additional check for OVR fields.
    ovr_match = re.search(r"Overall Rating\s+(\d+)", description, re.I)
    max_match = re.search(r"Max Overall\s+(\d+)", description, re.I)

    stats = {
        key: int(value)
        for key, value in re.findall(
            r'data-stat-value=["\']([^"\']+)["\'][^>]*>\s*(\d+)',
            page, re.I
        )
    }

    position = first(
        r'<span[^>]*class=["\'][^"\']*player-hero-position[^"\']*["\'][^>]*>'
        r'.*?<a[^>]*>(.*?)</a>',
        page
    )
    card_type = first(
        r'<p[^>]*class=["\'][^"\']*player-hero-card-type[^"\']*["\'][^>]*>'
        r'.*?<a[^>]*>(.*?)</a>',
        page
    )

    styles = re.findall(
        r'<span>\s*Attacking Playing Style\s*</span>\s*'
        r'<strong>(.*?)</strong>',
        page, re.I | re.S
    )
    playing_style = clean(styles[0]) if styles else ""

    club_row = first(
        r'<div class=["\']player-club-row["\']>(.*?)</div>',
        page
    )
    linked_names = [
        clean(x) for x in re.findall(
            r'<a\b[^>]*>(.*?)</a>', club_row, re.I | re.S
        )
    ]

    image_path = first(
        r'<img[^>]*data-player-card-image[^>]*src=["\']([^"\']+)["\']',
        page
    )
    image = urljoin(BASE, html.unescape(image_path)) if image_path else ""

    card_id_match = re.search(r"-(\d+)/?$", urlparse(url).path)
    card_id = card_id_match.group(1) if card_id_match else ""

    return {
        "player_name": name,
        "card_name": title.split(" | ")[0] if title else name,
        "card_type": card_type or "Unknown",
        "rating": int(ovr_match.group(1)) if ovr_match else None,
        "max_rating": int(max_match.group(1)) if max_match else None,
        "position": position,
        "playing_style": playing_style,
        "nationality": linked_names[0] if linked_names else "",
        "club": linked_names[1] if len(linked_names) > 1 else "",
        "image": image,
        "release_date": "",
        "source": "PESDB",
        "source_url": url,
        "source_card_id": card_id,
        "stats": stats,
    }

def main():
    parser = argparse.ArgumentParser(
        description="PESDB kartalarini JSON fayliga eksport qilish"
    )
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--output", default="pesdb_cards.json")
    parser.add_argument("--delay", type=float, default=1.5)
    args = parser.parse_args()

    if not 1 <= args.pages <= 100:
        parser.error("--pages 1–100 oralig'ida bo'lishi kerak")
    if not 1 <= args.delay <= 60:
        parser.error("--delay 1–60 soniya oralig'ida bo'lishi kerak")

    urls = []
    for page_num in range(1, args.pages + 1):
        list_url = LIST_URL if page_num == 1 else f"{LIST_URL}?page={page_num}"
        print(f"Ro'yxat sahifasi: {page_num}/{args.pages}")
        page_html = get_html(list_url)
        page_urls = extract_cards(page_html)
        print(f"Topilgan karta sahifalari: {len(page_urls)}")
        urls.extend(page_urls)
        if page_num < args.pages:
            time.sleep(args.delay)

    urls = list(dict.fromkeys(urls))
    records = []

    for index, url in enumerate(urls, 1):
        try:
            card = parse_player(url)
            if card["player_name"] and card["rating"] is not None:
                records.append(card)
                print(
                    f"[{index}/{len(urls)}] {card['player_name']} — "
                    f"{card['card_type']} — {card['rating']} OVR"
                )
            else:
                print(f"[{index}/{len(urls)}] Tekshirish kerak: {url}")
        except Exception as error:
            print(f"[{index}/{len(urls)}] Xato: {url} — {error}")
        if index < len(urls):
            time.sleep(args.delay)

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    print(f"\nEksport tugadi: {len(records)} ta karta")
    print(f"JSON fayl: {args.output}")
    print("Server bazasiga hech narsa yozilmadi.")

if __name__ == "__main__":
    main()
