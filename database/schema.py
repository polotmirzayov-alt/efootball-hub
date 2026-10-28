import sqlite3

def create_database(db_path="efootball.db"):
    connection = sqlite3.connect(db_path)

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
            card_type TEXT DEFAULT 'Standard'
        )
    """)

    connection.commit()
    connection.close()
    print("Player database created successfully.")

if __name__ == "__main__":
    create_database()
