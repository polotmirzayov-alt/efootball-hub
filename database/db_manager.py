import sqlite3

DB_NAME = "efootball.db"

def add_player(name, nationality, club, position, rating):
    with sqlite3.connect(DB_NAME) as db:
        existing = db.execute(
            "SELECT id FROM players WHERE name = ?",
            (name,)
        ).fetchone()

        if existing:
            print(f"Player already exists: {name}")
            return

        db.execute("""
            INSERT INTO players
            (name, nationality, club, position, rating)
            VALUES (?, ?, ?, ?, ?)
        """, (name, nationality, club, position, rating))

    print(f"Player added: {name}")

def show_players():
    with sqlite3.connect(DB_NAME) as db:
        players = db.execute("""
            SELECT id, name, nationality, club, position, rating
            FROM players
            ORDER BY rating DESC
        """).fetchall()

    if not players:
        print("Hozircha futbolchilar yo'q.")
        return

    for p in players:
        print(
            f"ID: {p[0]} | {p[1]} | {p[2]} | "
            f"{p[3]} | Reyting: {p[5]}"
        )

if __name__ == "__main__":
    add_player("Lionel Messi", "Argentina", "Inter Miami", "RWF", 88)
    add_player("Cristiano Ronaldo", "Portugal", "Al Nassr", "CF", 87)
    show_players()
