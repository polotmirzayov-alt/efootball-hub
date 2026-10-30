
const translations = {
  uz:{subtitle:"Futbolchilar dunyosi — barchasi bir joyda!",heading:"⚽ Futbolchilar",players:"Futbolchilar",rating:"Eng yuqori OVR",languages:"Tillar",search:"Futbolchi qidirish...",nationality:"Millati",club:"Klub",position:"Pozitsiya",ratingText:"Reyting",empty:"Futbolchi topilmadi",standard:"Oddiy"},
  en:{subtitle:"The world of footballers — all in one place!",heading:"⚽ Players",players:"Players",rating:"Highest OVR",languages:"Languages",search:"Search players...",nationality:"Nationality",club:"Club",position:"Position",ratingText:"Rating",empty:"No players found",standard:"Standard"},
  ru:{subtitle:"Мир футболистов — всё в одном месте!",heading:"⚽ Футболисты",players:"Футболисты",rating:"Максимальный OVR",languages:"Языки",search:"Поиск футболиста...",nationality:"Страна",club:"Клуб",position:"Позиция",ratingText:"Рейтинг",empty:"Футболисты не найдены",standard:"Стандарт"},
  pt:{subtitle:"O mundo do futebol — tudo em um só lugar!",heading:"⚽ Jogadores",players:"Jogadores",rating:"Maior OVR",languages:"Idiomas",search:"Pesquisar jogadores...",nationality:"Nacionalidade",club:"Clube",position:"Posição",ratingText:"Nota",empty:"Nenhum jogador encontrado",standard:"Padrão"},
  es:{subtitle:"El mundo del fútbol, todo en un solo lugar!",heading:"⚽ Jugadores",players:"Jugadores",rating:"OVR más alto",languages:"Idiomas",search:"Buscar jugadores...",nationality:"Nacionalidad",club:"Club",position:"Posición",ratingText:"Valoración",empty:"No se encontraron jugadores",standard:"Estándar"},
  fr:{subtitle:"Le monde du football, tout au même endroit !",heading:"⚽ Joueurs",players:"Joueurs",rating:"OVR maximum",languages:"Langues",search:"Rechercher un joueur...",nationality:"Nationalité",club:"Club",position:"Poste",ratingText:"Note",empty:"Aucun joueur trouvé",standard:"Standard"},
  de:{subtitle:"Die Welt des Fußballs — alles an einem Ort!",heading:"⚽ Spieler",players:"Spieler",rating:"Höchster OVR",languages:"Sprachen",search:"Spieler suchen...",nationality:"Nationalität",club:"Verein",position:"Position",ratingText:"Bewertung",empty:"Keine Spieler gefunden",standard:"Standard"},
  it:{subtitle:"Il mondo del calcio, tutto in un unico posto!",heading:"⚽ Giocatori",players:"Giocatori",rating:"OVR più alto",languages:"Lingue",search:"Cerca giocatori...",nationality:"Nazionalità",club:"Club",position:"Posizione",ratingText:"Valutazione",empty:"Nessun giocatore trovato",standard:"Standard"},
  tr:{subtitle:"Futbol dünyası — hepsi tek bir yerde!",heading:"⚽ Futbolcular",players:"Futbolcular",rating:"En yüksek OVR",languages:"Diller",search:"Futbolcu ara...",nationality:"Milliyet",club:"Kulüp",position:"Pozisyon",ratingText:"Puan",empty:"Futbolcu bulunamadı",standard:"Standart"},
  ar:{subtitle:"عالم كرة القدم — كل شيء في مكان واحد!",heading:"⚽ اللاعبون",players:"اللاعبون",rating:"أعلى تقييم",languages:"اللغات",search:"ابحث عن لاعب...",nationality:"الجنسية",club:"النادي",position:"المركز",ratingText:"التقييم",empty:"لم يتم العثور على لاعبين",standard:"قياسي"},
  zh:{subtitle:"足球世界，一切尽在一处！",heading:"⚽ 球员",players:"球员",rating:"最高评分",languages:"语言",search:"搜索球员...",nationality:"国籍",club:"俱乐部",position:"位置",ratingText:"评分",empty:"未找到球员",standard:"标准"},
  ja:{subtitle:"サッカー選手の世界、すべてここに！",heading:"⚽ 選手",players:"選手",rating:"最高OVR",languages:"言語",search:"選手を検索...",nationality:"国籍",club:"クラブ",position:"ポジション",ratingText:"評価",empty:"選手が見つかりません",standard:"スタンダード"},
  ko:{subtitle:"축구 선수의 세계, 모든 것을 한곳에서!",heading:"⚽ 선수",players:"선수",rating:"최고 OVR",languages:"언어",search:"선수 검색...",nationality:"국적",club:"클럽",position:"포지션",ratingText:"평점",empty:"선수를 찾을 수 없습니다",standard:"스탠다드"},
  hi:{subtitle:"फुटबॉल की दुनिया — सब कुछ एक जगह!",heading:"⚽ खिलाड़ी",players:"खिलाड़ी",rating:"सबसे अधिक OVR",languages:"भाषाएँ",search:"खिलाड़ी खोजें...",nationality:"राष्ट्रीयता",club:"क्लब",position:"पोज़िशन",ratingText:"रेटिंग",empty:"कोई खिलाड़ी नहीं मिला",standard:"स्टैंडर्ड"},
  id:{subtitle:"Dunia sepak bola — semua dalam satu tempat!",heading:"⚽ Pemain",players:"Pemain",rating:"OVR tertinggi",languages:"Bahasa",search:"Cari pemain...",nationality:"Kebangsaan",club:"Klub",position:"Posisi",ratingText:"Rating",empty:"Pemain tidak ditemukan",standard:"Standar"}
};

