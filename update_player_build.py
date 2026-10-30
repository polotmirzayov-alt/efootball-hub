from pathlib import Path

path = Path("screens/player.html")
text = path.read_text()

old = '<div class="grid" id="buildGrid" style="margin-top:10px"></div>'
new = '''<div class="grid" id="buildGrid" style="margin-top:10px"></div>
    <h3 class="section-title">HIGHLIGHTS</h3>
    <div class="badges" id="highlightsGrid"></div>
    <h3 class="section-title">MASLAHAT</h3>
    <p id="buildTip" class="muted">Hali maslahat kiritilmagan.</p>'''

if 'id="highlightsGrid"' in text:
    raise SystemExit("Bu o'zgarish avvaldan mavjud.")
if old not in text:
    raise SystemExit("XATO: buildGrid topilmadi. Fayl o'zgartirilmadi.")

text = text.replace(old, new, 1)
path.write_text(text)
print("1-qadam bajarildi: Highlights va Maslahat joylari qo'shildi.")
