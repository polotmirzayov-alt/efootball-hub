import json
import os
import sys
import time
from pathlib import Path

# ==================================================
# EFOOTBALL BUILD MASTER ULTIMATE
# A custom football build assistant for Termux
# ==================================================

GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
PURPLE = "\033[1;35m"
WHITE = "\033[1;37m"
DIM = "\033[2;37m"
RESET = "\033[0m"

DATA_FILE = Path.home() / ".efbm_players.json"

DEFAULT_PLAYERS = {
    "messi": {
        "name": "Lionel Messi",
        "card": "Epic / Example Build",
        "position": "SS / AMF / RWF",
        "stats": {
            "Shooting": 8,
            "Passing": 4,
            "Dribbling": 12,
            "Dexterity": 10,
            "Lower Body Strength": 4
        },
        "highlights": [
            "Dribbling va yaqin nazorat",
            "Muvozanat va tezkor burilish",
            "Aniq zarba va ijodkor pas"
        ],
        "tip": "Tor hududlarda dribling, tezkor pas va qulay vaziyatda zarbadan foydalan."
    },
    "nakata": {
        "name": "Hidetoshi Nakata",
        "card": "Epic / Example Build",
        "position": "AMF / CMF",
        "stats": {
            "Shooting": 4,
            "Passing": 9,
            "Dribbling": 11,
            "Dexterity": 8,
            "Lower Body Strength": 8
        },
        "highlights": [
            "To'p nazorati va qisqa paslar",
            "Hujumni bog'lash",
            "Harakat va chidamlilik"
        ],
        "tip": "To'pni tez uzat, bo'sh zonalarni top va hujumchilarni pas bilan ta'minla."
    },
    "ronaldo": {
        "name": "Cristiano Ronaldo",
        "card": "Build Template",
        "position": "CF / LWF",
        "stats": {
            "Shooting": 12,
            "Passing": 2,
            "Dribbling": 5,
            "Dexterity": 8,
            "Lower Body Strength": 8
        },
        "highlights": [
            "Zarba va yakunlash",
            "Jarima maydonchasidagi harakat",
            "Havodagi kurash"
        ],
        "tip": "Jarima maydonchasida qulay pozitsiya egalla va krosslardan foydalan."
    }
}


def clear():
    os.system("clear")


def pause():
    input(f"\n{DIM}Davom etish uchun Enter bosing...{RESET}")


def banner():
    print(f"""{GREEN}
╔══════════════════════════════════════════╗
║                                          ║
║      ⚽ EFOOTBALL BUILD MASTER ⚽          ║
║             U L T I M A T E              ║
║                                          ║
║       YOUR BUILD. YOUR FOOTBALL.         ║
╚══════════════════════════════════════════╝{RESET}""")


def load_database():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            print(f"{RED}Bazani o'qib bo'lmadi. Namuna baza yuklanadi.{RESET}")

    return json.loads(json.dumps(DEFAULT_PLAYERS))


def save_database(database):
    temp_file = DATA_FILE.with_suffix(".tmp")
    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(database, file, ensure_ascii=False, indent=2)
        temp_file.replace(DATA_FILE)
        return True
    except OSError as error:
        print(f"{RED}Saqlash xatosi: {error}{RESET}")
        return False


def show_player(key, player):
    print(f"\n{GREEN}{'═' * 44}{RESET}")
    print(f"{WHITE}⚽ {player.get('name', key)}{RESET}")
    print(f"{CYAN}Karta: {player.get('card', 'Noma’lum')}{RESET}")
    print(f"{CYAN}Pozitsiya: {player.get('position', 'Noma’lum')}{RESET}")
    print(f"{GREEN}{'─' * 44}{RESET}")

    print(f"{YELLOW}📊 BUILD OCHKO TAQSIMOTI{RESET}")
    stats = player.get("stats", {})
    total = 0

    for stat, value in stats.items():
        try:
            value = int(value)
        except (ValueError, TypeError):
            continue

        total += value
        bar = "█" * min(max(value, 0), 20)
        print(f"{GREEN}{stat:<24}{RESET} {WHITE}{value:>3}{RESET} {CYAN}{bar}{RESET}")

    print(f"\n{PURPLE}Jami kiritilgan ochko: {total}{RESET}")

    print(f"\n{YELLOW}⚡ ASOSIY XUSUSIYATLAR{RESET}")
    for item in player.get("highlights", []):
        print(f"  • {item}")

    print(f"\n{PURPLE}🧠 MURABBIY MASLAHATI{RESET}")
    print(f"  {player.get('tip', 'O‘yin uslubingga mos taktika tanla.')}")

    print(f"\n{DIM}Eslatma: buildlar namunaviy. Natija karta versiyasi, "
          f"o‘yin uslubi va o‘yin mexanikasiga bog‘liq.{RESET}")
    print(f"{GREEN}{'═' * 44}{RESET}")


