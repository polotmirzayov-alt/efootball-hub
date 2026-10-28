import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "efootball.db")


def create_database(db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                nationality TEXT DEFAULT '',
                club TEXT DEFAULT '',
                position TEXT DEFAULT '',
                rating INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                playing_style TEXT DEFAULT '',
                card_type TEXT DEFAULT 'Standard',
                image TEXT DEFAULT ''
            )
        """)

        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(players)")
        }

        if "image" not in columns:
            connection.execute(
                "ALTER TABLE players ADD COLUMN image TEXT DEFAULT ''"
            )

    print("Player database created successfully.")


if __name__ == "__main__":
    create_database()
