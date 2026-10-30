
const $ = id => document.getElementById(id);
const params = new URLSearchParams(location.search);
const playerId = params.get("id");

function addStat(label,value){
  const n = Math.max(0,Math.min(99,Number(value)||0));
  return `<div class="stat"><div class="stat-top"><span>${label}</span><strong>${n}</strong></div><div class="bar"><div class="fill" style="width:${n}%"></div></div></div>`;
}

function showTab(id){
  document.querySelectorAll("main section.panel").forEach(s=>s.classList.toggle("hidden",s.id!==id));
  document.querySelectorAll(".tabs button").forEach(b=>b.classList.toggle("active",b.dataset.tab===id));
}
document.querySelectorAll(".tabs button").forEach(b=>b.addEventListener("click",()=>showTab(b.dataset.tab)));


function showUnknown(container, message) {
  $(container).textContent = message;
}

function renderObjectStats(container, obj) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj) ||
      Object.keys(obj).length === 0) {
    showUnknown(container, "Ma’lumot mavjud emas.");
    return;
  }
  $(container).innerHTML = "";
  for (const [label, value] of Object.entries(obj)) {
    const item = document.createElement("div");
    item.className = "stat";
    const title = document.createElement("div");
    title.textContent = label;
    const val = document.createElement("strong");
    val.textContent = value == null || value === "" ? "—" : String(value);
    item.append(title, val);
    $(container).appendChild(item);
  }
}

function renderBadges(container, values, emptyMessage) {
  $(container).replaceChildren();
  if (!Array.isArray(values) || values.length === 0) {
    $(container).textContent = emptyMessage;
    return;
  }
  for (const value of values) {
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = String(value);
    $(container).appendChild(badge);
  }
}

async function loadPlayerCards(player) {
  const select = $("cardSelect");
  select.replaceChildren();
  const initial = document.createElement("option");
  initial.value = "";
  initial.textContent = "Kartani tanlang";
  select.appendChild(initial);

  try {
    const response = await fetch(`/api/players/${encodeURIComponent(player.id)}/cards`);
    if (!response.ok) throw new Error("Kartalar API xatosi");
    const cards = await response.json();

    if (!Array.isArray(cards) || cards.length === 0) {
      $("cardStatus").textContent =
        "Bu futbolchi uchun alohida karta hali bazaga kiritilmagan.";
      select.disabled = true;
      showUnknown("statsGrid", "Karta statistikasi mavjud emas.");
      showUnknown("skillsGrid", "Karta ko‘nikmalari mavjud emas.");
      showUnknown("positionsGrid", "Pozitsiya reytinglari mavjud emas.");
      return;
    }

    select.disabled = false;
    for (const card of cards) {
      const option = document.createElement("option");
      option.value = String(card.id);
      option.textContent =
        `${card.card_name || "Nomsiz karta"} — OVR ${card.rating ?? "—"}`;
      select.appendChild(option);
    }

    select.onchange = () => {
      const chosen = cards.find(c => String(c.id) === select.value);
      if (chosen) loadCardDetails(chosen);
    };

    select.value = String(cards[0].id);
    await loadCardDetails(cards[0]);
  } catch (error) {
    console.error("Karta yuklash xatosi:", error);
    $("cardStatus").textContent = "Kartalarni yuklab bo‘lmadi.";
    select.disabled = true;
  }
}

