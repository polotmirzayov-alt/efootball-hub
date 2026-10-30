import json
import time
from pathlib import Path
from pesdb_export import parse_player

PACKS = {
    "POTW European Club Championship": [
        "bernardo-silva-52912923449122",
        "carlos-augusto-52912923467603",
        "lucas-hernandez-52912923449613",
        "mario-hermoso-52912923454893",
        "nico-paz-52912923500110",
        "phil-foden-52912923459704",
        "rio-ngumoha-52912923519041",
        "ross-barkley-52912923389598",
        "scott-mctominay-52912923461501",
        "victor-osimhen-52912923471791",
        "yann-sommer-52912923381523",
    ],
    "POTW Worldwide": [
        "alejandro-grimaldo-52904601946818",
        "alex-berenguer-52904601949372",
        "andy-diouf-52904601990379",
        "christian-pulisic-52904601957864",
        "douglas-luiz-52904601961971",
        "gabriel-magalhaes-52904601956967",
        "jeremy-jacquet-52904602005240",
        "kylian-mbappe-52904601956478",
        "mathys-tel-52904601993215",
        "maximilian-beier-52904601987919",
        "suzuki-zion-52904601981375",
    ],
    "POTM Trendyol Süper Lig": [
        "abdulkerim-bardakci-53988275907363",
        "adrian-benedyczak-53988275928737",
        "emirhan-topcu-53988275905208",
        "gift-orban-53988275941823",
        "irfan-can-kahveci-53988275902638",
        "noah-saviolo-53988275961077",
    ],
    "POTM Brasileirão": [
        "alvaro-montoro-53991228739881",
        "fabio-53991228575687",
        "guillermo-varela-53991228619568",
        "kaio-jorge-53991228698710",
        "marcinho-53991228688058",
        "vitor-roque-53991228723165",
    ],
    "POTM J.LEAGUE": [
        "kaneko-takuro-53985859992727",
        "kim-seung-gyu-53985859923942",
        "marcinho-53985859977501",
        "mateus-brunetti-53985859992654",
        "matheus-thuler-53985859981027",
        "tatsuta-yugo-53985859984212",
    ],
}

BASE = "https://pesdb.net/efootball/players/"
OUTPUT = Path("pesdb_potw_potm_full.json")

records = []
seen_ids = set()
errors = []

total = sum(len(items) for items in PACKS.values())
index = 0

for collection, slugs in PACKS.items():
    print(f"\n===== {collection} =====")

    for slug in slugs:
        index += 1
        url = BASE + slug

        try:
            card = parse_player(url)
            card_id = str(card.get("source_card_id") or "")

            if not card_id:
                errors.append((url, "source_card_id yo‘q"))
                print(f"[{index}/{total}] ID topilmadi: {slug}")
                continue

            if card_id in seen_ids:
                errors.append((url, "Takroriy source_card_id"))
                print(f"[{index}/{total}] Takroriy ID: {card_id}")
                continue

            if card.get("rating") is None:
                errors.append((url, "Reyting topilmadi"))
                print(f"[{index}/{total}] Reyting yo‘q: {slug}")
                continue

            seen_ids.add(card_id)
            card["potw_collection"] = collection
            records.append(card)

            print(
                f"[{index}/{total}] "
                f"{card.get('player_name')} — "
                f"{card.get('rating')} OVR — {collection}"
            )

        except Exception as e:
            errors.append((url, str(e)))
            print(f"[{index}/{total}] XATO: {slug}: {e}")

        time.sleep(2)

# Faqat yangi faylga yoziladi.
temp = OUTPUT.with_suffix(".tmp")
temp.write_text(
    json.dumps(records, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
temp.replace(OUTPUT)

print("\n===== EKSPORT HISOBOTI =====")
print("Kutilgan:", total)
print("Muvaffaqiyatli:", len(records))
print("Xatolar:", len(errors))
print("Yangi fayl:", OUTPUT)

if errors:
    print("\nTekshirilishi kerak bo‘lgan yozuvlar:")
    for url, reason in errors:
        print(reason, "=>", url)

print("\nRender bazasiga hech narsa yuborilmadi.")
