import sqlite3

DB_NAME = "efootball.db"

def add_player():
    name = input("Futbolchi ismi: ").strip()
    nationality = input("Davlati: ").strip()
    club = input("Klubi: ").strip()
    position = input("Pozitsiyasi: ").strip()

    try:
        rating = int(input("Reytingi (0-110): "))
        if not 0 <= rating <= 110:
            print("Reyting 0 dan 110 gacha bo'lishi kerak.")
            return
    except ValueError:
        print("Reytingni raqam bilan kiriting.")
        return

    if not name:
        print("Futbolchi ismi bo'sh bo'lmasin.")
        return

    with sqlite3.connect(DB_NAME) as db:
        existing = db.execute(
            "SELECT id FROM players WHERE name = ?",
            (name,)
        ).fetchone()

        if existing:
            print("Bu futbolchi bazada allaqachon mavjud.")
            return

        db.execute("""
            INSERT INTO players
            (name, nationality, club, position, rating)
            VALUES (?, ?, ?, ?, ?)
        """, (name, nationality, club, position, rating))

    print(f"{name} bazaga muvaffaqiyatli qo'shildi!")

if __name__ == "__main__":
    add_player()
