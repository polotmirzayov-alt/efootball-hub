from flask import Flask, render_template_string, request

app = Flask(__name__)

# To'liq va mukammal futbolchilar bazasi (Stats, Builds, Skills, Positions)
DATABASE = {
    "cristiano ronaldo": {
        "name": "Cristiano Ronaldo",
        "card_type": "Big Time",
        "millat": "Portugal",
        "klub": "Al Nassr",
        "pozitsiya": "CF",
        "reyting": "108",
        "daraja": "Max",
        "oyin_uslubi": "Fox in the Box",
        "theme_effect": "🔥 Olov yonib turmoqda [BIG TIME EFFECT]",
        "stats": {
            "Attacking Awareness": 99, "Ball Control": 92, "Dribbling": 91,
            "Tight Possession": 90, "Low Pass": 85, "Lofted Pass": 84,
            "Finishing": 99, "Speed": 93, "Acceleration": 91,
            "Kicking Power": 99, "Physical Contact": 90, "Balance": 82, "Stamina": 89
        },
        "builds": "SHT: 8 | DRI: 8 | DEX: 8 | LBS: 12 (Optimal Max Build)",
        "skills": ["First-time Shot", "Acrobatic Finishing", "Heading", "Sombrero", "Cut Behind & Turn", "Scotch Move", "One-touch Pass"],
        "positions": {"CF": 99, "SS": 96, "LWF": 95, "RWF": 94, "AMF": 88, "CMF": 75, "DMF": 55, "CB": 45, "GK": 40}
    },
    "nakata": {
        "name": "Nakata Hidetoshi",
        "card_type": "Epic",
        "millat": "Japan",
        "klub": "AS Roma",
        "pozitsiya": "AMF",
        "reyting": "106.74",
        "daraja": "Max",
        "oyin_uslubi": "Creative Playmaker",
        "theme_effect": "🧊 Muz parchalanmoqda [EPIC EFFECT]",
        "stats": {
            "Attacking Awareness": 86, "Ball Control": 96, "Dribbling": 94,
            "Tight Possession": 96, "Low Pass": 96, "Lofted Pass": 92,
            "Finishing": 84, "Speed": 87, "Acceleration": 92,
            "Kicking Power": 91, "Physical Contact": 83, "Balance": 88, "Stamina": 85
        },
        "builds": "SHT: 4 | PAS: 9 | DRI: 11 | DEX: 8 | LBS: 8 (Midfield Maestro)",
        "skills": ["Long-range Curler", "Long-range Shooting", "Through Passing", "Super-sub", "Phenomenal Pass", "Double Touch"],
        "positions": {"CF": 82, "SS": 89, "AMF": 95, "CMF": 92, "LWF": 85, "RWF": 85, "DMF": 80, "CB": 60, "GK": 40}
    },
    "lionel messi": {
        "name": "Lionel Messi",
        "card_type": "Show Time",
        "millat": "Argentina",
        "klub": "Inter Miami",
        "pozitsiya": "RWF",
        "reyting": "107.2",
        "daraja": "Max",
        "oyin_uslubi": "Creative Playmaker",
        "theme_effect": "🌊 Suv to'lqini va oqim [SHOW TIME EFFECT]",
        "stats": {
            "Attacking Awareness": 96, "Ball Control": 99, "Dribbling": 99,
            "Tight Possession": 99, "Low Pass": 95, "Lofted Pass": 90,
            "Finishing": 97, "Speed": 90, "Acceleration": 98,
            "Kicking Power": 88, "Physical Contact": 65, "Balance": 99, "Stamina": 80
        },
        "builds": "SHT: 6 | PAS: 8 | DRI: 12 | DEX: 10 | LBS: 4 (Dribbling God)",
        "skills": ["Double Touch", "Sombrero", "Sole Control", "One-touch Pass", "Through Passing", "GP Turn"],
        "positions": {"CF": 95, "SS": 99, "LWF": 97, "RWF": 99, "AMF": 96, "CMF": 84, "DMF": 50, "CB": 40, "GK": 35}
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>eFootball Ultimate Hub</title>
    <style>
        body { background-color: #0d1b2a; color: #e0e1dd; font-family: Arial, sans-serif; margin: 0; padding: 15px; }
        .container { max-width: 600px; margin: auto; background: #1b263b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { color: #00b4d8; text-align: center; }
        select, button { width: 100%%; padding: 12px; margin: 10px 0; background: #415a77; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .tabs { display: flex; justify-content: space-between; margin: 15px 0; }
        .tab-btn { flex: 1; margin: 0 3px; padding: 10px; background: #1d3557; color: #a8dadc; border: 1px solid #457b9d; border-radius: 6px; text-align: center; font-weight: bold; text-decoration: none; font-size: 14px; }
        .tab-btn.active { background: #00b4d8; color: #0d1b2a; }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #0d1b2a; padding: 12px; border-radius: 8px; margin-top: 10px; }
        .card-box { background: #22333b; padding: 12px; border-radius: 8px; margin-top: 15px; border-left: 4px solid #00b4d8; }
        .stat-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #2b2d42; font-size: 14px; }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #8d99ae; }
    </style>
</head>
<body>
<div class="container">
    <h2>⚡ eFootball Ultimate Hub</h2>
    
    <form method="GET" action="/">
        <label><b>Kartani tanlang:</b></label>
        <select name="player" onchange="this.form.submit()">
            {% for key in database.keys() %}
                <option value="{{ key }}" {% if key == selected_key %}selected{% endif %}>{{ database[key]['name'] }} ({{ database[key]['card_type'] }})</option>
            {% endfor %}
        </select>
    </form>

    <div class="card-box">
        <p><b>Tanlangan karta:</b> {{ player['name'] }} - {{ player['reyting'] }} OVR</p>
        <p style="color: #ffd166; font-size: 13px;">{{ player['theme_effect'] }}</p>
    </div>

    <!-- 4 TA ASOSIY TUGMA (STATS, BUILDS, SKILLS, POSITIONS) -->
    <div class="tabs">
        <a href="/?player={{ selected_key }}&tab=stats" class="tab-btn {% if active_tab == 'stats' %}active{% endif %}">📊 Stats</a>
        <a href="/?player={{ selected_key }}&tab=builds" class="tab-btn {% if active_tab == 'builds' %}active{% endif %}">⚙️ Builds</a>
        <a href="/?player={{ selected_key }}&tab=skills" class="tab-btn {% if active_tab == 'skills' %}active{% endif %}">⚡ Skills</a>
        <a href="/?player={{ selected_key }}&tab=positions" class="tab-btn {% if active_tab == 'positions' %}active{% endif %}">🏟️ Positions</a>
    </div>

    <!-- PLAYER INFORMATION -->
    <div class="card-box">
        <h3 style="color: #48cae4; margin-top: 0; font-size: 16px;">PLAYER INFORMATION</h3>
        <div class="info-grid">
            <div><b>Millat:</b><br>{{ player['millat'] }}</div>
            <div><b>Klub:</b><br>{{ player['klub'] }}</div>
            <div><b>Pozitsiya:</b><br>{{ player['pozitsiya'] }}</div>
            <div><b>Reyting:</b><br>{{ player['reyting'] }}</div>
            <div><b>Daraja:</b><br>{{ player['daraja'] }}</div>
            <div><b>O'yin uslubi:</b><br>{{ player['oyin_uslubi'] }}</div>
        </div>
    </div>

    <!-- DINAMIK MAZMUN (Tugmalar bosilganda ochiladigan qism) -->
    <div class="card-box">
        {% if active_tab == 'stats' %}
            <h3 style="color: #52b788; margin-top: 0; font-size: 16px;">📊 PLAYER STATS</h3>
            {% for stat, val in player['stats'].items() %}
                <div class="stat-row">
                    <span>{{ stat }}</span>
                    <span style="color: {% if val >= 90 %}#52b788{% elif val >= 80 %}#ffd166{% else %}#ef476f{% endif %}; font-weight: bold;">{{ val }}</span>
                </div>
            {% endfor %}

        {% elif active_tab == 'builds' %}
            <h3 style="color: #f77f00; margin-top: 0; font-size: 16px;">⚙️ BUILDS & MAX TUGMASI</h3>
            <p><b>Optimal Ochko Taqsimoti:</b></p>
            <div style="background: #0d1b2a; padding: 12px; border-radius: 6px; color: #ffd166; font-weight: bold;">
                {{ player['builds'] }}
            </div>
            <p style="font-size: 13px; color: #8d99ae; margin-top: 10px;">* Bu build futbolchining eng yuqori ko'rsatkichga chiqishini ta'minlaydi.</p>

        {% elif active_tab == 'skills' %}
            <h3 style="color: #f72585; margin-top: 0; font-size: 16px;">⚡ PLAYER SKILLS</h3>
            <ul>
                {% for skill in player['skills'] %}
                    <li style="margin: 6px 0; color: #f8f9fa;">{{ skill }}</li>
                {% endfor %}
            </ul>

        {% elif active_tab == 'positions' %}
            <h3 style="color: #4cc9f0; margin-top: 0; font-size: 16px;">🏟️ POSITIONS RATING</h3>
            <div class="info-grid">
                {% for pos, val in player['positions'].items() %}
                    <div><b>{{ pos }}:</b> <span style="color: #4ade80;">{{ val }}</span></div>
                {% endfor %}
            </div>
        {% endif %}
    </div>

    <div class="footer">
        eFOOTBALL HUB • PLAYER PROFILE (TERMUX HOSTED)
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    selected_key = request.args.get('player', 'cristiano ronaldo')
    active_tab = request.args.get('tab', 'stats')
    
    if selected_key not in DATABASE:
        selected_key = 'cristiano ronaldo'
        
    player = DATABASE[selected_key]
    return render_template_string(HTML_TEMPLATE, database=DATABASE, player=player, selected_key=selected_key, active_tab=active_tab)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
