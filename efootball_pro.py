import sys
import time

def print_header():
    print("\033[1;36m" + "="*60)
    print("     🔥 eFOOTBALL ULTIMATE PRO HUB (TERMUX EDITION) 🔥")
    print("="*60 + "\033[0m")

# Barcha detallar va turlar bilan boyitilgan kengaytirilgan baza
database = {
    "nakata": {
        "name": "Nakata Hidetoshi",
        "type": "EPIC",
        "theme": "🧊 Muz parchalanmoqda... [EPIC CARD EFFECT]",
        "overall": "89 (Max 106.74)",
        "height": "175 cm", "weight": "70 kg", "age": "28",
        "positions": {
            "CF": 82, "SS": 89, "LWF": 85, "RWF": 85,
            "AMF": 95, "CMF": 92, "LMF": 88, "RMF": 88, "DMF": 80, "CB": 60, "GK": 40
        },
        "stats": {
            "Attacking Awareness": 86, "Ball Control": 96, "Dribbling": 94,
            "Tight Possession": 96, "Low Pass": 96, "Lofted Pass": 92,
            "Finishing": 84, "Speed": 87, "Acceleration": 92,
            "Kicking Power": 91, "Physical Contact": 83, "Balance": 88, "Stamina": 85,
            "Defensive Awareness": 69, "Defensive Engagement": 72, "Tackling": 68, "Aggression": 75
        },
        "physics": {
            "Arm Length": 5, "Shoulder Width": 11, "Neck Length": 4, "Chest Measurement": 6,
            "Neck Size": 9, "Shoulder Height": 8, "Leg Length": 9, "Thigh Size": 7,
            "Waist Size": 7, "Arm Size": 8, "Calf Size": 7,
            "Leg Coverage": "169", "Arm Coverage": "156.7", "Jump Height": "239.2"
        },
        "roles": {"Short FK": 76, "Long FK": 73, "PK": 75, "CK Taker": 83, "Join Attack": 61, "Captain": 78},
        "skills": ["Long-range Curler", "Long-range Shooting", "Through Passing", "Super-sub", "Phenomenal Pass", "Double Touch"],
        "max_build": "SHT: 4 | PAS: 9 | DRI: 11 | DEX: 8 | LBS: 8"
    },
    "ronaldo": {
        "name": "Cristiano Ronaldo",
        "type": "BIG TIME",
        "theme": "🔥 Olov yonib turibdi! [BIG TIME EFFECT ACTIVE]",
        "overall": "97 (Max 108.5)",
        "height": "187 cm", "weight": "85 kg", "age": "38",
        "positions": {
            "CF": 99, "SS": 96, "LWF": 95, "RWF": 94,
            "AMF": 88, "CMF": 75, "LMF": 85, "RMF": 85, "DMF": 55, "CB": 45, "GK": 40
        },
        "stats": {
            "Attacking Awareness": 99, "Ball Control": 92, "Dribbling": 91,
            "Tight Possession": 90, "Low Pass": 85, "Lofted Pass": 84,
            "Finishing": 99, "Speed": 93, "Acceleration": 91,
            "Kicking Power": 99, "Physical Contact": 90, "Balance": 82, "Stamina": 89,
            "Defensive Awareness": 40, "Defensive Engagement": 42, "Tackling": 38, "Aggression": 50
        },
        "physics": {
            "Arm Length": 7, "Shoulder Width": 9, "Neck Length": 5, "Chest Measurement": 8,
            "Neck Size": 8, "Shoulder Height": 7, "Leg Length": 8, "Thigh Size": 9,
            "Waist Size": 6, "Arm Size": 7, "Calf Size": 8,
            "Leg Coverage": "180", "Arm Coverage": "165.0", "Jump Height": "260.0"
        },
        "roles": {"Short FK": 92, "Long FK": 95, "PK": 99, "CK Taker": 80, "Join Attack": 95, "Captain": 90},
        "skills": ["First-time Shot", "Acrobatic Finishing", "Heading", "Sombrero", "Cut Behind & Turn", "Scotch Move"],
        "max_build": "SHT: 8 | DRI: 8 | DEX: 8 | LBS: 12"
    },
    "messi": {
        "name": "Lionel Messi",
        "type": "SHOW TIME",
        "theme": "🌊 Suv to'lqini va oqim harakatda! [SHOW TIME EFFECT]",
        "overall": "96 (Max 107.2)",
        "height": "170 cm", "weight": "72 kg", "age": "35",
        "positions": {
            "CF": 95, "SS": 99, "LWF": 97, "RWF": 99,
            "AMF": 96, "CMF": 82, "LMF": 90, "RMF": 90, "DMF": 50, "CB": 40, "GK": 35
        },
        "stats": {
            "Attacking Awareness": 96, "Ball Control": 99, "Dribbling": 99,
            "Tight Possession": 99, "Low Pass": 95, "Lofted Pass": 90,
            "Finishing": 97, "Speed": 90, "Acceleration": 98,
            "Kicking Power": 88, "Physical Contact": 65, "Balance": 99, "Stamina": 80,
            "Defensive Awareness": 35, "Defensive Engagement": 35, "Tackling": 30, "Aggression": 40
        },
        "physics": {
            "Arm Length": 4, "Shoulder Width": 6, "Neck Length": 4, "Chest Measurement": 5,
            "Neck Size": 6, "Shoulder Height": 5, "Leg Length": 7, "Thigh Size": 6,
            "Waist Size": 5, "Arm Size": 6, "Calf Size": 6,
            "Leg Coverage": "165", "Arm Coverage": "150.0", "Jump Height": "220.0"
        },
        "roles": {"Short FK": 98, "Long FK": 94, "PK": 96, "CK Taker": 92, "Join Attack": 90, "Captain": 85},
        "skills": ["Double Touch", "Sombrero", "Sole Control", "One-touch Pass", "Through Passing", "GP Turn"],
        "max_build": "SHT: 6 | PAS: 8 | DRI: 12 | DEX: 10 | LBS: 4"
    },
    "saliba": {
        "name": "William Saliba",
        "type": "POTW",
        "theme": "✨ Chiroyli yorug'lik nurlari tarqalmoqda! [POTW LIGHT EFFECT]",
        "overall": "89 (Max 102)",
        "height": "190 cm", "weight": "83 kg", "age": "22",
        "positions": {
            "CF": 72, "SS": 71, "LWF": 76, "RWF": 76,
            "AMF": 74, "CMF": 83, "LMF": 81, "RMF": 81, "DMF": 94, "CB": 102, "GK": 51
        },
        "stats": {
            "Attacking Awareness": 52, "Ball Control": 67, "Dribbling": 60,
            "Tight Possession": 70, "Low Pass": 72, "Lofted Pass": 68,
            "Finishing": 51, "Speed": 87, "Acceleration": 79,
            "Kicking Power": 66, "Physical Contact": 92, "Balance": 64, "Stamina": 89,
            "Defensive Awareness": 94, "Defensive Engagement": 94, "Tackling": 94, "Aggression": 91
        },
        "physics": {
            "Arm Length": 5, "Shoulder Width": 7, "Neck Length": 6, "Chest Measurement": 7,
            "Neck Size": 7, "Shoulder Height": 4, "Leg Length": 7, "Thigh Size": 8,
            "Waist Size": 7, "Arm Size": 6, "Calf Size": 8,
            "Leg Coverage": "183.4", "Arm Coverage": "170.3", "Jump Height": "278.7"
        },
        "roles": {"Short FK": 69, "Long FK": 63, "PK": 59, "CK Taker": 72, "Join Attack": 87, "Captain": 78},
        "skills": ["Heading", "One-touch Pass", "Weighted Pass", "Man Marking", "Interception", "Blocker"],
        "max_build": "DEX: 8 | LBS: 8 | DEF: 12"
    }
}

