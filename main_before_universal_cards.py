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



def _admin_authorized():
    import hmac
    token = os.environ.get("ADMIN_TOKEN", "")
    supplied = request.headers.get("Authorization", "")
    return bool(token) and hmac.compare_digest(supplied, "Bearer " + token)


@app.route("/api/admin/players", methods=["GET", "POST"])
def admin_players():
    if not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    if request.method == "GET":
        query = request.args.get("q", "").strip()[:120]
        try:
            if USE_POSTGRES:
                with postgres_db.get_connection() as db:
                    rows = db.execute("""
                        SELECT id, name, nationality, club, position,
                               rating, level, playing_style, card_type, image
                        FROM players
                        WHERE name ILIKE %s OR club ILIKE %s
                        ORDER BY rating DESC, name ASC
                        LIMIT 200
                    """, (f"%{query}%", f"%{query}%")).fetchall()
            else:
                with sqlite3.connect(DB_PATH) as db:
                    db.row_factory = sqlite3.Row
                    rows = db.execute("""
                        SELECT id, name, nationality, club, position,
                               rating, level, playing_style, card_type, image
                        FROM players
                        WHERE name LIKE ? OR club LIKE ?
                        ORDER BY rating DESC, name ASC
                        LIMIT 200
                    """, (f"%{query}%", f"%{query}%")).fetchall()
            return jsonify([dict(row) for row in rows])
        except Exception:
            app.logger.exception("Admin futbolchilar ro‘yxatida xato")
            return jsonify({"error": "Ro‘yxatni olib bo‘lmadi"}), 500

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON ma'lumot yuboring"}), 400

    name = str(data.get("name", "")).strip()
    if not name or len(name) > 120:
        return jsonify({"error": "Futbolchi ismi 1–120 belgidan iborat bo‘lsin"}), 400

    try:
        rating = int(data.get("rating", 0))
        level = int(data.get("level", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Rating va level son bo‘lishi kerak"}), 400

    if not 0 <= rating <= 200 or not 1 <= level <= 100:
        return jsonify({"error": "Rating 0–200, level 1–100 oralig‘ida bo‘lsin"}), 400

    player = (
        name,
        str(data.get("nationality", ""))[:80],
        str(data.get("club", ""))[:120],
        str(data.get("position", ""))[:30],
        rating,
        level,
        str(data.get("playing_style", ""))[:100],
        str(data.get("card_type", "Standard"))[:80],
        str(data.get("image", ""))[:500],
    )
    columns = "name, nationality, club, position, rating, level, playing_style, card_type, image"

    try:
        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                row = db.execute(
                    f"INSERT INTO players ({columns}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id, name",
                    player,
                ).fetchone()
        else:
            with sqlite3.connect(DB_PATH) as db:
                cursor = db.execute(
                    f"INSERT INTO players ({columns}) VALUES (?,?,?,?,?,?,?,?,?)",
                    player,
                )
                row = {"id": cursor.lastrowid, "name": name}

        return jsonify({"message": "Futbolchi qo‘shildi", "player": dict(row)}), 201
    except Exception:
        app.logger.exception("Admin futbolchi qo‘shishda xato")
        return jsonify({"error": "Futbolchini saqlab bo‘lmadi"}), 500


@app.route("/api/admin/players/<int:player_id>", methods=["PATCH", "DELETE"])
def admin_player_detail(player_id):
    if not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    if request.method == "DELETE":
        try:
            if USE_POSTGRES:
                with postgres_db.get_connection() as db:
                    row = db.execute(
                        "DELETE FROM players WHERE id = %s RETURNING id", (player_id,)
                    ).fetchone()
            else:
                with sqlite3.connect(DB_PATH) as db:
                    db.execute("DELETE FROM player_builds WHERE player_id = ?", (player_id,))
                    cursor = db.execute("DELETE FROM players WHERE id = ?", (player_id,))
                    row = {"id": player_id} if cursor.rowcount else None

            if not row:
                return jsonify({"error": "Futbolchi topilmadi"}), 404
            return jsonify({"message": "Futbolchi o‘chirildi", "id": player_id})
        except Exception:
            app.logger.exception("Admin futbolchi o‘chirishda xato")
            return jsonify({"error": "Futbolchini o‘chirib bo‘lmadi"}), 500

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON ma'lumot yuboring"}), 400

    allowed = {
        "name": ("name", 120), "nationality": ("nationality", 80),
        "club": ("club", 120), "position": ("position", 30),
        "playing_style": ("playing_style", 100),
        "card_type": ("card_type", 80), "image": ("image", 500),
    }
    updates = {}
    for key, (column, max_len) in allowed.items():
        if key in data:
            value = str(data[key]).strip()
            if len(value) > max_len or (key == "name" and not value):
                return jsonify({"error": f"{key} maydoni noto‘g‘ri"}), 400
            updates[column] = value

    for key in ("rating", "level"):
        if key in data:
            try:
                value = int(data[key])
            except (TypeError, ValueError):
                return jsonify({"error": f"{key} son bo‘lishi kerak"}), 400
            low, high = (0, 200) if key == "rating" else (1, 100)
            if not low <= value <= high:
                return jsonify({"error": f"{key} chegaradan tashqarida"}), 400
            updates[key] = value

    if not updates:
        return jsonify({"error": "Tahrirlash uchun maydon yuboring"}), 400

    try:
        if USE_POSTGRES:
            assignments = ", ".join(f"{key} = %s" for key in updates)
            values = list(updates.values()) + [player_id]
            with postgres_db.get_connection() as db:
                row = db.execute(
                    f"UPDATE players SET {assignments} WHERE id = %s RETURNING id, name",
                    values,
                ).fetchone()
        else:
            assignments = ", ".join(f"{key} = ?" for key in updates)
            values = list(updates.values()) + [player_id]
            with sqlite3.connect(DB_PATH) as db:
                cursor = db.execute(
                    f"UPDATE players SET {assignments} WHERE id = ?", values
                )
                row = {"id": player_id, "name": updates.get("name", "")} if cursor.rowcount else None

        if not row:
            return jsonify({"error": "Futbolchi topilmadi"}), 404
        return jsonify({"message": "Futbolchi yangilandi", "player": dict(row)})
    except Exception:
        app.logger.exception("Admin futbolchi tahrirlashda xato")
        return jsonify({"error": "Futbolchini yangilab bo‘lmadi"}), 500


@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    if not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401
    try:
        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                row = db.execute("""
                    SELECT
                        (SELECT COUNT(*) FROM players) AS players,
                        (SELECT COUNT(*) FROM player_builds) AS builds
                """).fetchone()
        else:
            with sqlite3.connect(DB_PATH) as db:
                db.row_factory = sqlite3.Row
                row = db.execute("""
                    SELECT
                        (SELECT COUNT(*) FROM players) AS players,
                        (SELECT COUNT(*) FROM player_builds) AS builds
                """).fetchone()
        return jsonify({"players": row["players"], "builds": row["builds"]})
    except Exception:
        app.logger.exception("Admin statistikasida xato")
        return jsonify({"error": "Statistikani olib bo‘lmadi"}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8001)),
        debug=False
    )
