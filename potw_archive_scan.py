import re
import time
import json
import urllib.request
from html import unescape
from pathlib import Path

BASE = "https://pesdb.net"
URL = BASE + "/efootball/packs/"

req = urllib.request.Request(
    URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(req, timeout=30) as r:
    page = r.read().decode("utf-8", "replace")

links = re.findall(
    r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
    page, re.I | re.S
)

packs = {}

for href, label in links:
    name = unescape(re.sub(r"<[^>]+>", " ", label))
    name = " ".join(name.split())

    category = None

    if re.search(r"\bPOTW\b", name, re.I):
        category = "POTW"
    elif re.search(r"\bPOTM\b", name, re.I):
        category = "POTM"

    if category and href.startswith("/efootball/packs/"):
        packs[href] = {
            "name": name,
            "category": category,
            "url": BASE + href
        }

print("Topilgan to'plamlar:", len(packs))

for pack in packs.values():
    print(pack["category"], "|", pack["name"])

Path("potw_archive.json").write_text(
    json.dumps(list(packs.values()), ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("\nArxiv katalogi saqlandi: potw_archive.json")
print("Faqat o'qish. Asosiy baza o'zgartirilmadi.")
