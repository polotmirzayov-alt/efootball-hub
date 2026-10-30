import re
from html.parser import HTMLParser
from urllib.parse import urljoin

from pesdb_export import get_html

BASE = "https://pesdb.net"
URL = BASE + "/efootball/players/"


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.forms = []
        self.current_form = None
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a" and attrs.get("href"):
            self.current_link = {
                "href": attrs["href"],
                "text": "",
            }

        if tag == "form":
            self.current_form = {
                "action": attrs.get("action", ""),
                "method": attrs.get("method", "get"),
                "fields": [],
            }

        if tag in ("input", "select", "button") and self.current_form is not None:
            name = attrs.get("name")
            if name:
                self.current_form["fields"].append({
                    "name": name,
                    "type": attrs.get("type", tag),
                    "value": attrs.get("value", ""),
                })

    def handle_data(self, data):
        if self.current_link is not None:
            self.current_link["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link is not None:
            link = self.current_link
            self.links.append((
                link["href"],
                " ".join(link["text"].split()),
            ))
            self.current_link = None

        if tag == "form" and self.current_form is not None:
            self.forms.append(self.current_form)
            self.current_form = None


page = get_html(URL)
parser = PageInspector()
parser.feed(page)

print("=== KARTA TURIGA OID HAVOLALAR ===")

seen = set()

for href, label in parser.links:
    full_url = urljoin(BASE, href)

    if re.search(
        r"featured=|epic|big.?time|show.?time|highlight|trending|potw",
        full_url + " " + label,
        re.I,
    ) and (full_url, label) not in seen:
        seen.add((full_url, label))
        print(label or "(matnsiz havola)", "->", full_url)

print("\n=== FILTRLAR ===")

for form in parser.forms:
    print("Form:", form["method"], urljoin(BASE, form["action"]))
    for field in form["fields"]:
        print(" ", field["name"], "|", field["type"], "|", field["value"])
