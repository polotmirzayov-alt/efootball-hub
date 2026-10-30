import re
import urllib.request
from urllib.parse import urljoin, urlparse

BASE = "https://pesdb.net"

for featured_id in ("2087", "2086"):
    url = f"{BASE}/efootball/players/?featured={featured_id}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            page = response.read().decode("utf-8", "replace")

        links = re.findall(
            r'<a\b[^>]*href=["\']([^"\']+)["\']',
            page,
            re.I
        )

        cards = {
            urljoin(BASE, link)
            for link in links
            if re.search(
                r"/efootball/players/[^/]+-\d+/?$",
                urlparse(link).path
            )
        }

        print(f"featured={featured_id}: {len(cards)} ta karta")

    except Exception as error:
        print(f"featured={featured_id}: xato — {error}")
