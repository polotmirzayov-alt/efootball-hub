page = open("player_test.html", encoding="utf-8").read()

keywords = [
    "Attacking Awareness",
    "Ball Control",
    "Dribbling",
    "Defensive Awareness",
    "Speed",
    "Acceleration",
    "Stamina",
    "Playing Style",
    "Overall Rating",
    "Max Overall",
    "Player Skills",
    "Booster"
]

print("========== PESDB MAYDONLARI ==========")

for word in keywords:
    index = page.find(word)

    if index == -1:
        print(f"\n[{word}] topilmadi")
        continue

    start = max(0, index - 250)
    end = min(len(page), index + 500)

    print(f"\n--- {word} ---")
    print(page[start:end].replace("\n", " ")[:750])

print("\nTEKSHIRUV TUGADI")
