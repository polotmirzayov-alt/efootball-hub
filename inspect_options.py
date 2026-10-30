from html.parser import HTMLParser
from pesdb_export import get_html

class SelectParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.target = None
        self.in_option = False
        self.value = ""
        self.text = []
        self.options = {"featured": [], "type": []}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "select":
            name = a.get("name", "")
            self.target = name if name in self.options else None
        elif tag == "option" and self.target:
            self.in_option = True
            self.value = a.get("value", "")
            self.text = []

    def handle_data(self, data):
        if self.in_option:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "option" and self.in_option:
            label = " ".join("".join(self.text).split())
            self.options[self.target].append((self.value, label))
            self.in_option = False
        elif tag == "select":
            self.target = None

html_text = get_html("https://pesdb.net/efootball/players/")
parser = SelectParser()
parser.feed(html_text)

for name, items in parser.options.items():
    print(f"\n=== {name.upper()} VARIANTLARI ===")
    for value, label in items:
        print(f"{label} -> {value}")
