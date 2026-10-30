from flask import Flask, jsonify, request, send_from_directory
import os
import json
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
    from database.add_content_tables import create_content_tables
    create_content_tables()
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


from database.build_master_tables import create_build_master_tables
create_build_master_tables(use_postgres=USE_POSTGRES, db_path=DB_PATH)


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


@app.route("/api/import-player", methods=["POST"])
def import_player():
    import hmac

    if not USE_POSTGRES:
        return jsonify({"error": "PostgreSQL talab qilinadi"}), 503

    token = os.environ.get("ADMIN_TOKEN", "")
    supplied = request.headers.get("Authorization", "")
    if not token or not hmac.compare_digest(
        supplied, "Bearer " + token
    ):
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON ma'lumot yuboring"}), 400

    efootball_id = str(data.get("efootball_id", "")).strip()
    name = str(data.get("name", "")).strip()

    if not efootball_id.isdigit() or not name:
        return jsonify({
            "error": "efootball_id raqam, name esa bo'sh bo'lmasin"
        }), 400

    if len(efootball_id) > 30 or len(name) > 120:
        return jsonify({"error": "Maydon uzunligi oshib ketdi"}), 400

    try:
        rating = int(data.get("rating", 0))
        level = int(data.get("level", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "rating va level son bo'lishi kerak"}), 400

    if not 0 <= rating <= 200 or not 1 <= level <= 100:
        return jsonify({"error": "rating yoki level chegaradan tashqarida"}), 400

    player = {
        "efootball_id": efootball_id,
        "name": name,
        "nationality": str(data.get("nationality", ""))[:80],
        "club": str(data.get("club", ""))[:120],
        "position": str(data.get("position", ""))[:30],
        "rating": rating,
        "level": level,
        "playing_style": str(data.get("playing_style", ""))[:100],
        "card_type": str(data.get("card_type", "Standard"))[:80],
        "image": str(data.get("image", ""))[:500],
    }

    try:
        with postgres_db.get_connection() as db:
            existing = db.execute(
                "SELECT id FROM players WHERE efootball_id = %s",
                (efootball_id,)
            ).fetchone()

            if existing:
                return jsonify({"error": "Bu eFootball ID oldin saqlangan"}), 409

            row = db.execute("""
                INSERT INTO players
                    (efootball_id, name, nationality, club, position,
                     rating, level, playing_style, card_type, image)
                VALUES
                    (%(efootball_id)s, %(name)s, %(nationality)s, %(club)s,
                     %(position)s, %(rating)s, %(level)s, %(playing_style)s,
                     %(card_type)s, %(image)s)
                RETURNING id, efootball_id, name
            """, player).fetchone()

        return jsonify({"message": "Futbolchi saqlandi", "player": row}), 201
    except Exception:
        app.logger.exception("Futbolchini saqlashda xato")
        return jsonify({"error": "Bazaga saqlash amalga oshmadi"}), 500


@app.route("/api/players/<int:player_id>/build", methods=["GET", "POST"])
def player_build(player_id):
    if request.method == "POST":
        import hmac

        token = os.environ.get("ADMIN_TOKEN", "")
        supplied = request.headers.get("Authorization", "")
        if not token or not hmac.compare_digest(
            supplied, "Bearer " + token
        ):
            return jsonify({"error": "Ruxsat berilmadi"}), 401

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "JSON ma'lumot yuboring"}), 400

        stats = data.get("stats", {})
        highlights = data.get("highlights", [])
        tip = data.get("tip", "")

        if not isinstance(stats, dict) or len(stats) > 20:
            return jsonify({"error": "Statistika formati noto'g'ri"}), 400
        if not isinstance(highlights, list) or len(highlights) > 10:
            return jsonify({"error": "Xususiyatlar formati noto'g'ri"}), 400
        if not isinstance(tip, str) or len(tip) > 500:
            return jsonify({"error": "Maslahat uzunligi noto'g'ri"}), 400

        clean_stats = {}
        for label, value in stats.items():
            if not isinstance(label, str) or not label.strip() or len(label) > 50:
                return jsonify({"error": "Statistika nomi noto'g'ri"}), 400
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 99:
                return jsonify({"error": "Statistika 0 dan 99 gacha bo'lishi kerak"}), 400
            clean_stats[label.strip()] = value

        if any(not isinstance(item, str) or len(item) > 150 for item in highlights):
            return jsonify({"error": "Xususiyatlardan biri noto'g'ri"}), 400

        stats_json = json.dumps(clean_stats, ensure_ascii=False)
        highlights_json = json.dumps(highlights, ensure_ascii=False)
        updated_at = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat()

        try:
            if USE_POSTGRES:
                with postgres_db.get_connection() as db:
                    player = db.execute(
                        "SELECT id FROM players WHERE id = %s", (player_id,)
                    ).fetchone()
                    if not player:
                        return jsonify({"error": "Futbolchi topilmadi"}), 404

                    db.execute("""
                        INSERT INTO player_builds
                            (player_id, stats, highlights, tip, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (player_id) DO UPDATE SET
                            stats = EXCLUDED.stats,
                            highlights = EXCLUDED.highlights,
                            tip = EXCLUDED.tip,
                            updated_at = EXCLUDED.updated_at
                    """, (player_id, stats_json, highlights_json, tip, updated_at))
            else:
                with sqlite3.connect(DB_PATH) as db:
                    player = db.execute(
                        "SELECT id FROM players WHERE id = ?", (player_id,)
                    ).fetchone()
                    if not player:
                        return jsonify({"error": "Futbolchi topilmadi"}), 404

                    db.execute("""
                        INSERT INTO player_builds
                            (player_id, stats, highlights, tip, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(player_id) DO UPDATE SET
                            stats = excluded.stats,
                            highlights = excluded.highlights,
                            tip = excluded.tip,
                            updated_at = excluded.updated_at
                    """, (player_id, stats_json, highlights_json, tip, updated_at))

            return jsonify({"message": "BUILD MASTER ma'lumotlari saqlandi"}), 200
        except Exception:
            app.logger.exception("BUILD MASTER ma'lumotlarini saqlashda xato")
            return jsonify({"error": "Ma'lumotlarni saqlab bo'lmadi"}), 500

    try:
        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                row = db.execute("""
                    SELECT stats, highlights, tip, updated_at
                    FROM player_builds WHERE player_id = %s
                """, (player_id,)).fetchone()
        else:
            with sqlite3.connect(DB_PATH) as db:
                db.row_factory = sqlite3.Row
                row = db.execute("""
                    SELECT stats, highlights, tip, updated_at
                    FROM player_builds WHERE player_id = ?
                """, (player_id,)).fetchone()

        if not row:
            return jsonify({
                "player_id": player_id,
                "stats": {},
                "highlights": [],
                "tip": "",
                "updated_at": ""
            })

        result = dict(row)
        result["stats"] = json.loads(result["stats"])
        result["highlights"] = json.loads(result["highlights"])
        result["player_id"] = player_id
        return jsonify(result)
    except Exception:
        app.logger.exception("BUILD MASTER ma'lumotlarini olishda xato")
        return jsonify({"error": "Ma'lumotlarni olib bo'lmadi"}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8001)),
        debug=False
    )
