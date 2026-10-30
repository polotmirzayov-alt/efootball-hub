from pathlib import Path

p = Path("main.py")
s = p.read_text()

changes = [
    (
        """("stats", "position_ratings", "skills", "boosters", "max_build")""",
        """("stats", "position_ratings", "skills", "boosters", "max_build", "physics", "roles")"""
    ),
    (
        """("stats", "position_ratings", "max_build") else [])""",
        """("stats", "position_ratings", "max_build", "physics", "roles") else [])"""
    ),
    (
        """        max_build = data.get("max_build", {})""",
        """        max_build = data.get("max_build", {})
        physics = data.get("physics", {})
        roles = data.get("roles", {})"""
    ),
    (
        """        if not isinstance(max_build, dict) or len(max_build) > 50:
            return jsonify({"error": "max_build noto'g'ri"}), 400""",
        """        if not isinstance(max_build, dict) or len(max_build) > 50:
            return jsonify({"error": "max_build noto'g'ri"}), 400
        if not isinstance(physics, dict) or len(physics) > 50:
            return jsonify({"error": "physics noto'g'ri"}), 400
        if not isinstance(roles, dict) or len(roles) > 50:
            return jsonify({"error": "roles noto'g'ri"}), 400"""
    ),
    (
        """            json.dumps(max_build, ensure_ascii=False),
            str(data.get("source", "manual"))[:80],""",
        """            json.dumps(max_build, ensure_ascii=False),
            json.dumps(physics, ensure_ascii=False),
            json.dumps(roles, ensure_ascii=False),
            str(data.get("source", "manual"))[:80],"""
    ),
    (
        """stats, position_ratings, skills, boosters, max_build, source, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        """stats, position_ratings, skills, boosters, max_build, physics, roles, source, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    ),
    (
        """max_build=EXCLUDED.max_build, source=EXCLUDED.source,""",
        """max_build=EXCLUDED.max_build, physics=EXCLUDED.physics,
                      roles=EXCLUDED.roles, source=EXCLUDED.source,"""
    ),
    (
        """stats, position_ratings, skills, boosters, max_build, source, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        """stats, position_ratings, skills, boosters, max_build, physics, roles, source, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    ),
    (
        """max_build=excluded.max_build, source=excluded.source,""",
        """max_build=excluded.max_build, physics=excluded.physics,
                      roles=excluded.roles, source=excluded.source,"""
    ),
]

for old, new in changes:
    count = s.count(old)
    if count != 1:
        raise SystemExit(
            f"STOP: kod bo'lagi {count} marta topildi; "
            "main.py o'zgartirilmadi.\n" + old
        )
    s = s.replace(old, new, 1)

p.write_text(s)
print("OK: physics va roles API kodiga qo'shildi.")
