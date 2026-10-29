from flask import Flask, jsonify, request, send_from_directory, render_template_string
import os
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)

from hub import PLAYERS as HUB_PLAYERS, HTML as HUB_HTML

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

from database.card_details import create_card_details_tables
create_card_details_tables(use_postgres=USE_POSTGRES, db_path=DB_PATH)

from database.card_builds import create_card_build_tables
create_card_build_tables(use_postgres=USE_POSTGRES, db_path=DB_PATH)


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "app.html")


@app.route("/hub", methods=["GET"])
def hub_home():
    selected = request.args.get("player", "ronaldo_bigtime")
    if selected not in HUB_PLAYERS:
        selected = "ronaldo_bigtime"

    player = HUB_PLAYERS[selected]
    try:
        ovr = int(request.args.get("ovr", player["ovr"]))
    except (TypeError, ValueError):
        ovr = player["ovr"]
    ovr = max(0, min(112, ovr))

    tab = request.args.get("tab", "stats")
    if tab not in {"stats", "builds", "skills", "positions"}:
        tab = "stats"

    html = HUB_HTML.replace('action="/"', 'action="/hub"')
    html = html.replace('href="/?player=', 'href="/hub?player=')
    html = html.replace(
        '<footer>',
        '<p style="text-align:center"><a href="/hub/cards">⚽ Bazadagi barcha kartalarni ko‘rish</a></p><footer>',
        1
    )

    return render_template_string(
        html,
        database=HUB_PLAYERS,
        selected=selected,
        player=player,
        ovr=ovr,
        tab=tab
    )



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
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 105:
                return jsonify({"error": "Statistika 0 dan 105 gacha bo'lishi kerak"}), 400
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




def _card_json(value, default):
    try:
        return json.loads(value) if value else default
    except (TypeError, ValueError):
        return default


