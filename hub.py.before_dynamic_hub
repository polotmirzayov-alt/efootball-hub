from flask import Flask, render_template_string, request

app = Flask(__name__)

PLAYERS = {
    "ronaldo_bigtime": {
        "name": "Cristiano Ronaldo", "type": "BIG TIME",
        "theme": "fire", "nation": "🇵🇹 Portugal",
        "club": "Al Nassr", "position": "CF",
        "ovr": 97, "max": 108, "level": "1 / 34",
        "style": "Fox in the Box", "height": "187 cm",
        "stats": {
            "Attacking Awareness": 99, "Ball Control": 92,
            "Dribbling": 91, "Tight Possession": 90,
            "Low Pass": 85, "Lofted Pass": 84,
            "Finishing": 99, "Heading": 95,
            "Set Piece Taking": 88, "Curl": 86,
            "Speed": 93, "Acceleration": 91,
            "Kicking Power": 99, "Jumping": 96,
            "Physical Contact": 90, "Balance": 82,
            "Stamina": 89, "Defensive Awareness": 40,
            "Tackling": 38, "Aggression": 50
        },
        "skills": [
            "First-time Shot", "Acrobatic Finishing", "Heading",
            "Sombrero", "Cut Behind & Turn", "Scotch Move",
            "Rising Shot", "Penalty Specialist"
        ],
        "positions": {"CF": 105, "SS": 98, "LWF": 96, "RWF": 94, "AMF": 88}
    },
    "messi_showtime": {
        "name": "Lionel Messi", "type": "SHOW TIME",
        "theme": "water", "nation": "🇦🇷 Argentina",
        "club": "Inter Miami", "position": "RWF",
        "ovr": 96, "max": 105, "level": "1 / 30",
        "style": "Deep-Lying Forward", "height": "170 cm",
        "stats": {
            "Attacking Awareness": 96, "Ball Control": 99,
            "Dribbling": 99, "Tight Possession": 99,
            "Low Pass": 95, "Lofted Pass": 90,
            "Finishing": 97, "Heading": 58,
            "Set Piece Taking": 96, "Curl": 95,
            "Speed": 90, "Acceleration": 98,
            "Kicking Power": 88, "Jumping": 62,
            "Physical Contact": 65, "Balance": 99,
            "Stamina": 80, "Defensive Awareness": 35,
            "Tackling": 30, "Aggression": 40
        },
        "skills": [
            "Momentum Dribbling", "Double Touch", "Sombrero",
            "Sole Control", "One-touch Pass", "Through Passing",
            "Outside Curler"
        ],
        "positions": {"CF": 95, "SS": 99, "LWF": 97, "RWF": 105, "AMF": 96}
    },
    "baggio_epic": {
        "name": "Roberto Baggio", "type": "EPIC",
        "theme": "ice", "nation": "🇮🇹 Italy",
        "club": "Inter Milan", "position": "AMF",
        "ovr": 93, "max": 105, "level": "1 / 33",
        "style": "Hole Player", "height": "174 cm",
        "stats": {
            "Attacking Awareness": 83, "Ball Control": 87,
            "Dribbling": 94, "Tight Possession": 93,
            "Low Pass": 93, "Lofted Pass": 86,
            "Finishing": 87, "Heading": 56,
            "Set Piece Taking": 71, "Curl": 77,
            "Speed": 88, "Acceleration": 94,
            "Kicking Power": 82, "Jumping": 55,
            "Physical Contact": 75, "Balance": 84,
            "Stamina": 75, "Defensive Awareness": 44,
            "Tackling": 43, "Aggression": 43
        },
        "skills": [
            "Momentum Dribbling", "Phenomenal Pass", "Double Touch",
            "Sole Control", "First-time Shot", "One-touch Pass",
            "Outside Curler"
        ],
        "positions": {"CF": 91, "SS": 94, "LWF": 94, "RWF": 94, "AMF": 105}
    },
    "nakata_highlight": {
        "name": "Hidetoshi Nakata", "type": "HIGHLIGHT",
        "theme": "urban", "nation": "🇯🇵 Japan",
        "club": "AS Roma", "position": "AMF",
        "ovr": 89, "max": 105, "level": "1 / 33",
        "style": "Creative Playmaker", "height": "175 cm",
        "stats": {
            "Attacking Awareness": 86, "Ball Control": 96,
            "Dribbling": 94, "Tight Possession": 96,
            "Low Pass": 96, "Lofted Pass": 92,
            "Finishing": 84, "Heading": 62,
            "Set Piece Taking": 76, "Curl": 81,
            "Speed": 87, "Acceleration": 92,
            "Kicking Power": 91, "Jumping": 67,
            "Physical Contact": 83, "Balance": 88,
            "Stamina": 85, "Defensive Awareness": 69,
            "Tackling": 68, "Aggression": 75
        },
        "skills": [
            "Long-range Curler", "Long-range Shooting",
            "Through Passing", "Super-sub", "Phenomenal Pass",
            "Double Touch", "One-touch Pass"
        ],
        "positions": {"CF": 82, "SS": 89, "LWF": 85, "RWF": 85, "AMF": 105}
    },
    "saliba_potw": {
        "name": "William Saliba", "type": "POTW",
        "theme": "potw", "nation": "🇫🇷 France",
        "club": "Arsenal", "position": "CB",
        "ovr": 89, "max": 102, "level": "1 / 28",
        "style": "The Destroyer", "height": "190 cm",
        "stats": {
            "Attacking Awareness": 52, "Ball Control": 67,
            "Dribbling": 60, "Tight Possession": 70,
            "Low Pass": 72, "Lofted Pass": 68,
            "Finishing": 51, "Heading": 90,
            "Set Piece Taking": 60, "Curl": 63,
            "Speed": 87, "Acceleration": 79,
            "Kicking Power": 66, "Jumping": 90,
            "Physical Contact": 92, "Balance": 64,
            "Stamina": 89, "Defensive Awareness": 94,
            "Tackling": 94, "Aggression": 91
        },
        "skills": [
            "Heading", "One-touch Pass", "Weighted Pass",
            "Man Marking", "Interception", "Acrobatic Clearance",
            "Fighting Spirit", "Blocker", "Aerial Superiority",
            "Sliding Tackle"
        ],
        "positions": {"CF": 72, "SS": 71, "AMF": 74, "DMF": 94, "CB": 102}
    },
    "maldini_legend": {
        "name": "Paolo Maldini", "type": "LEGEND",
        "theme": "dark", "nation": "🇮🇹 Italy",
        "club": "AC Milan", "position": "CB",
        "ovr": 94, "max": 105, "level": "1 / 30",
        "style": "Build Up", "height": "186 cm",
        "stats": {
            "Attacking Awareness": 60, "Ball Control": 78,
            "Dribbling": 72, "Tight Possession": 75,
            "Low Pass": 82, "Lofted Pass": 84,
            "Finishing": 58, "Heading": 89,
            "Set Piece Taking": 65, "Curl": 70,
            "Speed": 85, "Acceleration": 82,
            "Kicking Power": 78, "Jumping": 88,
            "Physical Contact": 88, "Balance": 76,
            "Stamina": 88, "Defensive Awareness": 98,
            "Tackling": 99, "Aggression": 92
        },
        "skills": [
            "Man Marking", "Interception", "Acrobatic Clearance",
            "Captaincy", "Fighting Spirit", "Blocker", "Sliding Tackle"
        ],
        "positions": {"CF": 60, "SS": 60, "AMF": 68, "DMF": 88, "CB": 105, "LB": 102, "RB": 95}
    },
    "haaland_standard": {
        "name": "Erling Haaland", "type": "STANDARD",
        "theme": "blue", "nation": "🇳🇴 Norway",
        "club": "Manchester City", "position": "CF",
        "ovr": 88, "max": 100, "level": "1 / 38",
        "style": "Goal Poacher", "height": "195 cm",
        "stats": {
            "Attacking Awareness": 95, "Ball Control": 76,
            "Dribbling": 72, "Tight Possession": 70,
            "Low Pass": 68, "Lofted Pass": 62,
            "Finishing": 96, "Heading": 88,
            "Set Piece Taking": 62, "Curl": 65,
            "Speed": 92, "Acceleration": 86,
            "Kicking Power": 95, "Jumping": 88,
            "Physical Contact": 96, "Balance": 70,
            "Stamina": 82, "Defensive Awareness": 42,
            "Tackling": 38, "Aggression": 65
        },
        "skills": [
            "First-time Shot", "Acrobatic Finishing", "Heading",
            "Super-sub", "Fighting Spirit", "One-touch Pass"
        ],
        "positions": {"CF": 100, "SS": 90, "LWF": 80, "RWF": 80, "AMF": 72}
    }
}

