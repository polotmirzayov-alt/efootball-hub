import json
import urllib.request
from html.parser import HTMLParser

data = json.load(open("potw_cards.json", encoding="utf-8"))
player = data["cards"][0]

print("Futbolchi:", player["name"])
print("ID:", player["featured_id"])

req = urllib.request.Request(
    player["player_url"],
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(req, timeout=30) as r:
    page = r.read().decode("utf-8", "replace")

open("player_test.html", "w", encoding="utf-8").write(page)

print("HTML hajmi:", len(page))

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_row = False
        self.in_cell = False
        self.rows = []
        self.row = []
        self.cell = ""

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_row = True
            self.row = []
        elif tag in ("td", "th") and self.in_row:
            self.in_cell = True
            self.cell = ""

    def handle_data(self, data):
        if self.in_cell:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            self.row.append(" ".join(self.cell.split()))
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if self.row:
                self.rows.append(self.row)
            self.in_row = False

parser = TableParser()
parser.feed(page)

print("\n========== JADVAL MA'LUMOTLARI ==========")

for row in parser.rows[:50]:
    print(" | ".join(row))

print("\nHTML player_test.html fayliga saqlandi.")
print("TEKSHIRUV TUGADI")
