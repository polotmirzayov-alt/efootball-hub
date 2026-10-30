import json
import os
import argparse
import urllib.request
import urllib.error
from pathlib import Path

INPUT = Path("pesdb_cards_enriched.jsonl")
POSITIONS = [
    "GK", "CB", "LB", "RB", "DMF", "CMF", "LMF",
    "RMF", "AMF", "LWF", "RWF", "SS", "CF"
]


def load_cards():
    if not INPUT.exists():
        raise FileNotFoundError(f"{INPUT} topilmadi")

    cards = []

    with INPUT.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{line_number}-qatorda JSON xatosi: {exc}"
                )

            cards.append(data)

    return cards


def build_payload(data):
    required = [
        "name", "nationality", "club", "card_name",
        "overall_rating", "max_overall", "card_type",
        "source_player_id", "featured_id",
        "primary_position", "stats", "skills"
    ]

    missing = [
        key for key in required
        if data.get(key) is None
    ]

    if missing:
        raise ValueError(
            f"{data.get('name', 'Nomaʼlum')}: "
            + ", ".join(missing)
        )

    name = str(data["name"]).strip()
    nationality = str(data["nationality"]).strip()
    club = str(data["club"]).strip()

    rating = data["overall_rating"]
    max_ovr = data["max_overall"]

    if (
        isinstance(rating, bool)
        or not isinstance(rating, int)
        or not 0 <= rating <= 112
    ):
        raise ValueError(f"{name}: OVR noto'g'ri")

    if (
        isinstance(max_ovr, bool)
        or not isinstance(max_ovr, int)
        or not 0 <= max_ovr <= 112
    ):
        raise ValueError(f"{name}: max OVR noto'g'ri")

    stats = data["stats"]
    skills = data["skills"]

    if not isinstance(stats, dict) or not stats:
        raise ValueError(f"{name}: stats noto'g'ri")

    for key, value in stats.items():
        if (
            not isinstance(key, str)
            or isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= 105
        ):
            raise ValueError(f"{name}: stat xatosi: {key}")

    if not isinstance(skills, list):
        raise ValueError(f"{name}: skills noto'g'ri")

    if any(not isinstance(x, str) for x in skills):
        raise ValueError(f"{name}: skills ichida noto'g'ri qiymat")

    primary = data["primary_position"]

    if primary not in POSITIONS:
        raise ValueError(f"{name}: primary_position noto'g'ri")

    secondary = data.get("secondary_positions", [])

    if not isinstance(secondary, list):
        raise ValueError(f"{name}: secondary_positions noto'g'ri")

    if any(x not in POSITIONS for x in secondary):
        raise ValueError(f"{name}: ikkilamchi pozitsiya noto'g'ri")

    secondary = list(dict.fromkeys(
        x for x in secondary if x != primary
    ))

    source_player_id = str(data["source_player_id"]).strip()
    featured_id = str(data["featured_id"]).strip()

    if not source_player_id or not featured_id:
        raise ValueError(f"{name}: manba ID noto'g'ri")

    source_card_id = f"{source_player_id}:{featured_id}"

    raw_boosters = data.get("boosters", [])

    booster_names = []

    if isinstance(raw_boosters, list):
        for booster in raw_boosters:
            if isinstance(booster, dict):
                booster_name = booster.get("name")
                if isinstance(booster_name, str) and booster_name.strip():
                    booster_names.append(booster_name.strip())
            elif isinstance(booster, str):
                booster_names.append(booster)

    card = {
        "player_name": name,
        "nationality": nationality,
        "club": club,
        "source": "PESDB",
        "source_card_id": source_card_id,
        "card_name": str(data["card_name"]).strip(),
        "rating": rating,
        "card_type": str(data["card_type"]).strip(),
        "position": primary,
        "playing_style": str(
            data.get("attacking_playing_style", "")
        ),
        "image": str(data.get("image_url") or ""),
        "release_date": ""
    }

    physics = {
        "static_stats": data.get("static_stats", {}),
        "player_details": data.get("details", {}),
        "booster_details": raw_boosters,
        "defensive_playing_style": data.get(
            "defensive_playing_style", ""
        ),
        "primary_position": primary,
        "secondary_positions": secondary
    }

    roles = {
        "ai_playing_styles": data.get("ai_playing_styles", []),
        "position_index": data.get("position"),
    }

    details = {
        "base_ovr": rating,
        "max_ovr": max_ovr,
        "height_cm": data.get("height_cm"),
        "weight_kg": data.get("weight_kg"),
        "age": data.get("age"),
        "stats": stats,
        "position_ratings": {},
        "skills": skills,
        "boosters": booster_names,
        "max_build": {},
        "physics": physics,
        "roles": roles,
        "source": "PESDB"
    }

    return {"card": card, "details": details}


def validate_all():
    raw_cards = load_cards()

    if not raw_cards:
        raise ValueError("JSONL fayl bo'sh")

    payloads = []
    seen = set()

    for index, data in enumerate(raw_cards, 1):
        payload = build_payload(data)
        card = payload["card"]

        source_id = card["source_card_id"]

        if source_id in seen:
            raise ValueError(f"Takroriy karta ID: {source_id}")

        seen.add(source_id)
        payloads.append(payload)

    return payloads


def request_json(url, token, payload):
    body = json.dumps(
        payload, ensure_ascii=False
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {exc.code}: {message[:1000]}"
        ) from exc


def main():
    parser = argparse.ArgumentParser(
        description="PESDB Bulk Importer"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Haqiqiy API import"
    )

    parser.add_argument(
        "--url",
        default=os.environ.get(
            "EFHUB_API",
            "http://127.0.0.1:8001"
        )
    )

    args = parser.parse_args()

    payloads = validate_all()

    players = {
        (
            p["card"]["player_name"].casefold(),
            p["card"]["nationality"].casefold(),
            p["card"]["club"].casefold()
        )
        for p in payloads
    }

    print("=== PESDB BULK IMPORT TEKSHIRUVI ===")
    print("Jami kartalar:", len(payloads))
    print("Noyob futbolchilar:", len(players))
    print("Noyob karta IDlari:", len({
        p["card"]["source_card_id"] for p in payloads
    }))

    for p in payloads:
        card = p["card"]
        details = p["details"]

        print(
            f'{card["player_name"]}: '
            f'OVR {card["rating"]}, '
            f'{card["position"]}, '
            f'{len(details["skills"])} Skills'
        )

    print("\nBarcha kartalar tekshiruvdan o'tdi.")

    if not args.apply:
        print("\nDRY-RUN: baza o'zgartirilmadi.")
        print("DRY-RUN: serverga so'rov yuborilmadi.")
        print("Haqiqiy import ushbu buyruqda bajarilmadi.")
        return

    token = os.environ.get("ADMIN_TOKEN", "")

    if not token:
        raise RuntimeError(
            "ADMIN_TOKEN mavjud emas. Import bekor qilindi."
        )

    print("\nDIQQAT: haqiqiy import boshlanmoqda.")

    result = request_json(
        args.url.rstrip("/") + "/api/import-pesdb-cards-bulk",
        token,
        {"items": payloads}
    )

    if not isinstance(result, dict):
        raise RuntimeError("Server javobi noto'g'ri")

    if result.get("error"):
        raise RuntimeError(str(result["error"]))

    print("\nSERVER JAVOBI:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
