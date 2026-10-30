from html.parser import HTMLParser

page = open("player_test.html", encoding="utf-8").read()

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []

    def handle_data(self, data):
        value = " ".join(data.split())
        if value:
            self.texts.append(value)

parser = TextParser()
parser.feed(page)

print("========== FUTBOLCHI SAHIFASIDAGI MATNLAR ==========")

for text in parser.texts:
    print(text)

