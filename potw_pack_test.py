import json
import re
import urllib.request
from html import unescape

packs = json.load(open("potw_archive.json", encoding="utf-8"))

for i, pack in enumerate(packs, 1):
    print(f"\n[{i}/{len(packs)}] {pack['name']}")

    req = urllib.request.Request(
        pack["url"],
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            page = r.read().decode("utf-8", "replace")

        print("HTML hajmi:", len(page))

        ids = set(re.findall(r'[?&]featured=(\d+)', page))

        print("Featured ID:", len(ids))
        print("POTW so'zi:", len(re.findall("POTW", page, re.I)))

        names = re.findall(
            r'<a\b[^>]*href=["\'][^"\']*players/[^"\']+["\'][^>]*>(.*?)</a>',
            page, re.I | re.S
        )

        for name in names[:15]:
            name = unescape(re.sub(r"<[^>]+>", "", name))
            print("Futbolchi:", " ".join(name.split()))

    except Exception as e:
        print("XATO:", e)

print("\nTEKSHIRUV TUGADI")
