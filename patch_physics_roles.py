from pathlib import Path
import re

p = Path("database/card_details.py")
s = p.read_text()

if "physics TEXT NOT NULL DEFAULT '{}'" in s and "roles TEXT NOT NULL DEFAULT '{}'" in s:
    print("Ustunlar kodda allaqachon bor; hech narsa o'zgartirilmadi.")
    raise SystemExit(0)

# Har ikkala CREATE TABLE ichiga ustunlarni qo'shish.
pattern = r"(                    max_build TEXT NOT NULL DEFAULT '\{\}',\n)(                    source TEXT NOT NULL DEFAULT 'manual',)"
matches = list(re.finditer(pattern, s))
if len(matches) != 2:
    raise SystemExit(f"STOP: 2 ta schema topilishi kerak edi, topildi: {len(matches)}. Fayl o'zgartirilmadi.")

s = re.sub(
    pattern,
    r"\1                    physics TEXT NOT NULL DEFAULT '{}',\n                    roles TEXT NOT NULL DEFAULT '{}',\n\2",
    s
)

marker = '    print("PLAYER CARD DETAILS: jadvallar tayyor.")'
if s.count(marker) != 1:
    raise SystemExit("STOP: migratsiya joyi topilmadi. Fayl o'zgartirilmadi.")

migration = '''    # Eski bazalarga ustunlarni ma'lumotlarni o'chirmasdan qo'shish.
    if use_postgres:
        from database.postgres_db import get_connection
        with get_connection() as db:
            db.execute("""
                ALTER TABLE player_card_details
                ADD COLUMN IF NOT EXISTS physics TEXT NOT NULL DEFAULT '{}'
            """)
            db.execute("""
                ALTER TABLE player_card_details
                ADD COLUMN IF NOT EXISTS roles TEXT NOT NULL DEFAULT '{}'
            """)
    else:
        with sqlite3.connect(db_path) as db:
            columns = {
                row[1] for row in
                db.execute("PRAGMA table_info(player_card_details)").fetchall()
            }
            if "physics" not in columns:
                db.execute(
                    "ALTER TABLE player_card_details "
                    "ADD COLUMN physics TEXT NOT NULL DEFAULT '{}'"
                )
            if "roles" not in columns:
                db.execute(
                    "ALTER TABLE player_card_details "
                    "ADD COLUMN roles TEXT NOT NULL DEFAULT '{}'"
                )

'''
s = s.replace(marker, migration + marker)
p.write_text(s)
print("OK: ikkala schema va xavfsiz migratsiya qo'shildi.")
