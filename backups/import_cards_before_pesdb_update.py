import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = os.environ.get(
    "EFOOTBALL_HUB_URL",
    "https://efootball-hub-a8l3.onrender.com"
).rstrip("/")


def api_request(path, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token

    request = urllib.request.Request(BASE_URL + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(
        description="eFootball kartalarini tekshirish va import qilish"
    )
    parser.add_argument("file", help="Kartalar JSON fayli")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Kartalarni serverga yozish (haqiqiy import)"
    )
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as file:
        cards = json.load(file)

    if not isinstance(cards, list):
        print("XATO: JSON ro'yxat bo'lishi kerak.")
        return 2

    for number, card in enumerate(cards, 1):
        if not isinstance(card, dict):
            print(f"XATO: {number}-yozuv obyekt emas.")
            return 2
        if not str(card.get("player_name", "")).strip():
            print(f"XATO: {number}-yozuvda player_name yo'q.")
            return 2
        if not str(card.get("card_name", "")).strip():
            print(f"XATO: {number}-yozuvda card_name yo'q.")
            return 2
        try:
            rating = int(card.get("rating", 0))
        except (TypeError, ValueError):
            print(f"XATO: {number}-yozuvdagi rating son emas.")
            return 2
        if not 0 <= rating <= 200:
            print(f"XATO: {number}-yozuvdagi rating 0–200 oralig'ida emas.")
            return 2

    print(f"JSON tekshirildi: {len(cards)} ta karta yozuvi.")

    if not args.apply:
        for card in cards:
            print(
                f"Sinov: {card['player_name']} — {card['card_name']} "
                f"({card.get('rating', 0)} OVR)"
            )
        print("SINOV REJIMI: server bazasiga hech narsa yozilmadi.")
        print("Haqiqiy import qilish uchun --apply kerak.")
        return 0

    token = os.environ.get("ADMIN_TOKEN", "")
    if not token:
        print("XATO: ADMIN_TOKEN muhiti o'rnatilmagan. Import bajarilmadi.")
        return 2

    players = api_request("/api/players")
    by_name = {}
    for player in players:
        by_name.setdefault(player["name"].strip().casefold(), []).append(player)

    added = 0
    skipped = 0

    for card in cards:
        name = str(card["player_name"]).strip()
        matches = by_name.get(name.casefold(), [])

        if len(matches) != 1:
            print(f"O'tkazildi: {name} — futbolchi yagona tarzda aniqlanmadi.")
            skipped += 1
            continue

        player_id = matches[0]["id"]
        existing = api_request(f"/api/players/{player_id}/cards")
        card_name = str(card["card_name"]).strip()
        rating = int(card.get("rating", 0))
        card_type = str(card.get("card_type", "Standard"))

        if any(
            item.get("card_name", "").casefold() == card_name.casefold()
            and item.get("rating") == rating
            and item.get("card_type", "Standard") == card_type
            for item in existing
        ):
            print(f"Mavjud, o'tkazildi: {name} — {card_name}")
            skipped += 1
            continue

        payload = {
            "card_name": card_name,
            "card_type": card_type,
            "rating": rating,
            "position": card.get("position", ""),
            "playing_style": card.get("playing_style", ""),
            "image": card.get("image", ""),
            "release_date": card.get("release_date", ""),
            "source": card.get("source", "json_import"),
        }

        request = urllib.request.Request(
            f"{BASE_URL}/api/players/{player_id}/cards",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                response.read()
            print(f"Qo'shildi: {name} — {card_name}")
            added += 1
        except urllib.error.HTTPError as error:
            print(f"XATO: {card_name}; HTTP {error.code}")
            skipped += 1

    print(f"Yakun: qo'shildi {added}; o'tkazildi/xato {skipped}.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, urllib.error.URLError) as error:
        print("XATO:", error)
        sys.exit(1)
