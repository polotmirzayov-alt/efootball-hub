import re
import json
import html
import urllib.request

def clean(value):
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()

def parse_player(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=30) as r:
        page = r.read().decode("utf-8", "replace")

    result = {
        "player_url": url,
        "name": "",
        "overall_rating": None,
        "max_overall": None,
        "image_url": "",
        "stats": {},
        "playing_style": "",
        "skills": [],
        "boosters": []
    }

    # Futbolchi nomi
    match = re.search(
        r'<h1[^>]*id="player-name"[^>]*>(.*?)</h1>',
        page, re.S
    )
    if match:
        result["name"] = clean(match.group(1))

    # Sahifa tavsifi
    match = re.search(
        r'<meta[^>]*name="description"[^>]*content="([^"]*)"',
        page
    )
    if match:
        description = html.unescape(match.group(1))

        rating = re.search(r"Overall Rating (\d+)", description)
        maximum = re.search(r"Max Overall (\d+)", description)

        if rating:
            result["overall_rating"] = int(rating.group(1))
        if maximum:
            result["max_overall"] = int(maximum.group(1))

    # Karta rasmi
    match = re.search(
        r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"',
        page
    )
    if match:
        result["image_url"] = match.group(1)

    # Barcha asosiy statistikalar
    pattern = (
        r'<strong[^>]*data-stat-value="([^"]+)"'
        r'[^>]*>(.*?)</strong>'
    )

    for key, value in re.findall(pattern, page, re.S):
        value = clean(value)
        if value.isdigit():
            result["stats"][key] = int(value)

    # Playing Style
    match = re.search(
        r'Attacking Playing Style</span>\s*'
        r'<strong[^>]*>(.*?)</strong>',
        page, re.S
    )
    if match:
        result["playing_style"] = clean(match.group(1))

    # Player Skills
    match = re.search(
        r'<h2>Player Skills</h2>(.*?)'
        r'<h2>AI Playing Styles</h2>',
        page, re.S
    )
    if match:
        result["skills"] = [
            clean(x) for x in re.findall(
                r'<a[^>]*>(.*?)</a>', match.group(1), re.S
            )
        ]

    # Boosters
    result["boosters"] = [
        clean(x) for x in re.findall(
            r'<strong>([^<]*\+\d+)</strong>',
            page
        )
    ]

    return result


if __name__ == "__main__":
    with open("potw_cards.json", encoding="utf-8") as f:
        cards = json.load(f)["cards"]

    player = parse_player(cards[0]["player_url"])

    print(json.dumps(player, ensure_ascii=False, indent=2))

    with open("player_parsed.json", "w", encoding="utf-8") as f:
        json.dump(player, f, ensure_ascii=False, indent=2)

    print("\nSAQLANDI: player_parsed.json")