const language = document.getElementById("language");
const search = document.getElementById("search");
let cards = [];

function changeLanguage() {
  const lang = language.value;
  const t = translations[lang] || translations.uz;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.getElementById("subtitle").textContent = t.subtitle;
  document.getElementById("heading").textContent = t.heading;
  document.getElementById("playersLabel").textContent = t.players;
  document.getElementById("ratingLabel").textContent = t.rating;
  document.getElementById("languagesLabel").textContent = t.languages;
  search.placeholder = t.search;
  document.getElementById("empty").textContent = t.empty;
  document.querySelectorAll(".nationality").forEach(e => e.textContent = t.nationality);
  document.querySelectorAll(".clubLabel").forEach(e => e.textContent = t.club);
  document.querySelectorAll(".positionLabel").forEach(e => e.textContent = t.position);
  document.querySelectorAll(".ratingText").forEach(e => e.textContent = t.ratingText);
  document.querySelectorAll(".badge").forEach(e => e.textContent = t.standard);
}

function filterPlayers() {
  const query = search.value.toLowerCase().trim();
  let visible = 0;
  cards.forEach(card => {
    const match = (card.dataset.name + " " + card.innerText).toLowerCase().includes(query);
    card.style.display = match ? "block" : "none";
    if (match) visible++;
  });
  document.getElementById("count").textContent = visible;
  document.getElementById("empty").style.display = visible ? "none" : "block";
}

language.addEventListener("change", changeLanguage);
search.addEventListener("input", filterPlayers);

