import re
import html
from urllib.parse import urlencode, urljoin, urlparse, parse_qs
from pesdb_export import get_html

BASE = "https://pesdb.net/efootball/players/"
types = [
    "epic", "big_time", "show_time", "highlight",
    "trending", "legendary", "standard"
]

for card_type in types:
    url = BASE + "?" + urlencode({"type": card_type})
    visited = set()
    page_numbers = {1}
    print(f"\n=== {card_type.upper()} ===")

    try:
        for _ in range(3):
            if url in visited:
                break
            visited.add(url)
            source = get_html(url)

            for href in re.findall(
                r'<a\b[^>]*href=["\']([^"\']+)["\']',
                source, re.I
            ):
                href = html.unescape(href)
                full = urljoin(BASE, href)
                query = parse_qs(urlparse(full).query)

                if query.get("type", [None])[0] != card_type:
                    continue

                for value in query.get("page", []):
                    if value.isdigit():
                        page_numbers.add(int(value))

            print("Tekshirilgan sahifa:", url)
            next_links = re.findall(
                r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>\s*Next\s*</a>',
                source, re.I
            )
            if not next_links:
                break
            next_url = urljoin(BASE, html.unescape(next_links[0]))
            if next_url in visited:
                break
            url = next_url

        print("Topilgan sahifa raqamlari:", sorted(page_numbers))
    except Exception as e:
        print("XATO:", e)
