from pathlib import Path

path = Path("app.html")
source = path.read_text()

start_marker = '      const build = adminText("button", "", "⚙️ BUILD MASTER");'
end_marker = '      const cardsButton = document.createElement("button");'

if source.count(start_marker) != 1 or source.count(end_marker) != 1:
    raise SystemExit("XATO: Kod chegaralari kutilganidek emas. Fayl o‘zgartirilmadi.")

start = source.index(start_marker)
end = source.index(end_marker, start)

replacement = '''      const build = adminText("button", "", "⚙️ BUILD MASTER");
      build.type = "button";
      build.addEventListener("click", () => openBuildMasterEditor(player));

'''

helper_marker = "async function refreshAdminPlayers() {"
if source.count(helper_marker) != 1:
    raise SystemExit("XATO: Yordamchi funksiya joyi topilmadi. Fayl o‘zgartirilmadi.")

helper = r"""
let buildMasterModal = null;

function ensureBuildMasterModal() {
  if (buildMasterModal) return buildMasterModal;

  const style = document.createElement("style");
  style.textContent = `
    #buildMasterModal { position:fixed; inset:0; z-index:9999; display:none;
      align-items:center; justify-content:center; padding:16px;
      background:rgba(0,0,0,.82); overflow:auto; }
    #buildMasterModal .bm-box { width:min(680px,100%); max-height:90vh;
      overflow:auto; padding:20px; border:1px solid #42ff9b;
      border-radius:16px; background:#111923; color:#e8f4ee; }
    #buildMasterModal label { display:block; margin:12px 0 6px; }
    #buildMasterModal select,#buildMasterModal textarea {
      box-sizing:border-box; width:100%; padding:11px; border-radius:8px;
      border:1px solid #49665a; background:#0b1118; color:#fff; font:inherit; }
    #buildMasterModal textarea { min-height:110px; resize:vertical; }
    #buildMasterModal .bm-actions { display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }
    #buildMasterModal button { padding:10px 14px; cursor:pointer; }
    #buildMasterModal [role=status] { overflow-wrap:anywhere; }
  `;
  document.head.appendChild(style);

  const modal = document.createElement("div");
  modal.id = "buildMasterModal";
  modal.innerHTML = `
    <section class="bm-box" role="dialog" aria-modal="true"
      aria-labelledby="bmTitle">
      <h2 id="bmTitle">⚙️ BUILD MASTER</h2>
      <p>Har bir karta uchun alohida ma’lumotlar saqlanadi.</p>
      <label for="bmCard">Karta</label>
      <select id="bmCard"></select>
      <label for="bmStats">Statistika (JSON)</label>
      <textarea id="bmStats" spellcheck="false"
        placeholder='{"Speed":95,"Finishing":90}'></textarea>
      <label for="bmHighlights">Highlights (JSON ro‘yxat)</label>
      <textarea id="bmHighlights" spellcheck="false"
        placeholder='["Bullet Header","Long-Range Curler"]'></textarea>
      <label for="bmTip">Karta uchun maslahat</label>
      <textarea id="bmTip" placeholder="Maslahatni kiriting..."></textarea>
      <p id="bmStatus" role="status" aria-live="polite"></p>
      <div class="bm-actions">
        <button type="button" id="bmSave">💾 Saqlash</button>
        <button type="button" id="bmClose">Yopish</button>
      </div>
    </section>`;
  document.body.appendChild(modal);

  modal.querySelector("#bmClose").addEventListener("click", () => {
    modal.style.display = "none";
  });
  modal.addEventListener("click", event => {
    if (event.target === modal) modal.style.display = "none";
  });
  modal.querySelector("#bmCard").addEventListener("change", () => {
    loadBuildMasterForm().catch(showBuildMasterError);
  });
  modal.querySelector("#bmSave").addEventListener("click", saveBuildMasterForm);

  buildMasterModal = modal;
  return modal;
}

function showBuildMasterError(error) {
  const status = document.querySelector("#buildMasterModal #bmStatus");
  if (status) status.textContent = "Xato: " + error.message;
}

async function openBuildMasterEditor(player) {
  const modal = ensureBuildMasterModal();
  const status = modal.querySelector("#bmStatus");
  const select = modal.querySelector("#bmCard");
  status.textContent = "Kartalar yuklanmoqda...";
  modal.style.display = "flex";

  try {
    const response = await adminRequest(
      `/api/players/${player.id}/cards`
    );
    const cards = Array.isArray(response) ? response : (response.cards || []);
    select.replaceChildren();

    if (!cards.length) {
      const option = document.createElement("option");
      option.textContent = "Avval ushbu futbolchiga karta yarating";
      option.value = "";
      select.appendChild(option);
      status.textContent = "Karta topilmadi. 🃏 KARTALAR tugmasi orqali karta yarating.";
      modal.querySelector("#bmStats").value = "{}";
      modal.querySelector("#bmHighlights").value = "[]";
      modal.querySelector("#bmTip").value = "";
      return;
    }

    for (const card of cards) {
      const option = document.createElement("option");
      option.value = String(card.id);
      option.textContent = `${card.card_name || "Nomsiz karta"} | OVR ${card.rating ?? "?"} | ID ${card.id}`;
      select.appendChild(option);
    }
    status.textContent = "";
    await loadBuildMasterForm();
  } catch (error) {
    status.textContent = "Xato: " + error.message;
  }
}

async function loadBuildMasterForm() {
  const modal = ensureBuildMasterModal();
  const select = modal.querySelector("#bmCard");
  const cardId = select.value;
  if (!cardId) return;

  const status = modal.querySelector("#bmStatus");
  status.textContent = "Saqlangan ma’lumotlar yuklanmoqda...";

  const result = await adminRequest(`/api/cards/${encodeURIComponent(cardId)}/build`);
  const build = result.build || {};
  modal.querySelector("#bmStats").value =
    JSON.stringify(build.stats || {}, null, 2);
  modal.querySelector("#bmHighlights").value =
    JSON.stringify(build.highlights || [], null, 2);
  modal.querySelector("#bmTip").value = build.tip || "";
  status.textContent = build.updated_at
    ? "Mavjud BUILD MASTER yuklandi."
    : "Bu kartada hali BUILD MASTER yo‘q.";
}

async function saveBuildMasterForm() {
  const modal = ensureBuildMasterModal();
  const select = modal.querySelector("#bmCard");
  const cardId = select.value;
  const status = modal.querySelector("#bmStatus");
  const saveButton = modal.querySelector("#bmSave");
  if (!cardId) {
    status.textContent = "Avval karta yarating.";
    return;
  }

  let stats;
  let highlights;
  try {
    stats = JSON.parse(modal.querySelector("#bmStats").value);
    highlights = JSON.parse(modal.querySelector("#bmHighlights").value);
  } catch {
    status.textContent = "JSON formati xato. Qavs va vergullarni tekshiring.";
    return;
  }

  if (!stats || typeof stats !== "object" || Array.isArray(stats) ||
      !Array.isArray(highlights)) {
    status.textContent = "Statistika obyekt, Highlights esa ro‘yxat bo‘lishi kerak.";
    return;
  }

  saveButton.disabled = true;
  status.textContent = "Saqlanmoqda...";
  try {
    await adminRequest(`/api/cards/${encodeURIComponent(cardId)}/build`, {
      method: "POST",
      body: JSON.stringify({
        stats,
        highlights,
        tip: modal.querySelector("#bmTip").value
      })
    });
    status.textContent = "BUILD MASTER muvaffaqiyatli saqlandi.";
    await refreshAdminPlayers();
  } catch (error) {
    status.textContent = "Xato: " + error.message;
  } finally {
    saveButton.disabled = false;
  }
}

"""

source = source[:start] + replacement + source[end:]
source = source.replace(helper_marker, helper + "\n" + helper_marker, 1)
path.write_text(source)
print("MUVAFFAQIYAT: BUILD MASTER modal interfeysi qo‘shildi.")