async function loadPlayersFromDatabase() {
  try {
    const response = await fetch("/api/players");
    if (!response.ok) throw new Error("API xatosi: " + response.status);
    const players = await response.json();
    const container = document.getElementById("players");

    container.innerHTML = players.map(player => `
      <article class="card" data-id="${player.id}" data-name="${player.name} ${player.nationality} ${player.club}">
        <div class="ovr">${player.rating}
          <span class="position">${player.position}</span>
        </div>
        ${player.image ? `<div class="player-image"><img src="${player.image}" alt="${player.name}" onerror="this.parentElement.style.display='none'"></div>` : ""}
        <div class="name">${player.name}</div>
        <div class="info">
          <span class="nationality">Millati</span>: ${player.nationality}<br>
          <span class="clubLabel">Klub</span>: ${player.club}<br>
          <span class="positionLabel">Pozitsiya</span>: ${player.position}<br>
          <span class="ratingText">Reyting</span>: ${player.rating}
        </div>
        <span class="badge">Standard</span>
      </article>
    `).join("");

   cards = [...container.querySelectorAll(".card")];
   cards.forEach(card => {
  card.style.cursor = "pointer";
  card.addEventListener("click", () => {
    window.location.href = `/player?id=${card.dataset.id}`;
  });
});
 changeLanguage();
    filterPlayers();
  } catch (error) {
    console.error("Futbolchilarni yuklashda xato:", error);
  }
}


document.getElementById("importPlayerForm").addEventListener("submit", async event => {
  event.preventDefault();
  const status = document.getElementById("importStatus");
  const button = event.currentTarget.querySelector('button[type="submit"]');
  const value = id => document.getElementById(id).value.trim();

  const payload = {
    efootball_id: value("importId"),
    name: value("importName"),
    nationality: value("importNationality"),
    club: value("importClub"),
    position: value("importPosition"),
    rating: Number(value("importRating")),
    card_type: value("importCardType") || "Standard",
    image: value("importImage")
  };

  if (!/^\d+$/.test(payload.efootball_id)) {
    status.textContent = "eFootball ID faqat raqamlardan iborat bo‘lishi kerak.";
    return;
  }

  button.disabled = true;
  status.textContent = "Saqlanmoqda...";

  try {
    const response = await fetch("/api/import-player", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + value("importToken")
      },
      body: JSON.stringify(payload)
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Saqlash amalga oshmadi.");
    }

    status.textContent = "Saqlandi: " + result.player.name;
    document.getElementById("importPlayerForm").reset();
    await loadPlayersFromDatabase();
  } catch (error) {
    status.textContent = "Xato: " + error.message;
  } finally {
    button.disabled = false;
  }
});


const adminStatus = document.getElementById("adminStatus");
const adminStats = document.getElementById("adminStats");
const adminPlayers = document.getElementById("adminPlayers");

function adminHeaders(json = false) {
  const headers = {
    "Authorization": "Bearer " + document.getElementById("importToken").value.trim()
  };
  if (json) headers["Content-Type"] = "application/json";
  return headers;
}

async function adminRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {...adminHeaders(Boolean(options.body)), ...(options.headers || {})}
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(result.error || "So‘rov bajarilmadi: " + response.status);
  return result;
}

function adminText(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text == null ? "" : String(text);
  return element;
}

