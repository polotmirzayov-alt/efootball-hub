import sqlite3
from schema import create_database, DB_PATH

create_database(DB_PATH)

with sqlite3.connect(DB_PATH) as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS player_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            card_name TEXT NOT NULL DEFAULT '',
            card_type TEXT NOT NULL DEFAULT 'Standard',
            rating INTEGER NOT NULL DEFAULT 0,
            position TEXT NOT NULL DEFAULT '',
            playing_style TEXT NOT NULL DEFAULT '',
            image TEXT NOT NULL DEFAULT '',
            release_date TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual',
            FOREIGN KEY (player_id) REFERENCES players(id)
                ON DELETE CASCADE
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            nationality TEXT NOT NULL DEFAULT '',
            formation TEXT NOT NULL DEFAULT '',
            attacking_style TEXT NOT NULL DEFAULT '',
            defensive_style TEXT NOT NULL DEFAULT '',
            image TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT 'manual'
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS manager_tactics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER NOT NULL,
            tactic_name TEXT NOT NULL DEFAULT '',
            tactic_value TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (manager_id) REFERENCES managers(id)
                ON DELETE CASCADE
        )
    """)

    print("Player cards:", db.execute(
        "SELECT COUNT(*) FROM player_cards"
    ).fetchone()[0])
    print("Managers:", db.execute(
        "SELECT COUNT(*) FROM managers"
    ).fetchone()[0])
    print("Manager tactics:", db.execute(
        "SELECT COUNT(*) FROM manager_tactics"
    ).fetchone()[0])
    print("Existing players:", db.execute(
        "SELECT COUNT(*) FROM players"
    ).fetchone()[0])

print("SUCCESS: New database tables are ready.")
