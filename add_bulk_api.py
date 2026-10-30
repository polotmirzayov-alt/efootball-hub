from pathlib import Path

path = Path("main.py")
source = path.read_text(encoding="utf-8")
marker = "\ndef _admin_authorized():"

if '@app.route("/api/import-pesdb-cards-bulk"' in source:
    raise SystemExit("Bulk API allaqachon mavjud. To'xtatildi.")

if marker not in source:
    raise SystemExit("API joyi topilmadi. To'xtatildi.")

route = r'''
@app.route("/api/import-pesdb-cards-bulk", methods=["POST"])
def import_pesdb_cards_bulk():
    if not _admin_authorized():
        return jsonify({"error": "Ruxsat berilmadi"}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON obyekt kerak"}), 400

    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        return jsonify({"error": "items 1–100 ta karta bo'lishi kerak"}), 400

    prepared = []
    seen_ids = set()

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return jsonify({"error": f"{index + 1}-karta noto'g'ri"}), 400

        card, details = item.get("card"), item.get("details")
        if not isinstance(card, dict) or not isinstance(details, dict):
            return jsonify({"error": f"{index + 1}-kartada card/details kerak"}), 400

        name = str(card.get("player_name", "")).strip()[:120]
        nationality = str(card.get("nationality", "")).strip()[:80]
        club = str(card.get("club", "")).strip()[:120]
        source_name = str(card.get("source", "PESDB")).strip()[:80] or "PESDB"
        source_id = str(card.get("source_card_id", "")).strip()[:100]
        card_name = str(card.get("card_name", "")).strip()[:120]

        if not all((name, card_name, source_id)):
            return jsonify({"error": f"{index + 1}-kartada majburiy maydon yo'q"}), 400

        identity = (source_name.casefold(), source_id.casefold())
        if identity in seen_ids:
            return jsonify({"error": f"JSON ichida takroriy source ID: {source_id}"}), 400
        seen_ids.add(identity)

        try:
            rating = card.get("rating")
            if isinstance(rating, bool):
                raise ValueError()
            rating = int(rating)
            if not 0 <= rating <= 200:
                raise ValueError()

            def optional_int(key, low, high):
                value = details.get(key)
                if value is None or value == "":
                    return None
                if isinstance(value, bool):
                    raise ValueError(key)
                number = int(value)
                if not low <= number <= high:
                    raise ValueError(key)
                return number

            base_ovr = optional_int("base_ovr", 0, 112)
            max_ovr = optional_int("max_ovr", 0, 112)
            height = optional_int("height_cm", 50, 260)
            weight = optional_int("weight_kg", 20, 250)
            age = optional_int("age", 10, 100)
        except (TypeError, ValueError):
            return jsonify({"error": f"{index + 1}-kartadagi sonli qiymat noto'g'ri"}), 400

        stats = details.get("stats", {})
        positions = details.get("position_ratings", {})
        skills = details.get("skills", [])
        boosters = details.get("boosters", [])
        max_build = details.get("max_build", {})
        physics = details.get("physics", {})
        roles = details.get("roles", {})

        if not isinstance(stats, dict) or len(stats) > 50:
            return jsonify({"error": f"{index + 1}-karta stats noto'g'ri"}), 400
        if not isinstance(positions, dict) or len(positions) > 30:
            return jsonify({"error": f"{index + 1}-karta position_ratings noto'g'ri"}), 400

        for group in (stats, positions):
            for key, value in group.items():
                if not isinstance(key, str) or not key.strip() or len(key) > 60:
                    return jsonify({"error": "Stat nomi noto'g'ri"}), 400
                if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 105:
                    return jsonify({"error": "Stat qiymati 0–105 oralig'ida bo'lishi kerak"}), 400

        for values, limit, label in ((skills, 200, "skills"), (boosters, 100, "boosters")):
            if not isinstance(values, list) or len(values) > limit:
                return jsonify({"error": f"{label} noto'g'ri"}), 400
            if any(not isinstance(x, str) or len(x) > 100 for x in values):
                return jsonify({"error": f"{label} elementlari noto'g'ri"}), 400

        for value, label in ((max_build, "max_build"), (physics, "physics"), (roles, "roles")):
            if not isinstance(value, dict) or len(value) > 50:
                return jsonify({"error": f"{label} noto'g'ri"}), 400

        prepared.append({
            "name": name, "nationality": nationality, "club": club,
            "source": source_name, "source_id": source_id,
            "card_name": card_name, "rating": rating, "card": card,
            "base_ovr": base_ovr, "max_ovr": max_ovr,
            "height": height, "weight": weight, "age": age,
            "stats": stats, "positions": positions, "skills": skills,
            "boosters": boosters, "max_build": max_build,
            "physics": physics, "roles": roles,
            "detail_source": str(details.get("source", "PESDB"))[:80]
        })

    import datetime
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    dump = lambda value: json.dumps(value, ensure_ascii=False)
    results = []
    player_cache = {}

    try:
        if USE_POSTGRES:
            with postgres_db.get_connection() as db:
                for p in prepared:
                    existing = db.execute(
                        "SELECT id FROM player_cards WHERE source=%s AND source_card_id=%s LIMIT 1",
                        (p["source"], p["source_id"])
                    ).fetchone()
                    if existing:
                        raise ValueError("Karta bazada mavjud: " + p["source_id"])

                    key = (p["name"].casefold(), p["nationality"].casefold(), p["club"].casefold())
                    player_id = player_cache.get(key)
                    created = False

                    if player_id is None:
                        player = db.execute("""
                            SELECT id FROM players
                            WHERE LOWER(TRIM(name))=LOWER(TRIM(%s))
                            AND LOWER(TRIM(COALESCE(nationality,'')))=LOWER(TRIM(%s))
                            AND LOWER(TRIM(COALESCE(club,'')))=LOWER(TRIM(%s))
                            ORDER BY id LIMIT 1
                        """, (p["name"], p["nationality"], p["club"])).fetchone()

                        if player:
                            player_id = player["id"]
                        else:
                            c = p["card"]
                            player = db.execute("""
                                INSERT INTO players
                                (name,nationality,club,position,rating,level,playing_style,card_type,image)
                                VALUES (%s,%s,%s,%s,%s,1,%s,%s,%s) RETURNING id
                            """, (
                                p["name"], p["nationality"], p["club"],
                                str(c.get("position", ""))[:30], p["rating"],
                                str(c.get("playing_style", ""))[:100],
                                str(c.get("card_type", "Standard"))[:80],
                                str(c.get("image", ""))[:500]
                            )).fetchone()
                            player_id, created = player["id"], True
                        player_cache[key] = player_id

                    c = p["card"]
                    row = db.execute("""
                        INSERT INTO player_cards
                        (player_id,card_name,card_type,rating,position,playing_style,image,release_date,source,source_card_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                    """, (
                        player_id, p["card_name"], str(c.get("card_type", "Standard"))[:80],
                        p["rating"], str(c.get("position", ""))[:30],
                        str(c.get("playing_style", ""))[:100], str(c.get("image", ""))[:500],
                        str(c.get("release_date", ""))[:30], p["source"], p["source_id"]
                    )).fetchone()
                    card_id = row["id"]

                    db.execute("""
                        INSERT INTO player_card_details
                        (card_id,base_ovr,max_ovr,height_cm,weight_kg,age,stats,position_ratings,skills,boosters,max_build,physics,roles,source,updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        card_id, p["base_ovr"], p["max_ovr"], p["height"], p["weight"], p["age"],
                        dump(p["stats"]), dump(p["positions"]), dump(p["skills"]), dump(p["boosters"]),
                        dump(p["max_build"]), dump(p["physics"]), dump(p["roles"]), p["detail_source"], now
                    ))
                    results.append({"player_id": player_id, "card_id": card_id, "player_created": created})

        else:
            with sqlite3.connect(DB_PATH) as db:
                db.execute("PRAGMA foreign_keys=ON")
                db.row_factory = sqlite3.Row

                for p in prepared:
                    existing = db.execute(
                        "SELECT id FROM player_cards WHERE source=? AND source_card_id=? LIMIT 1",
                        (p["source"], p["source_id"])
                    ).fetchone()
                    if existing:
                        raise ValueError("Karta bazada mavjud: " + p["source_id"])

                    key = (p["name"].casefold(), p["nationality"].casefold(), p["club"].casefold())
                    player_id = player_cache.get(key)
                    created = False

                    if player_id is None:
                        player = db.execute("""
                            SELECT id FROM players
                            WHERE LOWER(TRIM(name))=LOWER(TRIM(?))
                            AND LOWER(TRIM(COALESCE(nationality,'')))=LOWER(TRIM(?))
                            AND LOWER(TRIM(COALESCE(club,'')))=LOWER(TRIM(?))
                            ORDER BY id LIMIT 1
                        """, (p["name"], p["nationality"], p["club"])).fetchone()

                        if player:
                            player_id = player["id"]
                        else:
                            c = p["card"]
                            cur = db.execute("""
                                INSERT INTO players
                                (name,nationality,club,position,rating,level,playing_style,card_type,image)
                                VALUES (?,?,?,?,?,1,?,?,?)
                            """, (
                                p["name"], p["nationality"], p["club"],
                                str(c.get("position", ""))[:30], p["rating"],
                                str(c.get("playing_style", ""))[:100],
                                str(c.get("card_type", "Standard"))[:80],
                                str(c.get("image", ""))[:500]
                            ))
                            player_id, created = cur.lastrowid, True
                        player_cache[key] = player_id

                    c = p["card"]
                    cur = db.execute("""
                        INSERT INTO player_cards
                        (player_id,card_name,card_type,rating,position,playing_style,image,release_date,source,source_card_id)
                        VALUES (?,?,?,?,?,?,?,?,?,?)
                    """, (
                        player_id, p["card_name"], str(c.get("card_type", "Standard"))[:80],
                        p["rating"], str(c.get("position", ""))[:30],
                        str(c.get("playing_style", ""))[:100], str(c.get("image", ""))[:500],
                        str(c.get("release_date", ""))[:30], p["source"], p["source_id"]
                    ))
                    card_id = cur.lastrowid

                    db.execute("""
                        INSERT INTO player_card_details
                        (card_id,base_ovr,max_ovr,height_cm,weight_kg,age,stats,position_ratings,skills,boosters,max_build,physics,roles,source,updated_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        card_id, p["base_ovr"], p["max_ovr"], p["height"], p["weight"], p["age"],
                        dump(p["stats"]), dump(p["positions"]), dump(p["skills"]), dump(p["boosters"]),
                        dump(p["max_build"]), dump(p["physics"]), dump(p["roles"]), p["detail_source"], now
                    ))
                    results.append({"player_id": player_id, "card_id": card_id, "player_created": created})

        return jsonify({"message": "Bulk import muvaffaqiyatli", "imported_cards": len(results), "results": results}), 201

    except ValueError as exc:
        return jsonify({"error": str(exc), "rolled_back": True}), 409
    except Exception:
        app.logger.exception("PESDB bulk import xatosi")
        return jsonify({"error": "Bulk import bekor qilindi; tranzaksiya rollback qilindi"}), 500
'''

path.write_text(source.replace(marker, route + marker, 1), encoding="utf-8")
print("Bulk API main.py ga qo'shildi.")