def search_player(database):
    query = input(f"{CYAN}Futbolchi nomi: {RESET}").strip().lower()

    if not query:
        print(f"{RED}Nom kiritilmadi.{RESET}")
        return

    matches = [
        (key, player)
        for key, player in database.items()
        if query in key.lower()
        or query in player.get("name", "").lower()
    ]

    if not matches:
        print(f"{RED}❌ '{query}' topilmadi.{RESET}")
        print(f"{DIM}Yangi karta qo‘shish menyusidan foydalanishing mumkin.{RESET}")
        return

    for key, player in matches:
        show_player(key, player)


def add_player(database):
    name = input(f"{CYAN}Futbolchi yoki murabbiy ismi: {RESET}").strip()
    if not name:
        print(f"{RED}Ism bo‘sh bo‘lishi mumkin emas.{RESET}")
        return

    key = input(f"{CYAN}Qidiruv kaliti (masalan, mbappe): {RESET}").strip().lower()
    if not key or len(key) > 60:
        print(f"{RED}Kalit noto‘g‘ri.{RESET}")
        return

    if key in database:
        confirm = input(f"{YELLOW}Bu kalit mavjud. Yangilansinmi? (ha/yo‘q): {RESET}")
        if confirm.strip().lower() not in ("ha", "h", "yes", "y"):
            print("Bekor qilindi.")
            return

    card = input("Karta turi: ").strip() or "Custom"
    position = input("Pozitsiya: ").strip() or "Noma'lum"

    stats = {}
    print(f"\n{YELLOW}Statistika nomi va qiymatini kiriting.{RESET}")
    print("Tugatish uchun nom o'rniga 'tamom' yozing.")

    while len(stats) < 20:
        stat = input("Statistika nomi: ").strip()
        if stat.lower() == "tamom":
            break
        if not stat:
            continue

        raw = input("Ochko (0-99): ").strip()
        try:
            value = int(raw)
            if not 0 <= value <= 99:
                raise ValueError
        except ValueError:
            print(f"{RED}0 dan 99 gacha butun son kiriting.{RESET}")
            continue

        stats[stat[:50]] = value

    highlights = []
    tip = input("Murabbiy maslahati: ").strip() or "O‘yin uslubingga mos taktika tanla."

    database[key] = {
        "name": name[:100],
        "card": card[:50],
        "position": position[:50],
        "stats": stats,
        "highlights": highlights,
        "tip": tip[:500]
    }

    if save_database(database):
        print(f"{GREEN}✓ {name} bazaga saqlandi!{RESET}")


def list_players(database):
    print(f"\n{YELLOW}📚 BAZADAGI KARTALAR{RESET}")
    if not database:
        print("Baza hozircha bo‘sh.")
        return

    for number, (key, player) in enumerate(
        sorted(database.items()), start=1
    ):
        print(f"{GREEN}{number:>3}.{RESET} {player.get('name', key)} "
              f"{DIM}[{key}]{RESET}")

    print(f"\nJami: {len(database)} ta karta")


def delete_player(database):
    key = input(f"{CYAN}O'chirish uchun kalit: {RESET}").strip().lower()

    if key not in database:
        print(f"{RED}Bunday kalit topilmadi.{RESET}")
        return

    name = database[key].get("name", key)
    confirm = input(
        f"{RED}{name} kartasini o'chirishni tasdiqlaysanmi? (ha/yo'q): {RESET}"
    )

    if confirm.strip().lower() in ("ha", "h", "yes", "y"):
        del database[key]
        if save_database(database):
            print(f"{GREEN}Karta o'chirildi.{RESET}")


def main():
    database = load_database()

    while True:
        clear()
        banner()
        print(f"\n{WHITE}1.{RESET} 🔎 Futbolchi qidirish")
        print(f"{WHITE}2.{RESET} 📚 Barcha kartalar")
        print(f"{WHITE}3.{RESET} ➕ Yangi karta qo'shish")
        print(f"{WHITE}4.{RESET} 🗑️ Kartani o'chirish")
        print(f"{WHITE}5.{RESET} 📊 Baza statistikasi")
        print(f"{WHITE}0.{RESET} 🚪 Chiqish")

        choice = input(f"\n{CYAN}Tanlovingiz: {RESET}").strip()

        if choice == "1":
            search_player(database)
            pause()
        elif choice == "2":
            list_players(database)
            pause()
        elif choice == "3":
            add_player(database)
            pause()
        elif choice == "4":
            delete_player(database)
            pause()
        elif choice == "5":
            print(f"\n{YELLOW}Bazada {len(database)} ta karta mavjud.{RESET}")
            pause()
        elif choice == "0":
            print(f"{GREEN}EFOOTBALL BUILD MASTER — GAME ON! ⚽{RESET}")
            break
        else:
            print(f"{RED}Noto'g'ri tanlov.{RESET}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{YELLOW}Dastur to'xtatildi. Omad!{RESET}")
        sys.exit(0)
