import json
import re
import urllib.request
from html import unescape
from urllib.parse import urljoin

packs = json.load(open("potw_archive.json", encoding="utf-8"))

url = packs[0]["url"]

req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(req, timeout=30) as r:
    page = r.read().decode("utf-8", "replace")

print("========== FUTBOLCHI HAVOLALARI ==========")

links = re.findall(
    r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
    page, re.I | re.S
)

for href, label in links:
    if "players/" in href:
        name = unescape(re.sub(r"<[^>]+>", "", label))
        print("NOM:", " ".join(name.split()))
        print("URL:", urljoin(url, href))
        print("---")

print("\n========== RASMLAR ==========")

images = re.findall(
    r'<img\b[^>]*>',
    page,
    re.I
)

for img in images[:20]:
    print(img[:500])

print("\n========== ID TEKSHIRUVI ==========")

for pattern in [
    r'featured[^<]{0,100}',
    r'player_id[^<]{0,100}',
    r'data-id=["\'][^"\']+',
]:
    print("\nPATTERN:", pattern)
    for match in re.findall(pattern, page, re.I):
        print(match)

print("\nTEKSHIRUV TUGADI")