async function loadCardDetails(card) {
  $("cardStatus").textContent = "Karta tafsilotlari yuklanmoqda...";
  $("rating").textContent = card.rating ?? "--";
  $("position").textContent = card.position || "--";
  $("cardType").textContent = "🃏 " + (card.card_type || "Noma’lum");

  showUnknown("statsGrid", "Ma’lumot yuklanmoqda...");
  showUnknown("skillsGrid", "Ma’lumot yuklanmoqda...");
  showUnknown("positionsGrid", "Ma’lumot yuklanmoqda...");
  showUnknown("buildGrid", "Ma’lumot yuklanmoqda...");
  showUnknown("highlightsGrid", "Ma’lumot yuklanmoqda.");

  try {
    const response = await fetch(`/api/cards/${encodeURIComponent(card.id)}/details`);
    if (!response.ok) throw new Error("Karta tafsilotlari API xatosi");

    const result = await response.json();
    const details = result.details === null ? null : result;

    if (!details) {
      $("cardStatus").textContent =
        "Karta tanlandi, lekin batafsil ma'lumotlar kiritilmagan.";
      showUnknown("statsGrid", "Statistika mavjud emas.");
      showUnknown("skillsGrid", "Ko‘nikmalar mavjud emas.");
      showUnknown("positionsGrid", "Pozitsiya reytinglari mavjud emas.");

      const buildResponse = await fetch(
        `/api/cards/${encodeURIComponent(card.id)}/build`
      );
      if (!buildResponse.ok) {
        throw new Error("Karta BUILD MASTER API xatosi");
      }

      const buildResult = await buildResponse.json();
      const cardBuild = buildResult.build;

      if (cardBuild) {
        renderObjectStats("buildGrid", cardBuild.stats);
        renderBadges(
          "highlightsGrid",
          cardBuild.highlights,
          "Karta highlights ma'lumoti mavjud emas."
        );
        $("buildStatus").textContent =
          "Tanlangan karta uchun BUILD MASTER";
        $("buildTip").textContent =
          cardBuild.tip || "Karta maslahati mavjud emas.";
      } else {
        showUnknown("buildGrid", "BUILD MASTER hali kiritilmagan.");
        showUnknown("highlightsGrid", "Highlights mavjud emas.");
        $("buildStatus").textContent =
          "Karta uchun BUILD MASTER kiritilmagan.";
        $("buildTip").textContent = "Maslahat mavjud emas.";
      }
      return;
    }

    $("cardStatus").textContent =
      "Tanlangan karta: " + (card.card_name || "Nomsiz karta") +
      " | MAX OVR: " + (details.max_ovr ?? "Kiritilmagan");
    $("rating").textContent = card.rating ?? "--";
    $("position").textContent = card.position || "--";

    renderObjectStats("statsGrid", details.stats);
    renderObjectStats("positionsGrid", details.position_ratings);
    renderBadges("skillsGrid", details.skills, "Ko‘nikmalar mavjud emas.");

    // Tanlangan kartaning alohida BUILD MASTER ma'lumotlari.
    const buildResponse = await fetch(
      `/api/cards/${encodeURIComponent(card.id)}/build`
    );
    if (!buildResponse.ok) {
      throw new Error("Karta BUILD MASTER API xatosi");
    }

    const buildResult = await buildResponse.json();
    const cardBuild = buildResult.build;

    if (cardBuild) {
      renderObjectStats("buildGrid", cardBuild.stats);
      renderBadges(
        "highlightsGrid",
        cardBuild.highlights,
        "Karta highlights ma'lumoti mavjud emas."
      );
      $("buildStatus").textContent =
        "Tanlangan karta uchun BUILD MASTER";
      $("buildTip").textContent =
        cardBuild.tip || "Karta maslahati mavjud emas.";
    } else {
      // BUILD MASTER kiritilmagan bo‘lsa, eski MAX BUILD ko‘rsatiladi.
      renderObjectStats("buildGrid", details.max_build);
      renderBadges(
        "highlightsGrid",
        details.boosters,
        "Boosterlar mavjud emas."
      );
      $("buildStatus").textContent =
        "BUILD MASTER kiritilmagan — MAX BUILD ko‘rsatilmoqda.";
      $("buildTip").textContent = "Karta maslahati mavjud emas.";
    }
  } catch (error) {
    console.error("Karta tafsilotlari xatosi:", error);
    $("cardStatus").textContent = "Karta tafsilotlarini yuklab bo‘lmadi.";
    showUnknown("statsGrid", "Ma’lumotni yuklashda xatolik.");
    showUnknown("skillsGrid", "Ma’lumotni yuklashda xatolik.");
    showUnknown("positionsGrid", "Ma’lumotni yuklashda xatolik.");
    showUnknown("buildGrid", "Ma’lumotni yuklashda xatolik.");
    showUnknown("highlightsGrid", "Ma’lumotni yuklashda xatolik.");
  }
}

async function loadProfile(){
  if(!playerId){$("loading").classList.add("hidden");$("error").classList.remove("hidden");return;}
  try{
    const response=await fetch("/api/players");
    if(!response.ok) throw new Error("API error");
    const players=await response.json();
    const p=players.find(x=>String(x.id)===playerId);
    if(!p) throw new Error("Player not found");

    $("name").textContent=p.name||"Noma’lum futbolchi";
    $("rating").textContent=p.rating??"--";
    $("position").textContent=p.position||"--";
    $("club").textContent=p.club||"Klub noma’lum";
    $("nationality").textContent="🌍 "+(p.nationality||"Noma’lum");
    $("cardType").textContent="🃏 "+(p.card_type||"Standard");
    $("level").textContent="⭐ Level "+(p.level||1);
    document.title=(p.name||"Player")+" — eFOOTBALL HUB";

    if(p.image){
      $("photo").src=p.image;
      $("photo").onload=()=>{$("photo").classList.remove("hidden");$("noPhoto").style.display="none";};
      $("photo").onerror=()=>{$("photo").classList.add("hidden");$("noPhoto").style.display="flex";};
    }

    $("infoGrid").innerHTML=[
      ["Millat",p.nationality||"—"],
      ["Klub",p.club||"—"],
      ["Pozitsiya",p.position||"—"],
      ["Reyting",p.rating??"—"],
      ["Daraja",p.level||1],
      ["O‘yin uslubi",p.playing_style||"—"],
      ["Karta turi",p.card_type||"Standard"]
    ].map(([a,b])=>`<div class="stat">${a}<br><strong>${b}</strong></div>`).join("");

    $("statsGrid").innerHTML =
      '<p class="muted">Batafsil futbolchi statistikasi hali bazaga kiritilmagan.</p>';

    $("buildGrid").innerHTML = "";
    $("highlightsGrid").innerHTML = "";
    $("buildTip").textContent = "Hali maslahat kiritilmagan.";

    // BUILD MASTER endi tanlangan karta orqali loadCardDetails() ichida yuklanadi.
    // Eski futbolchi bo‘yicha build bu yerda yuklanmaydi.
    $("skillsGrid").textContent = "Haqiqiy karta ko‘nikmalari kiritilmagan.";
    $("positionsGrid").textContent = "Haqiqiy pozitsiya reytinglari kiritilmagan.";
    await loadPlayerCards(p);

    $("loading").classList.add("hidden");
    $("profile").classList.remove("hidden");
  }catch(e){
    console.error(e);
    $("loading").classList.add("hidden");
    $("error").classList.remove("hidden");
  }
}
loadProfile();
