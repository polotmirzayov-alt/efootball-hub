from pathlib import Path

path = Path("screens/player.html")
text = path.read_text()

old = '''    <p class="muted">Bu bo‘limda futbolchini kuchaytirish uchun ochkolar taqsimoti qo‘shiladi.</p>'''
new = '''    <p class="muted" id="buildStatus">BUILD MASTER ma’lumotlari yuklanmoqda...</p>'''

if old in text:
    text = text.replace(old, new, 1)
elif 'id="buildStatus"' not in text:
    raise SystemExit("Build holati matni topilmadi. Fayl o'zgartirilmadi.")

start = text.find('    const rating=Number(p.rating)||70;')
end_marker = '    $("buildGrid").innerHTML=[["Dribling",8],["Pas",8],["Zarba",8],["Tezlik",8],["Kuch",4],["Himoya",0]].map(([a,b])=>addStat(a,b)).join("");'
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit("Eski statistika kodi topilmadi. Fayl saqlanmadi.")

end += len(end_marker)

replacement = '''    $("statsGrid").innerHTML =
      '<p class="muted">Batafsil futbolchi statistikasi hali bazaga kiritilmagan.</p>';

    $("buildGrid").innerHTML = "";
    $("highlightsGrid").innerHTML = "";
    $("buildTip").textContent = "Hali maslahat kiritilmagan.";

    try {
      const response = await fetch(`/api/players/${encodeURIComponent(p.id)}/build`);
      if (!response.ok) throw new Error("Build API xatosi");

      const build = await response.json();
      const stats = build.stats || {};
      const entries = Object.entries(stats);

      if (entries.length) {
        $("buildGrid").innerHTML = entries
          .map(([label, value]) => addStat(label, value)).join("");
        $("buildStatus").textContent = "Saqlangan BUILD MASTER statistikasi.";
      } else {
        $("buildStatus").textContent = "Hali build statistikasi saqlanmagan.";
      }

      const highlights = Array.isArray(build.highlights) ? build.highlights : [];
      for (const item of highlights) {
        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = item;
        $("highlightsGrid").appendChild(badge);
      }

      if (!highlights.length) {
        $("highlightsGrid").textContent = "Hali highlights kiritilmagan.";
      }

      $("buildTip").textContent = build.tip || "Hali maslahat kiritilmagan.";
    } catch (error) {
      console.error("BUILD MASTER xatosi:", error);
      $("buildStatus").textContent = "BUILD MASTER ma’lumotlarini yuklab bo‘lmadi.";
      $("highlightsGrid").textContent = "Ma’lumotlar hozircha mavjud emas.";
    }'''

text = text[:start] + replacement + text[end:]
path.write_text(text)
print("2-qadam bajarildi: profil BUILD MASTER API bilan ulandi.")