@app.route("/api/players/<int:player_id>/cards", methods=["GET", "POST"])
def player_cards_api(player_id):
    if request.method == "POST" and not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    try:
        if request.method == "GET":
            if USE_POSTGRES:
                with postgres_db.get_connection() as db:
                    rows = db.execute("""
                        SELECT id, player_id, card_name, card_type, rating,
                               position, playing_style, image, release_date, source
                        FROM player_cards
                        WHERE player_id = %s
                        ORDER BY rating DESC, id DESC
                    """, (player_id,)).fetchall()
            else:
                with sqlite3.connect(DB_PATH) as db:
                    db.row_factory = sqlite3.Row
                    rows = db.execute("""
                        SELECT id, player_id, card_name, card_type, rating,
                               position, playing_style, image, release_date, source
                        FROM player_cards
                        WHERE player_id = ?
                        ORDER BY rating DESC, id DESC
                    """, (player_id,)).fetchall()
            return jsonify([dict(row) for row in rows])

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "JSON ma'lumot yuboring"}), 400

        name = str(data.get("card_name", "")).strip()
        if not name or len(name) > 120:
            return jsonify({"error": "card_name 1–120 belgi bo'lishi kerak"}), 400

        try:
            rating = int(data.get("rating", 0))
        except (TypeError, ValueError):
            return jsonify({"error": "rating son bo'lishi kerak"}), 400
        if not 0 <= rating <= 200:
            return jsonify({"error": "rating 0–200 oralig'ida bo'lishi kerak"}), 400

        values = (
            player_id, name,
            str(data.get("card_type", "Standard"))[:80],
            rating, str(data.get("position", ""))[:30],
            str(data.get("playing_style", ""))[:100],
            str(data.get("image", ""))[:500],
            str(data.get("release_date", ""))[:30],
            str(data.get("source", "manual"))[:80],
        )

        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                player = db.execute(
                    "SELECT id FROM players WHERE id = %s", (player_id,)
                ).fetchone()
                if not player:
                    return jsonify({"error": "Futbolchi topilmadi"}), 404
                row = db.execute("""
                    INSERT INTO player_cards
                    (player_id, card_name, card_type, rating, position,
                     playing_style, image, release_date, source)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id, player_id, card_name, card_type, rating,
                              position, playing_style, image, release_date, source
                """, values).fetchone()
        else:
            with sqlite3.connect(DB_PATH) as db:
                db.row_factory = sqlite3.Row
                player = db.execute(
                    "SELECT id FROM players WHERE id = ?", (player_id,)
                ).fetchone()
                if not player:
                    return jsonify({"error": "Futbolchi topilmadi"}), 404
                cursor = db.execute("""
                    INSERT INTO player_cards
                    (player_id, card_name, card_type, rating, position,
                     playing_style, image, release_date, source)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, values)
                row = db.execute("""
                    SELECT id, player_id, card_name, card_type, rating,
                           position, playing_style, image, release_date, source
                    FROM player_cards WHERE id = ?
                """, (cursor.lastrowid,)).fetchone()
                row = dict(row)

        return jsonify({"message": "Karta yaratildi", "card": dict(row)}), 201
    except Exception:
        app.logger.exception("Karta API xatosi")
        return jsonify({"error": "Karta ma'lumotini saqlab bo'lmadi"}), 500


@app.route("/api/cards/<int:card_id>/details", methods=["GET", "POST"])
def card_details_api(card_id):
    if request.method == "POST" and not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    try:
        if request.method == "GET":
            if USE_POSTGRES:
                with postgres_db.get_connection() as db:
                    row = db.execute("""
                        SELECT * FROM player_card_details WHERE card_id = %s
                    """, (card_id,)).fetchone()
            else:
                with sqlite3.connect(DB_PATH) as db:
                    db.row_factory = sqlite3.Row
                    row = db.execute("""
                        SELECT * FROM player_card_details WHERE card_id = ?
                    """, (card_id,)).fetchone()

            if not row:
                return jsonify({"card_id": card_id, "details": None})
            result = dict(row)
            for key in ("stats", "position_ratings", "skills", "boosters", "max_build", "physics", "roles"):
                result[key] = _card_json(result.get(key), {} if key in
                    ("stats", "position_ratings", "max_build", "physics", "roles") else [])
            return jsonify(result)

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "JSON ma'lumot yuboring"}), 400

        def optional_int(key, minimum, maximum):
            value = data.get(key)
            if value is None or value == "":
                return None
            if isinstance(value, bool):
                raise ValueError(key)
            number = int(value)
            if not minimum <= number <= maximum:
                raise ValueError(key)
            return number

        try:
            base_ovr = optional_int("base_ovr", 0, 112)
            max_ovr = optional_int("max_ovr", 0, 112)
            height = optional_int("height_cm", 50, 260)
            weight = optional_int("weight_kg", 20, 250)
            age = optional_int("age", 10, 100)
        except (ValueError, TypeError):
            return jsonify({"error": "OVR, bo'y, vazn yoki yosh qiymati noto'g'ri"}), 400

        stats = data.get("stats", {})
        positions = data.get("position_ratings", {})
        skills = data.get("skills", [])
        boosters = data.get("boosters", [])
        max_build = data.get("max_build", {})
        physics = data.get("physics", {})
        roles = data.get("roles", {})

        if not isinstance(stats, dict) or len(stats) > 50:
            return jsonify({"error": "stats noto'g'ri"}), 400
        if not isinstance(positions, dict) or len(positions) > 30:
            return jsonify({"error": "position_ratings noto'g'ri"}), 400
        for group in (stats, positions):
            for key, value in group.items():
                if not isinstance(key, str) or not key.strip() or len(key) > 60:
                    return jsonify({"error": "Statistika yoki pozitsiya nomi noto'g'ri"}), 400
                if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 105:
                    return jsonify({"error": "Statistika va pozitsiya qiymatlari 0–105 bo'lishi kerak"}), 400
        if not isinstance(skills, list) or len(skills) > 200 or any(not isinstance(x, str) or len(x) > 100 for x in skills):
            return jsonify({"error": "skills noto'g'ri"}), 400
        if not isinstance(boosters, list) or len(boosters) > 100 or any(not isinstance(x, str) or len(x) > 100 for x in boosters):
            return jsonify({"error": "boosters noto'g'ri"}), 400
        if not isinstance(max_build, dict) or len(max_build) > 50:
            return jsonify({"error": "max_build noto'g'ri"}), 400
        if not isinstance(physics, dict) or len(physics) > 50:
            return jsonify({"error": "physics noto'g'ri"}), 400
        if not isinstance(roles, dict) or len(roles) > 50:
            return jsonify({"error": "roles noto'g'ri"}), 400

        payload = (
            card_id, base_ovr, max_ovr, height, weight, age,
            json.dumps(stats, ensure_ascii=False),
            json.dumps(positions, ensure_ascii=False),
            json.dumps(skills, ensure_ascii=False),
            json.dumps(boosters, ensure_ascii=False),
            json.dumps(max_build, ensure_ascii=False),
            json.dumps(physics, ensure_ascii=False),
            json.dumps(roles, ensure_ascii=False),
            str(data.get("source", "manual"))[:80],
            __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
        )

        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                card = db.execute(
                    "SELECT id FROM player_cards WHERE id = %s", (card_id,)
                ).fetchone()
                if not card:
                    return jsonify({"error": "Karta topilmadi"}), 404
                db.execute("""
                    INSERT INTO player_card_details
                    (card_id, base_ovr, max_ovr, height_cm, weight_kg, age,
                     stats, position_ratings, skills, boosters, max_build, physics, roles, source, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (card_id) DO UPDATE SET
                      base_ovr=EXCLUDED.base_ovr, max_ovr=EXCLUDED.max_ovr,
                      height_cm=EXCLUDED.height_cm, weight_kg=EXCLUDED.weight_kg,
                      age=EXCLUDED.age, stats=EXCLUDED.stats,
                      position_ratings=EXCLUDED.position_ratings,
                      skills=EXCLUDED.skills, boosters=EXCLUDED.boosters,
                      max_build=EXCLUDED.max_build, physics=EXCLUDED.physics,
                      roles=EXCLUDED.roles, source=EXCLUDED.source,
                      updated_at=EXCLUDED.updated_at
                """, payload)
        else:
            with sqlite3.connect(DB_PATH) as db:
                card = db.execute(
                    "SELECT id FROM player_cards WHERE id = ?", (card_id,)
                ).fetchone()
                if not card:
                    return jsonify({"error": "Karta topilmadi"}), 404
                db.execute("""
                    INSERT INTO player_card_details
                    (card_id, base_ovr, max_ovr, height_cm, weight_kg, age,
                     stats, position_ratings, skills, boosters, max_build, physics, roles, source, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(card_id) DO UPDATE SET
                      base_ovr=excluded.base_ovr, max_ovr=excluded.max_ovr,
                      height_cm=excluded.height_cm, weight_kg=excluded.weight_kg,
                      age=excluded.age, stats=excluded.stats,
                      position_ratings=excluded.position_ratings,
                      skills=excluded.skills, boosters=excluded.boosters,
                      max_build=excluded.max_build, physics=excluded.physics,
                      roles=excluded.roles, source=excluded.source,
                      updated_at=excluded.updated_at
                """, payload)

        return jsonify({"message": "Karta tafsilotlari saqlandi", "card_id": card_id}), 200
    except Exception:
        app.logger.exception("Karta tafsilotlari API xatosi")
        return jsonify({"error": "Karta tafsilotlarini saqlab bo'lmadi"}), 500


def _admin_authorized():
    import hmac
    token = os.environ.get("ADMIN_TOKEN", "")
    supplied = request.headers.get("Authorization", "")
    return bool(token) and hmac.compare_digest(supplied, "Bearer " + token)



@app.route("/api/cards/<int:card_id>/build", methods=["GET", "POST"])
def card_build_api(card_id):
    if request.method == "POST" and not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    try:
        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                card = db.execute(
                    "SELECT id FROM player_cards WHERE id = %s", (card_id,)
                ).fetchone()
                if not card:
                    return jsonify({"error": "Karta topilmadi"}), 404

                if request.method == "GET":
                    row = db.execute(
                        "SELECT * FROM player_card_builds WHERE card_id = %s",
                        (card_id,)
                    ).fetchone()
                    if not row:
                        return jsonify({"card_id": card_id, "build": None})
                    result = dict(row)
                else:
                    data = request.get_json(silent=True)
                    if not isinstance(data, dict):
                        return jsonify({"error": "JSON ma'lumot yuboring"}), 400
                    stats = data.get("stats", {})
                    highlights = data.get("highlights", [])
                    tip = data.get("tip", "")
                    if not isinstance(stats, dict) or len(stats) > 50:
                        return jsonify({"error": "stats noto'g'ri"}), 400
                    if not isinstance(highlights, list) or len(highlights) > 50 or any(not isinstance(x, str) or len(x) > 120 for x in highlights):
                        return jsonify({"error": "highlights noto'g'ri"}), 400
                    if not isinstance(tip, str) or len(tip) > 1000:
                        return jsonify({"error": "tip noto'g'ri"}), 400
                    for key, value in stats.items():
                        if not isinstance(key, str) or not key.strip() or len(key) > 60:
                            return jsonify({"error": "Stat nomi noto'g'ri"}), 400
                        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 105:
                            return jsonify({"error": "Stat qiymati 0–105 bo'lishi kerak"}), 400
                    updated = datetime.now().astimezone().isoformat()
                    db.execute("""
                        INSERT INTO player_card_builds
                            (card_id, stats, highlights, tip, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (card_id) DO UPDATE SET
                            stats = EXCLUDED.stats,
                            highlights = EXCLUDED.highlights,
                            tip = EXCLUDED.tip,
                            updated_at = EXCLUDED.updated_at
                    """, (
                        card_id, json.dumps(stats, ensure_ascii=False),
                        json.dumps(highlights, ensure_ascii=False), tip, updated
                    ))
                    return jsonify({"message": "Karta buildi saqlandi", "card_id": card_id}), 200
        else:
            with sqlite3.connect(DB_PATH) as db:
                db.row_factory = sqlite3.Row
                card = db.execute(
                    "SELECT id FROM player_cards WHERE id = ?", (card_id,)
                ).fetchone()
                if not card:
                    return jsonify({"error": "Karta topilmadi"}), 404

                if request.method == "GET":
                    row = db.execute(
                        "SELECT * FROM player_card_builds WHERE card_id = ?",
                        (card_id,)
                    ).fetchone()
                    if not row:
                        return jsonify({"card_id": card_id, "build": None})
                    result = dict(row)
                else:
                    data = request.get_json(silent=True)
                    if not isinstance(data, dict):
                        return jsonify({"error": "JSON ma'lumot yuboring"}), 400
                    stats = data.get("stats", {})
                    highlights = data.get("highlights", [])
                    tip = data.get("tip", "")
                    if not isinstance(stats, dict) or len(stats) > 50:
                        return jsonify({"error": "stats noto'g'ri"}), 400
                    if not isinstance(highlights, list) or len(highlights) > 50 or any(not isinstance(x, str) or len(x) > 120 for x in highlights):
                        return jsonify({"error": "highlights noto'g'ri"}), 400
                    if not isinstance(tip, str) or len(tip) > 1000:
                        return jsonify({"error": "tip noto'g'ri"}), 400
                    for key, value in stats.items():
                        if not isinstance(key, str) or not key.strip() or len(key) > 60:
                            return jsonify({"error": "Stat nomi noto'g'ri"}), 400
                        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 105:
                            return jsonify({"error": "Stat qiymati 0–105 bo'lishi kerak"}), 400
                    updated = datetime.now().astimezone().isoformat()
                    db.execute("""
                        INSERT INTO player_card_builds
                            (card_id, stats, highlights, tip, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(card_id) DO UPDATE SET
                            stats = excluded.stats,
                            highlights = excluded.highlights,
                            tip = excluded.tip,
                            updated_at = excluded.updated_at
                    """, (
                        card_id, json.dumps(stats, ensure_ascii=False),
                        json.dumps(highlights, ensure_ascii=False), tip, updated
                    ))
                    return jsonify({"message": "Karta buildi saqlandi", "card_id": card_id}), 200

        for key, default in (("stats", {}), ("highlights", [])):
            value = result.get(key)
            try:
                result[key] = json.loads(value) if isinstance(value, str) else value
            except (ValueError, TypeError):
                result[key] = default
        return jsonify({"card_id": card_id, "build": result}), 200

    except Exception:
        app.logger.exception("Karta build API xatosi")
        return jsonify({"error": "Karta buildini o'qish yoki saqlash amalga oshmadi"}), 500


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



@app.route("/hub/cards", methods=["GET"])
def hub_cards():
    query = """
        SELECT
            pc.id AS card_id,
            pc.card_name,
            pc.card_type,
            pc.rating AS card_rating,
            pc.position AS card_position,
            pc.playing_style AS card_style,
            pc.image AS card_image,
            pc.release_date,
            p.name AS player_name,
            p.nationality,
            p.club
        FROM player_cards pc
        JOIN players p ON p.id = pc.player_id
        ORDER BY pc.rating DESC, pc.id DESC
    """
    try:
        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                cards = db.execute(query).fetchall()
        else:
            with sqlite3.connect(DB_PATH) as db:
                db.row_factory = sqlite3.Row
                cards = [dict(row) for row in db.execute(query).fetchall()]

        html = """
        <!doctype html>
        <html lang="uz">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>eFootball Hub — Kartalar</title>
          <style>
            body{margin:0;padding:20px;background:#080b13;color:#f4f6ff;
                 font-family:Arial,sans-serif}
            h1{color:#ffd45c}
            .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
            .card{background:#141b2b;border:1px solid #303b52;border-radius:14px;padding:16px}
            .rating{font-size:30px;font-weight:bold;color:#ffd45c}
            .muted{color:#b6c0d4;line-height:1.6}
            a{color:#ffd45c}
            .empty{padding:18px;border:1px dashed #59647a;border-radius:12px}
          </style>
        </head>
        <body>
          <p><a href="/hub">← Eski HUB sahifasi</a></p>
          <h1>⚽ eFootball kartalari</h1>
          <p class="muted">Bazadagi kartalar: {{ cards|length }}</p>
          {% if cards %}
          <div class="grid">
            {% for c in cards %}
            <article class="card">
              <div class="rating">{{ c.card_rating }} OVR</div>
              <h2>{{ c.card_name }}</h2>
              <p class="muted">{{ c.player_name }}</p>
              <p class="muted">{{ c.card_type }} · {{ c.card_position }}</p>
              <p class="muted">{{ c.nationality or 'Millat kiritilmagan' }}<br>
              {{ c.club or 'Klub kiritilmagan' }}<br>
              {{ c.card_style or 'O‘yin uslubi kiritilmagan' }}</p>
              {% if c.release_date %}
              <p class="muted">Chiqarilgan sana: {{ c.release_date }}</p>
              {% endif %}
            </article>
            {% endfor %}
          </div>
          {% else %}
          <div class="empty">Hozircha bazada karta yo‘q.</div>
          {% endif %}
        </body>
        </html>
        """
        return render_template_string(html, cards=cards)
    except Exception:
        app.logger.exception("HUB kartalarini yuklashda xato")
        return jsonify({"error": "Kartalarni yuklab bo‘lmadi"}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8001)),
        debug=False
    )
