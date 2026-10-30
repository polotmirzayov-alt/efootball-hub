
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
    }
    $("skillsGrid").innerHTML=["Double Touch","Sole Control","One-touch Pass","First-time Shot","Outside Curler"].map(s=>`<span class="badge">${s}</span>`).join("");
    $("positionsGrid").innerHTML=["CF","SS","AMF","LWF","RWF","CMF","DMF","CB","GK"].map((pos,i)=>{
      const score=pos===p.position?rating:Math.max(40,rating-[4,2,0,3,3,8,15,25,45][i]);
      return `<div class="pos"><span>${pos}</span><strong>${score}</strong></div>`;
    }).join("");

    $("loading").classList.add("hidden");
    $("profile").classList.remove("hidden");
  }catch(e){
    console.error(e);
    $("loading").classList.add("hidden");
    $("error").classList.remove("hidden");
  }
}
loadProfile();
