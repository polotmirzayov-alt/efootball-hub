import sqlite3

DB_NAME = "efootball.db"

def show_player_card():
    name = input("Futbolchi ismini kiriting: ").strip()

    with sqlite3.connect(DB_NAME) as db:
        players = db.execute("""
            SELECT name, nationality, club, position, rating, card_type
            FROM players
            WHERE name LIKE ?
        """, (f"%{name}%",)).fetchall()

    if not players:
        print("Futbolchi topilmadi!")
        return

    if len(players) > 1:
        print("Bir nechta futbolchi topildi. Ismni aniqroq kiriting.")
        return

    player = players[0]

    print("\n" + "=" * 32)
    print("       🏆 eFOOTBALL HUB")
    print("=" * 32)
    print(f"   ⭐ OVR: {player[4]}")
    print(f"   👤 Ism: {player[0]}")
    print(f"   🌍 Davlat: {player[1]}")
    print(f"   🏟️ Klub: {player[2]}")
    print(f"   ⚽ Pozitsiya: {player[3]}")
    print(f"   💎 Karta: {player[5]}")
    print("=" * 32)

if __name__ == "__main__":
    show_player_card()
