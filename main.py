from flask import Flask, jsonify, send_from_directory
import os
import sqlite3

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "efootball.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    from database import postgres_db

    postgres_db.create_tables()
    postgres_db.seed_players()
else:
    from database.schema import create_database

    create_database(DB_PATH)

    def seed_sqlite_players():
        players = [
            (
                "Lionel Messi", "Argentina", "Inter Miami",
                "RWF", 88, ""
            ),
            (
                "Cristiano Ronaldo", "Portugal", "Al Nassr",
                "CF", 95, "/assets/players/ronaldo.png"
            ),
        ]

        with sqlite3.connect(DB_PATH) as db:
            for player in players:
                db.execute("""
                    INSERT INTO players
                        (name, nationality, club, position, rating, image)
                    SELECT ?, ?, ?, ?, ?, ?
                    WHERE NOT EXISTS (
                        SELECT 1 FROM players WHERE name = ?
                    )
                """, player + (player[0],))

    seed_sqlite_players()


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "app.html")


@app.route("/player")
def player_profile():
    return send_from_directory(
        os.path.join(BASE_DIR, "screens"),
        "player.html"
    )


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "assets"),
        filename
    )


@app.route("/api/players")
def players():
    if USE_POSTGRES:
        with postgres_db.get_connection() as db:
            rows = db.execute("""
                SELECT id, name, nationality, club, position, rating,
                       level, playing_style, card_type, image
                FROM players
                ORDER BY rating DESC
            """).fetchall()

        return jsonify(rows)

    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""
            SELECT id, name, nationality, club, position, rating,
                   level, playing_style, card_type, image
            FROM players
            ORDER BY rating DESC
        """).fetchall()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8001)),
        debug=False
    )
