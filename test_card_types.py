from urllib.parse import urlencode
from pesdb_export import get_html, extract_cards

types = [
    "epic",
    "big_time",
    "show_time",
    "highlight",
    "trending",
    "legendary",
    "standard",
]

for card_type in types:
    url = "https://pesdb.net/efootball/players/?" + urlencode({
        "type": card_type
    })
    try:
        page = get_html(url)
        cards = extract_cards(page)
        print(f"{card_type}: {len(cards)} ta karta")
        for card in cards[:3]:
            print("  ", card)
    except Exception as e:
        print(f"{card_type}: XATO — {e}")
