import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from pesdb_parser_v2 import parse_page

URL_FILE = Path("pesdb_sitemap_new_urls.json")
OUTPUT_FILE = Path("pesdb_new_cards_test.jsonl")
ERROR_FILE = Path("pesdb_miner_errors.jsonl")

MAX_NEW_CARDS = 3
WAIT_SECONDS = 5

if not URL_FILE.exists():
    raise SystemExit("XATOLIK: URL katalogi topilmadi.")

urls = json.loads(URL_FILE.read_text(encoding="utf-8"))

saved_urls = set()
saved_ids = set()

if OUTPUT_FILE.exists():
    with OUTPUT_FILE.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            try:
                card = json.loads(line)
                if card.get("player_url"):
                    saved_urls.add(card["player_url"])
                if card.get("source_player_id"):
                    saved_ids.add(str(card["source_player_id"]))
            except json.JSONDecodeError:
                print("OGOHLANTIRISH: JSONL ichida buzilgan qator bor.")

pending = [
    url for url in urls
    if url not in saved_urls
]

print("Katalogdagi URL:", len(urls))
print("Oldin saqlangan:", len(saved_urls))
print("Tekshiriladigan URL:", min(MAX_NEW_CARDS, len(pending)))
print("Natija fayli:", OUTPUT_FILE)
print("-" * 40)

success = 0

for index, url in enumerate(pending[:MAX_NEW_CARDS]):
    print(f"\n[{index + 1}/{min(MAX_NEW_CARDS, len(pending))}]")
    print("Tekshirilmoqda:", url)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")

    except urllib.error.HTTPError as error:
        print("HTTP xatosi:", error.code)

        if error.code in (403, 429):
            print("Xavfsizlik cheklovi. Miner to‘xtatildi.")
            break

        record = {"url": url, "error": f"HTTP {error.code}"}
        with ERROR_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
        continue

    except Exception as error:
        print("Ulanish xatosi:", str(error))
        record = {"url": url, "error": str(error)}
        with ERROR_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
        continue

    try:
        card = parse_page(html, url)

        if not card or not card.get("name") or not card.get("stats"):
            raise ValueError("Karta ma'lumotlari to'liq ajratilmadi.")

        player_id = str(card.get("source_player_id") or "")

        if url in saved_urls or (player_id and player_id in saved_ids):
            print("Takroriy karta. Saqlanmadi.")
            continue

        with OUTPUT_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(card, ensure_ascii=False) + "\n")

        saved_urls.add(url)
        if player_id:
            saved_ids.add(player_id)

        success += 1
        print("SAQLANDI:", card["name"])
        print("OVR:", card.get("overall_rating"))
        print("Karta turi:", card.get("card_type"))
        print("Statistika:", len(card.get("stats", {})))
        print("Skills:", len(card.get("skills", [])))

    except Exception as error:
        print("Parser xatosi:", str(error))
        record = {"url": url, "error": str(error)}
        with ERROR_FILE.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    if index < min(MAX_NEW_CARDS, len(pending)) - 1:
        print(f"{WAIT_SECONDS} soniya kutilyapti...")
        time.sleep(WAIT_SECONDS)

print("\n" + "-" * 40)
print("Sinov yakunlandi.")
print("Yangi saqlangan kartalar:", success)
print("Natija:", OUTPUT_FILE)
print("Xatolar:", ERROR_FILE)
print("Server va asosiy baza o'zgartirilmadi.")
