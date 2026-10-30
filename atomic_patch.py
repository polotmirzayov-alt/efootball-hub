from pathlib import Path

path = Path("main.py")
source = path.read_text(encoding="utf-8")
marker = "\ndef _admin_authorized():"

if "def import_pesdb_card_complete():" in source:
    raise SystemExit("Endpoint allaqachon mavjud. O'zgartirish kiritilmadi.")

if marker not in source:
    raise SystemExit("Joy topilmadi. O'zgartirish kiritilmadi.")

endpoint = r'''

@app.route("/api/import-pesdb-card-complete", methods=["POST"])
def import_pesdb_card_complete():
    if not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON ma'lumot yuboring"}), 400

    card = data.get("card")
    details = data.get("details")
    if not isinstance(card, dict) or not isinstance(details, dict):
        return jsonify({"error": "card va details obyektlari kerak"}), 400

    name = str(card.get("player_name", "")).strip()[:120]
    nationality = str(card.get("nationality", "")).strip()[:80]
    club = str(card.get("club", "")).strip()[:120]
    source_name = str(card.get("source", "PESDB")).strip()[:80] or "PESDB"
    source_id = str(card.get("source_card_id", "")).strip()[:100]
    card_name = str(card.get("card_name", "")).strip()[:120]

    if not all((name, card_name, source_id)):
        return jsonify({"error": "Futbolchi, karta nomi va manba ID majburiy"}), 400

    try:
        rating = int(card.get("rating"))
        if isinstance(card.get("rating"), bool) or not 0 <= rating <= 200:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "OVR noto'g'ri"}), 400

    def optional_int(key, minimum, maximum):
        value = details.get(key)
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
        return jsonify({"error": "Tafsilotlardagi sonli qiymatlar noto'g'ri"}), 400

    stats = details.get("stats", {})
    positions = details.get("position_ratings", {})
    skills = details.get("skills", [])
    boosters = details.get("boosters", [])
    max_build = details.get("max_build", {})
    physics = details.get("physics", {})
    roles = details.get("roles", {})

    if not isinstance(stats, dict) or len(stats) > 50:
        return jsonify({"error": "stats noto'g'ri"}), 400
    if not isinstance(positions, dict) or len(positions) > 30:
        return jsonify({"error": "position_ratings noto'g'ri"}), 400

    for group in (stats, positions):
        for key, value in group.items():
            if not isinstance(key, str) or not key.strip() or len(key) > 60:
                return jsonify({"error": "Stat nomi noto'g'ri"}), 400
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 105:
                return jsonify({"error": "Stat qiymati 0–105 oralig'ida bo'lishi kerak"}), 400

    for values, limit, label in (
        (skills, 200, "skills"),
        (boosters, 100, "boosters"),
    ):
        if not isinstance(values, list) or len(values) > limit:
            return jsonify({"error": label + " noto'g'ri"}), 400
        if any(not isinstance(x, str) or len(x) > 100 for x in values):
            return jsonify({"error": label + " elementlari noto'g'ri"}), 400

    for value, label in (
        (max_build, "max_build"),
        (physics, "physics"),
        (roles, "roles"),
    ):
        if not isinstance(value, dict) or len(value) > 50:
            return jsonify({"error": label + " noto'g'ri"}), 400

    import datetime
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    dump = lambda value: json.dumps(value, ensure_ascii=False)

    try:
        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                existing = db.execute("""
                    SELECT id, player_id, card_name
                    FROM player_cards
                    WHERE source = %s AND source_card_id = %s
                    LIMIT 1
                """, (source_name, source_id)).fetchone()

                if existing:
                    return jsonify({
                        "duplicate": True,
                        "message": "Karta oldin import qilingan",
                        "card": dict(existing)
                    }), 200

                player = db.execute("""
                    SELECT id FROM players
                    WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                      AND LOWER(TRIM(COALESCE(nationality,''))) = LOWER(TRIM(%s))
                      AND LOWER(TRIM(COALESCE(club,''))) = LOWER(TRIM(%s))
                    ORDER BY id LIMIT 1
                """, (name, nationality, club)).fetchone()

                player_created = not bool(player)
                if player:
                    player_id = player["id"]
                else:
                    player_row = db.execute("""
                        INSERT INTO players
                        (name,nationality,club,position,rating,level,
                         playing_style,card_type,image)
                        VALUES (%s,%s,%s,%s,%s,1,%s,%s,%s)
                        RETURNING id
                    """, (
                        name, nationality, club,
                        str(card.get("position", ""))[:30], rating,
                        str(card.get("playing_style", ""))[:100],
                        str(card.get("card_type", "Standard"))[:80],
                        str(card.get("image", ""))[:500]
                    )).fetchone()
                    player_id = player_row["id"]

                row = db.execute("""
                    INSERT INTO player_cards
                    (player_id,card_name,card_type,rating,position,
                     playing_style,image,release_date,source,source_card_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                """, (
                    player_id, card_name,
                    str(card.get("card_type", "Standard"))[:80],
                    rating, str(card.get("position", ""))[:30],
                    str(card.get("playing_style", ""))[:100],
                    str(card.get("image", ""))[:500],
                    str(card.get("release_date", ""))[:30],
                    source_name, source_id
                )).fetchone()
                card_id = row["id"]

                db.execute("""
                    INSERT INTO player_card_details
                    (card_id,base_ovr,max_ovr,height_cm,weight_kg,age,
                     stats,position_ratings,skills,boosters,max_build,
                     physics,roles,source,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    card_id, base_ovr, max_ovr, height, weight, age,
                    dump(stats), dump(positions), dump(skills),
                    dump(boosters), dump(max_build), dump(physics),
                    dump(roles), str(details.get("source", "PESDB"))[:80], now
                ))

        else:
            with sqlite3.connect(DB_PATH) as db:
                db.execute("PRAGMA foreign_keys = ON")
                db.row_factory = sqlite3.Row

                existing = db.execute("""
                    SELECT id,player_id,card_name FROM player_cards
                    WHERE source=? AND source_card_id=? LIMIT 1
                """, (source_name, source_id)).fetchone()

                if existing:
                    return jsonify({
                        "duplicate": True,
                        "message": "Karta oldin import qilingan",
                        "card": dict(existing)
                    }), 200

                player = db.execute("""
                    SELECT id FROM players
                    WHERE LOWER(TRIM(name))=LOWER(TRIM(?))
                      AND LOWER(TRIM(COALESCE(nationality,'')))=LOWER(TRIM(?))
                      AND LOWER(TRIM(COALESCE(club,'')))=LOWER(TRIM(?))
                    ORDER BY id LIMIT 1
                """, (name, nationality, club)).fetchone()

                player_created = not bool(player)
                if player:
                    player_id = player["id"]
                else:
                    cursor = db.execute("""
                        INSERT INTO players
                        (name,nationality,club,position,rating,level,
                         playing_style,card_type,image)
                        VALUES (?,?,?,?,?,1,?,?,?)
                    """, (
                        name, nationality, club,
                        str(card.get("position", ""))[:30], rating,
                        str(card.get("playing_style", ""))[:100],
                        str(card.get("card_type", "Standard"))[:80],
                        str(card.get("image", ""))[:500]
                    ))
                    player_id = cursor.lastrowid

                cursor = db.execute("""
                    INSERT INTO player_cards
                    (player_id,card_name,card_type,rating,position,
                     playing_style,image,release_date,source,source_card_id)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    player_id, card_name,
                    str(card.get("card_type", "Standard"))[:80],
                    rating, str(card.get("position", ""))[:30],
                    str(card.get("playing_style", ""))[:100],
                    str(card.get("image", ""))[:500],
                    str(card.get("release_date", ""))[:30],
                    source_name, source_id
                ))
                card_id = cursor.lastrowid

                db.execute("""
                    INSERT INTO player_card_details
                    (card_id,base_ovr,max_ovr,height_cm,weight_kg,age,
                     stats,position_ratings,skills,boosters,max_build,
                     physics,roles,source,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    card_id, base_ovr, max_ovr, height, weight, age,
                    dump(stats), dump(positions), dump(skills),
                    dump(boosters), dump(max_build), dump(physics),
                    dump(roles), str(details.get("source", "PESDB"))[:80], now
                ))

        return jsonify({
            "message": "Karta va tafsilotlari bitta tranzaksiyada saqlandi",
            "duplicate": False,
            "player_created": player_created,
            "player_id": player_id,
            "card_id": card_id
        }), 201

    except Exception:
        app.logger.exception("Atomik PESDB import xatosi")
        return jsonify({"error": "Import bekor qilindi; tranzaksiya rollback qilindi"}), 500

'''

path.write_text(source.replace(marker, endpoint + marker, 1), encoding="utf-8")
print("Yangi endpoint qo'shildi.")
