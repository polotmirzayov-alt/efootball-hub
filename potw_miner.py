import json
import re
import time
import urllib.request
from pathlib import Path
from html import unescape
from urllib.parse import urljoin

BASE = "https://pesdb.net"
packs = json.loads(
    Path("potw_archive.json").read_text(encoding="utf-8")
)

cards = {}
errors = []

for i, pack in enumerate(packs, 1):
    print(f"\n[{i}/{len(packs)}] {pack['name']}")

    req = urllib.request.Request(
        pack["url"],
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            page = r.read().decode("utf-8", "replace")

        pattern = (
            r'<a\b[^>]*href=["\']([^"\']*players/[^"\']+)'
            r'["\'][^>]*>(.*?)</a>'
        )

        for href, label in re.findall(
            pattern, page, re.I | re.S
        ):
            player_url = urljoin(pack["url"], href)

            if not re.search(r"players/[^/]+-\d+", player_url):
                continue

            match = re.search(r"-(\d+)$", player_url)

            if not match:
                continue

            fid = match.group(1)
            name = " ".join(
                unescape(re.sub(r"<[^>]+>", "", label)).split()
            )

            image = (
                BASE + "/assets/img/card/f" + fid + ".png"
            )

            cards[fid] = {
                "featured_id": fid,
                "name": name,
                "player_url": player_url,
                "image_url": image,
                "pack": pack["name"],
                "category": pack["category"]
            }

        print("Topilgan kartalar:", len(cards))

    except Exception as e:
        errors.append({
            "pack": pack["name"],
            "error": str(e)
        })
        print("XATO:", e)

    time.sleep(2)

output = {
    "source": "PESDB",
    "total_cards": len(cards),
    "cards": list(cards.values()),
    "errors": errors
}

Path("potw_cards.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("\n========== YAKUNIY NATIJA ==========")
print("Kartalar:", len(cards))
print("Xatolar:", len(errors))
print("Fayl: potw_cards.json")
print("Asosiy baza o'zgartirilmadi.")