def main():
    print_header()
    print("\033[1;33m[!] Bazadagi futbolchilar: nakata, ronaldo, messi, saliba\033[0m")
    print("\033[1;32m[!] 'Max [ism]' deb yozsangiz to'liq 'Max Build' va detallar chiqadi.\033[0m\n")

    while True:
        query = input("\033[1;35m⚽ Futbolchi nomini kiriting (Chiqish uchun 'exit'): \033[0m").strip().lower()

        if query == 'exit':
            print("\n\033[1;31mDastur yakunlandi. O'yinda omad!\033[0m")
            break

        is_max = False
        if query.startswith("max "):
            is_max = True
            query = query.replace("max ", "").strip()

        if query in database:
            p = database[query]
            print("\n" + "\033[1;32m" + "█"*60)
            print(f" ⭐ {p['name']} | Karta Turi: [{p['type']}]")
            print(f" ✨ Effekt: {p['theme']}")
            print("█"*60 + "\033[0m")

            print(f"📊 Reyting: \033[1;33m{p['overall']}\033[0m | Bo'yi: {p['height']} | Vazni: {p['weight']} | Yoshi: {p['age']}")

            # Pozitsiyalar reytingi
            print("\n\033[1;36m🏟️ POZITSIYALAR REYTINGI:\033[0m")
            pos = p['positions']
            print(f"     [CF: {pos['CF']}]      [SS: {pos['SS']}]      [AMF: {pos['AMF']}]")
            print(f"  [LWF: {pos['LWF']}]    [RWF: {pos['RWF']}]    [CMF: {pos['CMF']}]")
            print(f"  [LMF: {pos['LMF']}]    [RMF: {pos['RMF']}]    [DMF: {pos['DMF']}]")
            print(f"          [CB: {pos['CB']}]      [GK: {pos['GK']}]")

            # Stats (Statistikalar)
            print("\n\033[1;33m📈 STATS (ASOSIY KO'RSATKICHLAR):\033[0m")
            for k, v in p['stats'].items():
                color = "\033[1;32m" if v >= 90 else ("\033[1;33m" if v >= 80 else "\033[1;31m")
                print(f"  • {k:<24} : {color}{v}\033[0m")

            # Player Model & Physics
            print("\n\033[1;34m🧬 PLAYER MODEL & PHYSICS:\033[0m")
            print(f"  • Leg Coverage    : \033[1;33m{p['physics']['Leg Coverage']}\033[0m")
            print(f"  • Arm Coverage    : \033[1;33m{p['physics']['Arm Coverage']}\033[0m")
            print(f"  • Jump Height     : \033[1;33m{p['physics']['Jump Height']}\033[0m")

            # In-Match Roles
            print("\n\033[1;35m🎯 IN-MATCH ROLES:\033[0m")
            r = p['roles']
            print(f"  • Short FK Taker : {r['Short FK']}  |  CK Taker   : {r['CK Taker']}")
            print(f"  • Long FK Taker  : {r['Long FK']}  |  Join Attack: {r['Join Attack']}")
            print(f"  • PK Taker       : {r['PK']}  |  Captain    : {r['Captain']}")

            # Max Build va Tugma holati
            print("\n\033[1;32m⚙️ BUILDS & MAX TUGMASI:\033[0m")
            print(f"  🔥 Optimal Ochko Taqsmioti (Max Build): \033[1;33m{p['max_build']}\033[0m")

            # Skills
            print("\n\033[1;31m⚡ SKILLS:\033[0m")
            print("  " + ", ".join(p['skills']))
            print("\033[1;32m" + "█"*60 + "\033[0m\n")

        else:
            print(f"\n\033[1;31m❌ '{query'}' bo'yicha ma'lumot topilmadi!\033[0m\n")

if __name__ == "__main__":
    main()
