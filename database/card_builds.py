import sqlite3


def create_card_build_tables(use_postgres=False, db_path=None):
    if use_postgres:
        from database.postgres_db import get_connection

        with get_connection() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS player_card_builds (
                    card_id BIGINT PRIMARY KEY
                        REFERENCES player_cards(id) ON DELETE CASCADE,
                    stats TEXT NOT NULL DEFAULT '{}',
                    highlights TEXT NOT NULL DEFAULT '[]',
                    tip TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT ''
                )
            """)
    else:
        if not db_path:
            raise ValueError("SQLite uchun db_path kerak")

        with sqlite3.connect(db_path) as db:
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("""
                CREATE TABLE IF NOT EXISTS player_card_builds (
                    card_id INTEGER PRIMARY KEY
                        REFERENCES player_cards(id) ON DELETE CASCADE,
                    stats TEXT NOT NULL DEFAULT '{}',
                    highlights TEXT NOT NULL DEFAULT '[]',
                    tip TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT ''
                )
            """)

    print("CARD BUILD MASTER: jadval tayyor.")
