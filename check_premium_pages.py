import re
import html
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from pesdb_export import get_html, extract_cards

base = "https://pesdb.net/efootball/players/"
types = ["epic", "big_time", "show_time", "highlight"]

for kind in types:
    print(f"\n=== {kind.upper()} ===")
    url = base + "?" + urlencode({"type": kind})
    visited = set()
    all_cards = set()

    for page_no in range(1, 101):
        if url in visited:
            print("Takroriy URL aniqlandi; to‘xtatildi.")
            break

        visited.add(url)

        try:
            source = get_html(url)
            cards = extract_cards(source)
            all_cards.update(cards)
            print(f"{page_no}-sahifa: {len(cards)} ta karta")
        except Exception as e:
            print("XATO:", e)
            break

        links = re.findall(
            r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>\s*Next\s*</a>',
            source, re.I
        )

        if not links:
            print("Keyingi sahifa havolasi yo‘q.")
            break

        url = urljoin(base, html.unescape(links[0]))

    print("Takrorlarsiz jami karta havolalari:", len(all_cards))
