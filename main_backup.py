from flask import Flask, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "efootball.db")

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "app.html")

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, "assets"), filename)

@app.route("/api/players")
def players():
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""
            SELECT id, name, nationality, club, position, rating, image
            FROM players
            ORDER BY rating DESC
        """).fetchall()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=False)
