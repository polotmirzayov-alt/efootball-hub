import json
import re
import time
import html
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

FILE = Path("pesdb_card_urls.json")

if not FILE.exists():
    print("XATO: pesdb_card_urls.json topilmadi.")
    raise SystemExit

data = json.loads(FILE.read_text(encoding="utf-8"))

# Katalog ichidan barcha PESDB futbolchi URLlarini yig‘ish
urls = set()

def collect(obj):
    if isinstance(obj, str):
        if "pesdb.net/efootball/players/" in obj:
            urls.add(obj)
    elif isinstance(obj, dict):
        for value in obj.values():
            collect(value)
    elif isinstance(obj, list):
        for value in obj:
            collect(value)

collect(data)
urls = sorted(urls)

if not urls:
    print("Katalogdan futbolchi URLlari topilmadi.")
    raise SystemExit

# 10 ta sahifani katalog bo‘ylab teng taqsimlab tanlash
count = min(10, len(urls))
indexes = [round(i * (len(urls) - 1) / max(1, count - 1))
           for i in range(count)]
sample = [urls[i] for i in indexes]

found = {}

print("Jami katalog URLlari:", len(urls))
print("Sinov sahifalari:", len(sample))

for number, url in enumerate(sample, 1):
    print(f"\n[{number}/{len(sample)}] Tekshirilmoqda: {url}")

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=25) as response:
            page = response.read().decode("utf-8", "replace")

        pattern = r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'

        for href, label in re.findall(pattern, page, re.I | re.S):
            text = re.sub(r"<[^>]+>", " ", label)
            text = html.unescape(re.sub(r"\s+", " ", text)).strip()

            if re.search(r"\bPOTW\b|Player of the Week", text, re.I):
                match = re.search(r"[?&]featured=(\d+)", href)
                if match:
                    found[match.group(1)] = text

        print("Topilgan POTW ID:", len(found))

    except Exception as error:
        print("XATO:", error)

    if number < len(sample):
        time.sleep(2)

print("\n========== NATIJA ==========")
print("Yangi tekshiruvda topilgan POTW ID:", len(found))

for fid, name in sorted(found.items(), key=lambda item: int(item[0])):
    print(fid, "—", name)

print("\nFaqat o‘qish. Fayllar va Render bazasi o‘zgartirilmadi.")
