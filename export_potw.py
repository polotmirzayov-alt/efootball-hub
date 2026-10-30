import json
import re
import time
from urllib.parse import urlparse

from pesdb_export import get_html, extract_cards, parse_player

BASE = "https://pesdb.net"

FEATURED = {
    "POTW": "2087",
    "POTW European Club Championship": "2086",
}


def main():
    all_cards = {}

    for collection, featured_id in FEATURED.items():
        url = f"{BASE}/efootball/players/?featured={featured_id}"

        print(f"\nTekshirilmoqda: {collection}")

        try:
            page = get_html(url)
            urls = extract_cards(page)

            print(f"Topildi: {len(urls)} ta karta")

            for card_url in urls:
                all_cards[card_url] = collection

        except Exception as error:
            print(f"Ro'yxatni olishda xato: {error}")
            return

        time.sleep(2)

    records = []
    seen_ids = set()

    for index, (url, collection) in enumerate(
        all_cards.items(), 1
    ):
        try:
            card = parse_player(url)
            card_id = card.get("source_card_id", "")

            if not card_id or card_id in seen_ids:
                print(f"[{index}] Takroriy yoki bo'sh ID")
                continue

            if card.get("rating") is None:
                print(f"[{index}] Reyting topilmadi: {url}")
                continue

            seen_ids.add(card_id)

            # PESDB sahifasidagi haqiqiy karta turini saqlaymiz.
            card["potw_collection"] = collection

            records.append(card)

            print(
                f"[{index}/{len(all_cards)}] "
                f"{card['player_name']} — "
                f"{card['card_type']} — "
                f"{card['rating']} OVR"
            )

        except Exception as error:
            print(f"[{index}] Xato: {error}")

        time.sleep(2)

    output = "pesdb_potw_full_test.json"

    with open(output, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    print(f"\nEksport tugadi: {len(records)} ta karta")
    print(f"Fayl: {output}")
    print("Server bazasiga hech narsa yozilmadi.")


if __name__ == "__main__":
    main()