HTML = r"""
<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#080b13">
<title>eFootball Ultimate Hub</title>
<style>
:root{color-scheme:dark;--bg:#080b13;--panel:#111827;--muted:#9ca3af}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(ellipse at top,#17233a 0,#080b13 65%);color:#f8fafc;font:15px system-ui,Arial,sans-serif;min-height:100vh;padding:20px}
main{max-width:980px;margin:auto}
header{text-align:center;margin:10px 0 24px}
header h1{margin:0;font-size:clamp(25px,5vw,40px);letter-spacing:1px}
header h1 span{color:#38bdf8}
header p{color:var(--muted);margin:8px 0}
.layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:18px}
.panel{background:#101827eF;border:1px solid #263449;border-radius:18px;padding:18px;box-shadow:0 18px 45px #0005}
label{display:block;color:#aab8ca;font-size:13px;margin-bottom:7px}
select,input{width:100%;padding:12px;border-radius:10px;border:1px solid #34445b;background:#080f1d;color:white;font-size:15px}
input[type=range]{padding:0;accent-color:#38bdf8}
.field{margin-bottom:18px}
.pill{display:inline-block;border:1px solid #ffffff35;background:#0005;border-radius:999px;padding:5px 10px;font-size:11px;letter-spacing:1px}
.card{--accent:#f97316;--glow:#f97316;position:relative;isolation:isolate;overflow:hidden;min-height:330px;border-radius:17px;padding:22px;border:1px solid var(--accent);display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 0 24px color-mix(in srgb,var(--glow) 25%,transparent);transition:box-shadow .3s,transform .3s}
.card:hover{transform:translateY(-3px);box-shadow:0 0 38px color-mix(in srgb,var(--glow) 40%,transparent)}
.card:before,.card:after{content:"";position:absolute;inset:-35%;z-index:-1;pointer-events:none}
.card:after{background:radial-gradient(ellipse at 50% 110%,color-mix(in srgb,var(--glow) 45%,transparent),transparent 55%);animation:pulse 4s ease-in-out infinite alternate}
.card:before{opacity:.7;animation:drift 12s linear infinite}
.fire{--accent:#ff6537;--glow:#ff3b1f;background:linear-gradient(145deg,#210b0b,#68190e 55%,#120b12)}
.fire:before{background:repeating-linear-gradient(115deg,transparent 0 30px,#ff6b3522 31px 34px,transparent 35px 62px)}
.water{--accent:#45d9ff;--glow:#00a6ff;background:linear-gradient(145deg,#041a39,#075985 55%,#042b38)}
.water:before{background:repeating-radial-gradient(ellipse at 50% 100%,transparent 0 24px,#58e5ff24 25px 27px,transparent 28px 50px)}
.ice{--accent:#b9edff;--glow:#64caff;background:linear-gradient(145deg,#071e39,#17618a 55%,#0b132c)}
.ice:before{background:linear-gradient(60deg,transparent 45%,#d8f5ff24 46% 47%,transparent 48%),linear-gradient(120deg,transparent 35%,#d8f5ff20 36% 37%,transparent 38%)}
.urban{--accent:#d78cff;--glow:#b34cff;background:linear-gradient(145deg,#100d1d,#40204d 55%,#151221)}
.urban:before{background:linear-gradient(0deg,#0b0d18 0 28%,transparent 29%),repeating-linear-gradient(90deg,transparent 0 28px,#e8c4ff12 29px 31px),linear-gradient(180deg,transparent 40%,#f0abff12 41% 42%,transparent 43%)}
.potw{--accent:#ffe08a;--glow:#ffc44d;background:linear-gradient(145deg,#1d2e34,#527c70 48%,#a66a36)}
.potw:before{background:radial-gradient(ellipse at 50% 20%,#fff9d455,transparent 35%),repeating-linear-gradient(100deg,transparent 0 45px,#fff7d412 46px 48px)}
.dark{--accent:#d1d5db;--glow:#94a3b8;background:linear-gradient(145deg,#090b11,#282b37 60%,#111827)}
.dark:before{background:repeating-linear-gradient(135deg,transparent 0 40px,#ffffff0c 41px 43px)}
.blue{--accent:#60a5fa;--glow:#3b82f6;background:linear-gradient(145deg,#07163d,#1d4ed8 58%,#10172f)}
.blue:before{background:repeating-linear-gradient(115deg,transparent 0 32px,#60a5fa18 33px 35px,transparent 36px 64px)}
@keyframes drift{0%{transform:translateX(-2%) translateY(0)}50%{transform:translateX(2%) translateY(-2%)}100%{transform:translateX(-2%) translateY(0)}}
@keyframes pulse{from{opacity:.45;transform:scale(.96)}to{opacity:1;transform:scale(1.04)}}
.card-top,.card-bottom{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.ovr{font-size:48px;font-weight:900;line-height:1;text-shadow:0 3px 18px #0008}
.pos{font-size:13px;letter-spacing:2px}
.name{font-size:clamp(22px,4vw,32px);font-weight:900;line-height:1.12;margin:18px 0 8px;text-shadow:0 3px 15px #0008}
.sub{font-size:13px;color:#f1f5f9d9}
.card-bottom{align-items:flex-end;border-top:1px solid #ffffff35;padding-top:14px}
.card-bottom strong{display:block;font-size:14px}
.tabs{display:flex;gap:7px;flex-wrap:wrap;margin:16px 0}
.tab{flex:1;min-width:75px;border:1px solid #334155;background:#172235;color:#cbd5e1;padding:11px 6px;border-radius:10px;font-weight:700;cursor:pointer}
.tab.active{background:#0284c7;border-color:#38bdf8;color:white}
.content{background:#0b1220;border:1px solid #263449;border-radius:14px;padding:15px}
.section-title{font-size:14px;color:#7dd3fc;margin:0 0 12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.info{background:#151f30;border:1px solid #29374a;padding:11px;border-radius:10px;min-width:0}
.info small{display:block;color:#94a3b8;font-size:11px;margin-bottom:4px}
.info b{overflow-wrap:anywhere}
.stat{margin:13px 0}
.stat-head{display:flex;justify-content:space-between;gap:10px;font-size:12px;margin-bottom:5px}
.bar{height:6px;background:#263449;border-radius:9px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:9px;background:linear-gradient(90deg,#38bdf8,#34d399);transition:width .3s}
.skills{display:flex;flex-wrap:wrap;gap:8px}
.skill{border:1px solid #36516b;background:#172b40;padding:8px 10px;border-radius:9px;font-size:12px}
footer{text-align:center;color:#64748b;font-size:11px;padding:22px 0 5px}
@media(max-width:700px){body{padding:12px}.layout{grid-template-columns:1fr}.panel{padding:14px}.card{min-height:285px}.tabs{gap:5px}.tab{font-size:12px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<main>
<header>
<h1>⚽ eFootball <span>ULTIMATE HUB</span></h1>
<p>Kartalar • Reytinglar • Skills • Pozitsiyalar</p>
</header>
<div class="layout">
<section class="panel">
<form method="get" action="/">
<div class="field">
<label for="player">FUTBOLCHI KARTASINI TANLANG</label>
<select id="player" name="player" onchange="this.form.submit()">
{% for key,p in database.items() %}
<option value="{{key}}" {% if key==selected %}selected{% endif %}>{{p.name}} — {{p.type}}</option>
{% endfor %}
</select>
</div>
<div class="field">
<label for="ovr">OVR darajasi: <strong id="ovrLabel">{{ovr}}</strong></label>
<input id="ovr" name="ovr" type="range" min="0" max="112" value="{{ovr}}" oninput="document.getElementById('ovrLabel').textContent=this.value">
</div>
<input type="hidden" name="tab" value="{{tab}}">
<button class="tab" type="submit" style="width:100%">⚡ Reytingni ko‘rsatish</button>
</form>
<div class="card {{player.theme}}" style="margin-top:18px">
<div class="card-top">
<div><span class="pill">{{player.type}}</span><div class="pos" style="margin-top:10px">{{player.position}}</div></div>
<div style="text-align:right"><div class="ovr">{{ovr}}</div><div class="pos">OVR</div></div>
</div>
<div>
<div class="name">{{player.name}}</div>
<div class="sub">{{player.nation}} · {{player.club}}</div>
</div>
<div class="card-bottom">
<div><strong>{{player.style}}</strong><span class="sub">O‘yin uslubi</span></div>
<div style="text-align:right"><strong>{{player.level}}</strong><span class="sub">{{player.height}}</span></div>
</div>
</div>
<div class="tabs">
<a class="tab {% if tab=='stats' %}active{% endif %}" href="/?player={{selected}}&ovr={{ovr}}&tab=stats">📊 Stats</a>
<a class="tab {% if tab=='builds' %}active{% endif %}" href="/?player={{selected}}&ovr={{ovr}}&tab=builds">⚙️ Builds</a>
<a class="tab {% if tab=='skills' %}active{% endif %}" href="/?player={{selected}}&ovr={{ovr}}&tab=skills">⚡ Skills</a>
<a class="tab {% if tab=='positions' %}active{% endif %}" href="/?player={{selected}}&ovr={{ovr}}&tab=positions">🏟️ Positions</a>
</div>
</section>
<section class="panel">
<div class="content">
{% if tab=='stats' %}
<h3 class="section-title">📊 FUTBOLCHI STATISTIKALARI</h3>
<div class="grid">
<div class="info"><small>Millat</small><b>{{player.nation}}</b></div>
<div class="info"><small>Klub</small><b>{{player.club}}</b></div>
<div class="info"><small>Pozitsiya</small><b>{{player.position}}</b></div>
<div class="info"><small>O‘yin uslubi</small><b>{{player.style}}</b></div>
</div>
<h3 class="section-title" style="margin-top:20px">Asosiy ko‘rsatkichlar</h3>
{% for stat,val in player.stats.items() %}
<div class="stat">
<div class="stat-head"><span>{{stat}}</span><b>{{val}}</b></div>
<div class="bar"><i style="width:{{val}}%"></i></div>
</div>
{% endfor %}
{% elif tab=='builds' %}
<h3 class="section-title">⚙️ PLAYER BUILD</h3>
<div class="grid">
{% for label,value in player.stats.items() if label in ['Finishing','Low Pass','Dribbling','Speed','Acceleration','Physical Contact','Stamina','Defensive Awareness'] %}
<div class="info"><small>{{label}}</small><b>{{value}} / 105</b><div class="bar" style="margin-top:8px"><i style="width:{{value}}%"></i></div></div>
{% endfor %}
</div>
<p class="sub">Bu bo‘limdagi ko‘rsatkichlar futbolchining bazaviy atributlaridir. Maxsus build taqsimoti alohida kiritilmagan.</p>
{% elif tab=='skills' %}
<h3 class="section-title">⚡ PLAYER SKILLS</h3>
<div class="skills">
{% for skill in player.skills %}<span class="skill">✦ {{skill}}</span>{% endfor %}
</div>
{% elif tab=='positions' %}
<h3 class="section-title">🏟️ POZITSIYA REYTINGLARI</h3>
{% for pos,val in player.positions.items() %}
<div class="stat">
<div class="stat-head"><span>{{pos}}</span><b>{{val}}</b></div>
<div class="bar"><i style="width:{{[val,105]|min}}%"></i></div>
</div>
{% endfor %}
{% endif %}
</div>
<footer>Statistikalar namuna ma’lumotlari asosida. Har bir karta qiymatlari o‘yindagi aniq versiyaga qarab farq qilishi mumkin.</footer>
</section>
</div>
<footer>eFootball Ultimate Hub · Mobile friendly · Animated card themes</footer>
</main>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    selected = request.args.get("player", "ronaldo_bigtime")
    if selected not in PLAYERS:
        selected = "ronaldo_bigtime"

    player = PLAYERS[selected]
    try:
        ovr = int(request.args.get("ovr", player["ovr"]))
    except (TypeError, ValueError):
        ovr = player["ovr"]

    ovr = max(0, min(112, ovr))
    tab = request.args.get("tab", "stats")
    if tab not in {"stats", "builds", "skills", "positions"}:
        tab = "stats"

    return render_template_string(
        HTML,
        database=PLAYERS,
        selected=selected,
        player=player,
        ovr=ovr,
        tab=tab
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