async function refreshAdminPlayers() {
  adminStatus.textContent = "Yuklanmoqda...";
  try {
    const q = document.getElementById("adminSearch").value.trim();
    const rows = await adminRequest("/api/admin/players?q=" + encodeURIComponent(q));
    adminPlayers.replaceChildren();

    for (const player of rows) {
      const card = adminText("div", "admin-player", "");
      card.appendChild(adminText("div", "admin-name",
        player.name + " · OVR " + player.rating));
      card.appendChild(adminText("div", "", 
        [player.nationality, player.club, player.position, "ID " + player.id]
          .filter(Boolean).join(" · ")));

      const edit = adminText("button", "", "✏️ Tahrirlash");
      edit.type = "button";
      edit.addEventListener("click", async () => {
        const name = prompt("Futbolchi ismi:", player.name);
        if (name === null) return;
        const ratingText = prompt("OVR (0–200):", player.rating);
        if (ratingText === null) return;
        const rating = Number(ratingText);
        if (!name.trim() || !Number.isInteger(rating) || rating < 0 || rating > 200) {
          adminStatus.textContent = "Ism yoki OVR noto‘g‘ri.";
          return;
        }
        try {
          await adminRequest("/api/admin/players/" + player.id, {
            method: "PATCH",
            body: JSON.stringify({name: name.trim(), rating})
          });
          adminStatus.textContent = "Futbolchi yangilandi.";
          await refreshAdminPlayers();
          await loadPlayersFromDatabase();
        } catch (error) {
          adminStatus.textContent = "Xato: " + error.message;
        }
      });

      const remove = adminText("button", "", "🗑️ O‘chirish");
      remove.type = "button";
      remove.addEventListener("click", async () => {
        if (!confirm(player.name + " futbolchisini bazadan o‘chirasizmi?")) return;
        try {
          await adminRequest("/api/admin/players/" + player.id, {method: "DELETE"});
          adminStatus.textContent = "Futbolchi o‘chirildi.";
          await refreshAdminPlayers();
          await loadPlayersFromDatabase();
        } catch (error) {
          adminStatus.textContent = "Xato: " + error.message;
        }
      });

      const build = adminText("button", "", "⚙️ BUILD MASTER");
      build.type = "button";
      build.addEventListener("click", async () => {
        try {
          const current = await adminRequest(
            "/api/players/" + player.id + "/build"
          );

          const statsText = prompt(
            'Statistika JSON (masalan: {"Speed":95,"Finishing":90}):',
            JSON.stringify(current.stats || {}, null, 2)
          );
          if (statsText === null) return;

          let stats;
          try {
            stats = JSON.parse(statsText);
          } catch {
            adminStatus.textContent = "Statistika JSON formati noto‘g‘ri.";
            return;
          }

          const highlightsText = prompt(
            'Highlights JSON (masalan: ["Bullet Header","Long-Range Curler"]):',
            JSON.stringify(current.highlights || [], null, 2)
          );
          if (highlightsText === null) return;

          let highlights;
          try {
            highlights = JSON.parse(highlightsText);
          } catch {
            adminStatus.textContent = "Highlights JSON formati noto‘g‘ri.";
            return;
          }

          const tip = prompt(
            "Futbolchi uchun maslahat:",
            current.tip || ""
          );
          if (tip === null) return;

          await adminRequest("/api/players/" + player.id + "/build", {
            method: "POST",
            body: JSON.stringify({stats, highlights, tip})
          });

          adminStatus.textContent = "BUILD MASTER ma’lumotlari saqlandi.";
          await refreshAdminPlayers();
        } catch (error) {
          adminStatus.textContent = "Xato: " + error.message;
        }
      });

      card.append(edit, remove, build);
      adminPlayers.appendChild(card);
    }
    if (!rows.length) adminPlayers.appendChild(adminText("p", "", "Futbolchi topilmadi."));
    adminStatus.textContent = "Topildi: " + rows.length + " ta futbolchi.";
  } catch (error) {
    adminStatus.textContent = "Xato: " + error.message;
  }
}

document.getElementById("adminRefresh").addEventListener("click", refreshAdminPlayers);
document.getElementById("adminSearch").addEventListener("input", refreshAdminPlayers);

document.getElementById("adminStatsButton").addEventListener("click", async () => {
  try {
    const stats = await adminRequest("/api/admin/stats");
    adminStats.textContent = "Futbolchilar: " + stats.players +
      " · BUILD MASTER yozuvlari: " + stats.builds;
  } catch (error) {
    adminStats.textContent = "Xato: " + error.message;
  }
});

document.getElementById("adminAddForm").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = Object.fromEntries(new FormData(form).entries());
  data.rating = Number(data.rating);
  data.level = Number(data.level);

  try {
    await adminRequest("/api/admin/players", {
      method: "POST",
      body: JSON.stringify(data)
    });
    adminStatus.textContent = "Futbolchi muvaffaqiyatli qo‘shildi.";
    form.reset();
    await refreshAdminPlayers();
    await loadPlayersFromDatabase();
  } catch (error) {
    adminStatus.textContent = "Xato: " + error.message;
  }
});


changeLanguage();
loadPlayersFromDatabase();
