"""
Monopoly Deal - Card Table Edition
Features: Realistic card table aesthetic, proper payment from properties, multiplayer support
"""

import streamlit as st
import streamlit.components.v1 as components
import random
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ============================================================
# CONFIGURATION
# ============================================================

COLORS = ["Brown", "Light Blue", "Pink", "Orange", "Red",
          "Yellow", "Green", "Dark Blue", "Railroad", "Utility"]

PROPERTY_SETS = {
    "Brown": 2, "Light Blue": 3, "Pink": 3, "Orange": 3, "Red": 3,
    "Yellow": 3, "Green": 3, "Dark Blue": 2, "Railroad": 4, "Utility": 2
}

RENT_VALUES = {
    "Brown": [1, 2], "Light Blue": [1, 2, 3], "Pink": [1, 2, 4],
    "Orange": [1, 3, 5], "Red": [2, 3, 6], "Yellow": [2, 4, 6],
    "Green": [2, 4, 7], "Dark Blue": [3, 8],
    "Railroad": [1, 2, 3, 4], "Utility": [1, 2],
}

HOUSE_BONUS, HOTEL_BONUS = 3, 4
MAX_HAND, PLAYS_PER_TURN = 7, 3

COLOR_HEX = {
    "Brown": "#8B4513", "Light Blue": "#87CEEB", "Pink": "#E91E63",
    "Orange": "#FF9800", "Red": "#F44336", "Yellow": "#FFEB3B",
    "Green": "#4CAF50", "Dark Blue": "#1565C0", "Railroad": "#455A64", "Utility": "#78909C"
}

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Monopoly Deal", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# WOODEN TABLE AESTHETIC STYLES
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@400;500;600;700&display=swap');

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* WOODEN TABLE BACKGROUND */
.stApp {
    background: 
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect fill='%23c9a66b' width='100' height='100'/%3E%3Cpath d='M0 0h100v2H0zM0 10h100v1H0zM0 23h100v2H0zM0 35h100v1H0zM0 48h100v2H0zM0 60h100v1H0zM0 73h100v2H0zM0 85h100v1H0zM0 97h100v2H0z' fill='%23b8956a' fill-opacity='0.4'/%3E%3C/svg%3E"),
        linear-gradient(135deg, #c9a66b 0%, #a67c52 50%, #8b6342 100%);
    background-size: 100px 100px, cover;
    min-height: 100vh;
}

/* Add wood grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 50px,
            rgba(139, 99, 66, 0.1) 50px,
            rgba(139, 99, 66, 0.1) 51px
        ),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 20px,
            rgba(0,0,0,0.03) 20px,
            rgba(0,0,0,0.03) 21px
        );
    pointer-events: none;
    z-index: 0;
}

.stApp > * { position: relative; z-index: 1; }

/* Typography */
h1, h2, h3 { 
    font-family: 'Playfair Display', serif !important; 
    color: #3d2617 !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.3);
}

p, span, div, .stMarkdown { 
    font-family: 'Poppins', sans-serif !important;
    color: #2d1810 !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    background: linear-gradient(145deg, #d4a574, #b8895a) !important;
    color: #2d1810 !important;
    border: 2px solid #8b6342 !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0,0,0,0.4) !important;
    background: linear-gradient(145deg, #e0b584, #c99a6a) !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #2d1810 !important;
    font-weight: bold !important;
}

/* Card area backgrounds */
.card-area {
    background: rgba(0,0,0,0.15);
    border-radius: 15px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# REALISTIC CARD RENDERER
# ============================================================

CARD_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@500;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Poppins', sans-serif;
    background: transparent;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 8px;
    justify-content: flex-start;
    align-items: flex-end;
}

body.center { justify-content: center; }
body.scattered { justify-content: center; gap: 5px; }

/* REALISTIC PLAYING CARD */
.card {
    width: 90px;
    height: 130px;
    background: linear-gradient(145deg, #ffffff 0%, #f8f8f8 50%, #f0f0f0 100%);
    border-radius: 8px;
    position: relative;
    box-shadow: 
        0 2px 4px rgba(0,0,0,0.2),
        0 4px 8px rgba(0,0,0,0.15),
        0 0 0 1px rgba(0,0,0,0.05),
        inset 0 1px 0 rgba(255,255,255,0.8);
    transition: all 0.25s ease;
    cursor: pointer;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 3px; left: 3px; right: 3px; bottom: 3px;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 6px;
    pointer-events: none;
}

.card:hover {
    transform: translateY(-12px) rotate(-2deg) scale(1.05);
    box-shadow: 
        0 15px 30px rgba(0,0,0,0.3),
        0 5px 15px rgba(0,0,0,0.2);
    z-index: 100;
}

/* Scattered card rotations */
.card:nth-child(odd) { transform: rotate(-1deg); }
.card:nth-child(even) { transform: rotate(1deg); }
.card:nth-child(3n) { transform: rotate(-2deg); }
.card:nth-child(3n+1):hover { transform: translateY(-12px) rotate(2deg) scale(1.05); }

/* Card Header */
.card-header {
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3px;
    border-radius: 6px 6px 0 0;
    margin: 3px 3px 0 3px;
}

.card-title {
    font-size: 8px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    text-align: center;
}

.card-title.dark { color: #1a1a1a; text-shadow: none; }

/* Card Body */
.card-body {
    height: 65px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4px;
}

/* Card Footer */
.card-footer {
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, #f5f5f5, #e8e8e8);
    margin: 0 3px 3px 3px;
    border-radius: 0 0 5px 5px;
    border-top: 1px solid #ddd;
}

.value-badge {
    font-size: 11px;
    font-weight: 700;
    color: #2e7d32;
    background: linear-gradient(145deg, #e8f5e9, #c8e6c9);
    padding: 2px 10px;
    border-radius: 10px;
    border: 1.5px solid #a5d6a7;
}

/* MONEY CARD */
.money .card-header { background: linear-gradient(145deg, #2e7d32, #1b5e20); }
.money .card-body { background: linear-gradient(180deg, #e8f5e9, #c8e6c9); }
.money-value {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    color: #1b5e20;
    line-height: 1;
}
.money-symbol { font-size: 10px; color: #2e7d32; font-weight: 600; }

/* ACTION CARD */
.action .card-header { background: linear-gradient(145deg, #e53935, #c62828); }
.action .card-body { background: linear-gradient(180deg, #ffebee, #ffcdd2); }
.action-icon { font-size: 28px; }
.action-name { font-size: 7px; font-weight: 600; color: #c62828; text-transform: uppercase; margin-top: 2px; text-align: center; }

/* RENT CARD */
.rent .card-header { background: linear-gradient(145deg, #5c6bc0, #3949ab); }
.rent .card-body { background: linear-gradient(180deg, #e8eaf6, #c5cae9); }
.rent-icon { font-size: 24px; }
.rent-dots { display: flex; gap: 4px; margin-top: 4px; }
.rent-dot { width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }

/* BUILDING CARD */
.building .card-header { background: linear-gradient(145deg, #6d4c41, #4e342e); }
.building .card-body { background: linear-gradient(180deg, #efebe9, #d7ccc8); }
.building-icon { font-size: 30px; }
.building-label { font-size: 8px; color: #4e342e; font-weight: 600; }

/* PROPERTY CARD */
.property .rent-table {
    background: white;
    border-radius: 4px;
    padding: 3px 5px;
    font-size: 7px;
    color: #333;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
    width: 85%;
}
.rent-row { display: flex; justify-content: space-between; padding: 1px 0; }
.rent-row:not(:last-child) { border-bottom: 1px dotted #ddd; }

/* WILD CARD */
.wild .card-header {
    background: linear-gradient(90deg, #f44336, #ff9800, #ffeb3b, #4caf50, #2196f3, #9c27b0);
    background-size: 200% 100%;
    animation: rainbow 2s linear infinite;
}
@keyframes rainbow {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

/* FACE DOWN CARD */
.card-back {
    width: 70px;
    height: 100px;
    border-radius: 6px;
    background: 
        repeating-linear-gradient(45deg, #c62828, #c62828 5px, #b71c1c 5px, #b71c1c 10px);
    box-shadow: 0 3px 8px rgba(0,0,0,0.3);
    position: relative;
}
.card-back::before {
    content: '';
    position: absolute;
    inset: 5px;
    background: #d32f2f;
    border-radius: 3px;
    border: 2px solid #ffcdd2;
}
.card-back::after {
    content: 'M';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 700;
    color: #ffcdd2;
}

/* Random rotations for scattered look */
.card-back:nth-child(1) { transform: rotate(-3deg); }
.card-back:nth-child(2) { transform: rotate(2deg); }
.card-back:nth-child(3) { transform: rotate(-1deg); }
.card-back:nth-child(4) { transform: rotate(3deg); }
.card-back:nth-child(5) { transform: rotate(-2deg); }
.card-back:nth-child(6) { transform: rotate(1deg); }
.card-back:nth-child(7) { transform: rotate(-2deg); }
</style>
"""

def make_card_html(card) -> str:
    if card.kind == "money":
        return f'''
        <div class="card money">
            <div class="card-header"><span class="card-title">CASH</span></div>
            <div class="card-body">
                <div class="money-symbol">$</div>
                <div class="money-value">{card.value}</div>
                <div class="money-symbol">MILLION</div>
            </div>
            <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
        </div>'''
    
    elif card.kind == "property":
        color = card.active_color or (card.options[0] if card.options else "Brown")
        hex_color = COLOR_HEX.get(color, "#888")
        is_wild = getattr(card, 'is_wild', False)
        text_class = "dark" if color in ["Yellow", "Light Blue"] else ""
        
        if is_wild:
            opts = getattr(card, 'options', [])
            label = "/".join([o[:3] for o in opts[:2]]) if len(opts) <= 2 else "ANY"
            return f'''
            <div class="card property wild">
                <div class="card-header"><span class="card-title">WILD</span></div>
                <div class="card-body">
                    <div style="font-size:28px;">🃏</div>
                    <div style="font-size:8px;color:#666;margin-top:2px;">{label}</div>
                </div>
                <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
            </div>'''
        else:
            rents = RENT_VALUES.get(color, [1])
            rent_rows = "".join([f'<div class="rent-row"><span>{i+1}:</span><span>${r}M</span></div>' for i, r in enumerate(rents[:3])])
            name = color[:10]
            return f'''
            <div class="card property">
                <div class="card-header" style="background: linear-gradient(145deg, {hex_color}, {hex_color}cc);">
                    <span class="card-title {text_class}">{name}</span>
                </div>
                <div class="card-body">
                    <div class="rent-table">{rent_rows}</div>
                </div>
                <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
            </div>'''
    
    elif card.kind == "action":
        icons = {"DEAL_BREAKER": "💥", "SLY_DEAL": "🦊", "FORCED_DEAL": "🔄", "JUST_SAY_NO": "🚫",
                 "DEBT_COLLECTOR": "💰", "BIRTHDAY": "🎂", "DOUBLE_RENT": "✖️", "PASS_GO": "▶️"}
        icon = icons.get(getattr(card, 'action_id', ''), "⚡")
        name = card.name[:12]
        return f'''
        <div class="card action">
            <div class="card-header"><span class="card-title">ACTION</span></div>
            <div class="card-body">
                <div class="action-icon">{icon}</div>
                <div class="action-name">{name}</div>
            </div>
            <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
        </div>'''
    
    elif card.kind == "rent":
        rent_colors = getattr(card, 'rent_colors', [])
        if "Any" in rent_colors:
            dots = '<div style="font-size:9px;color:#3949ab;font-weight:600;">ANY</div>'
        else:
            dots = '<div class="rent-dots">' + "".join([f'<div class="rent-dot" style="background:{COLOR_HEX.get(c,"#888")};"></div>' for c in rent_colors[:2]]) + '</div>'
        return f'''
        <div class="card rent">
            <div class="card-header"><span class="card-title">RENT</span></div>
            <div class="card-body">
                <div class="rent-icon">🏦</div>
                {dots}
            </div>
            <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
        </div>'''
    
    elif card.kind == "building":
        btype = getattr(card, 'building_type', 'HOUSE')
        icon = "🏠" if btype == "HOUSE" else "🏨"
        return f'''
        <div class="card building">
            <div class="card-header"><span class="card-title">{btype}</span></div>
            <div class="card-body">
                <div class="building-icon">{icon}</div>
                <div class="building-label">+${3 if btype=="HOUSE" else 4}M</div>
            </div>
            <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
        </div>'''
    
    return '<div class="card"><div class="card-body">?</div></div>'

def render_cards(cards, height=155, center=False, scattered=False):
    if not cards:
        return
    cards_html = "".join([make_card_html(c) for c in cards])
    body_class = "center" if center else ("scattered" if scattered else "")
    html = f"<!DOCTYPE html><html><head>{CARD_STYLES}</head><body class='{body_class}'>{cards_html}</body></html>"
    components.html(html, height=height, scrolling=False)

def render_card_backs(count, height=120):
    if count <= 0:
        return
    backs = "".join(['<div class="card-back"></div>' for _ in range(count)])
    html = f"<!DOCTYPE html><html><head>{CARD_STYLES}</head><body class='center'>{backs}</body></html>"
    components.html(html, height=height, scrolling=False)


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Card:
    name: str
    value: int
    kind: str

@dataclass
class PropertyCard(Card):
    options: List[str] = field(default_factory=list)
    active_color: Optional[str] = None
    is_wild: bool = False
    def __post_init__(self):
        if self.active_color is None and self.options:
            self.active_color = self.options[0]

@dataclass
class ActionCard(Card):
    action_id: str = ""

@dataclass
class RentCard(Card):
    rent_colors: List[str] = field(default_factory=list)
    single_target: bool = False

@dataclass
class BuildingCard(Card):
    building_type: str = ""


# ============================================================
# DECK & PLAYER
# ============================================================

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self._build()
        random.shuffle(self.cards)

    def draw(self, n: int) -> List[Card]:
        return [self.cards.pop() for _ in range(min(n, len(self.cards)))]

    def discard_to_bottom(self, cards: List[Card]):
        self.cards = cards + self.cards

    def _build(self):
        props = [("Brown", 1, 2), ("Light Blue", 1, 3), ("Pink", 2, 3), ("Orange", 2, 3),
                 ("Red", 3, 3), ("Yellow", 3, 3), ("Green", 4, 3), ("Dark Blue", 4, 2),
                 ("Railroad", 2, 4), ("Utility", 2, 2)]
        for color, val, count in props:
            for _ in range(count):
                self.cards.append(PropertyCard(name=f"{color}", value=val, kind="property",
                                               options=[color], active_color=color))
        
        wilds = [("LtBlue/Brown", 1, ["Light Blue", "Brown"]), ("LtBlue/Rail", 1, ["Light Blue", "Railroad"]),
                 ("Pink/Orange", 2, ["Pink", "Orange"]), ("Pink/Orange", 2, ["Pink", "Orange"]),
                 ("Red/Yellow", 2, ["Red", "Yellow"]), ("Red/Yellow", 2, ["Red", "Yellow"]),
                 ("DkBlue/Green", 4, ["Dark Blue", "Green"]), ("Green/Rail", 4, ["Green", "Railroad"]),
                 ("Rail/Utility", 2, ["Railroad", "Utility"]), ("Any Color", 0, COLORS), ("Any Color", 0, COLORS)]
        for name, val, opts in wilds:
            self.cards.append(PropertyCard(name=name, value=val, kind="property", options=opts,
                                           active_color=opts[0], is_wild=True))
        
        for v, c in {1: 6, 2: 5, 3: 3, 4: 3, 5: 2, 10: 1}.items():
            for _ in range(c):
                self.cards.append(Card(name=f"${v}M", value=v, kind="money"))
        
        actions = [("Deal Breaker", 5, "DEAL_BREAKER", 2), ("Forced Deal", 3, "FORCED_DEAL", 3),
                   ("Sly Deal", 3, "SLY_DEAL", 3), ("Just Say No", 4, "JUST_SAY_NO", 3),
                   ("Debt Collector", 3, "DEBT_COLLECTOR", 3), ("It's My Birthday", 2, "BIRTHDAY", 3),
                   ("Double Rent", 1, "DOUBLE_RENT", 2), ("Pass Go", 1, "PASS_GO", 10)]
        for name, val, aid, count in actions:
            for _ in range(count):
                self.cards.append(ActionCard(name=name, value=val, kind="action", action_id=aid))
        
        for _ in range(3):
            self.cards.append(BuildingCard(name="House", value=3, kind="building", building_type="HOUSE"))
        for _ in range(2):
            self.cards.append(BuildingCard(name="Hotel", value=4, kind="building", building_type="HOTEL"))
        
        rents = [("LtBlue/Brown", 1, ["Light Blue", "Brown"], False, 2),
                 ("Pink/Orange", 1, ["Pink", "Orange"], False, 2),
                 ("Red/Yellow", 1, ["Red", "Yellow"], False, 2),
                 ("DkBlue/Green", 1, ["Dark Blue", "Green"], False, 2),
                 ("Rail/Utility", 1, ["Railroad", "Utility"], False, 2),
                 ("Any Color", 3, ["Any"], True, 3)]
        for name, val, cols, single, count in rents:
            for _ in range(count):
                self.cards.append(RentCard(name=name, value=val, kind="rent", rent_colors=cols, single_target=single))


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.bank: List[Card] = []
        self.props: Dict[str, List[PropertyCard]] = {}
        self.buildings: Dict[str, Dict[str, bool]] = {}
        self.double_rent_pending: bool = False

    def bank_total(self) -> int:
        return sum(c.value for c in self.bank)
    
    def total_table_value(self) -> int:
        """Total value of everything on table (bank + properties)"""
        prop_val = sum(c.value for cards in self.props.values() for c in cards)
        return self.bank_total() + prop_val

    def prop_count(self, color: str) -> int:
        return len(self.props.get(color, []))

    def has_full_set(self, color: str) -> bool:
        return self.prop_count(color) >= PROPERTY_SETS[color]

    def full_sets(self) -> List[str]:
        return [c for c in COLORS if self.has_full_set(c)]
    
    def has_anything_on_table(self) -> bool:
        return len(self.bank) > 0 or any(self.props.values())


# ============================================================
# GAME LOGIC
# ============================================================

def calc_rent(p: Player, color: str) -> int:
    count = p.prop_count(color)
    if count <= 0:
        return 0
    scale = RENT_VALUES.get(color, [1])
    base = scale[min(count, len(scale)) - 1]
    if p.has_full_set(color) and color not in ("Railroad", "Utility"):
        b = p.buildings.get(color, {})
        if b.get("house"):
            base += HOUSE_BONUS
        if b.get("hotel"):
            base += HOTEL_BONUS
    return base

def init_game(mode="vs_cpu", player_names=None):
    d = Deck()
    
    if mode == "vs_cpu":
        p1, p2 = Player("You"), Player("CPU")
        p2.is_cpu = True
    else:
        names = player_names or ["Player 1", "Player 2"]
        p1, p2 = Player(names[0]), Player(names[1])
        p1.is_cpu = False
        p2.is_cpu = False
    
    p1.hand.extend(d.draw(5))
    p2.hand.extend(d.draw(5))
    
    return {
        "deck": d, 
        "players": {p1.name: p1, p2.name: p2},
        "player_order": [p1.name, p2.name],
        "current_player_idx": 0,
        "plays_left": PLAYS_PER_TURN,
        "phase": "TURN_START", 
        "log": ["🎮 Game started!"], 
        "winner": None, 
        "round": 1,
        "mode": mode
    }

def get_current_player(g):
    return g["players"][g["player_order"][g["current_player_idx"]]]

def get_opponent(g):
    opp_idx = 1 - g["current_player_idx"]
    return g["players"][g["player_order"][opp_idx]]

def log(g, msg):
    g["log"].append(msg)

def draw_cards(g, player, count):
    drawn = g["deck"].draw(count)
    player.hand.extend(drawn)
    log(g, f"🎴 {player.name} drew {len(drawn)} cards")

def bank_card(g, player, idx):
    c = player.hand.pop(idx)
    player.bank.append(c)
    log(g, f"🏦 {player.name} banked {c.name}")
    g["plays_left"] -= 1

def play_property(g, player, idx, color_choice=None):
    c = player.hand.pop(idx)
    if hasattr(c, 'is_wild') and c.is_wild and color_choice:
        c.active_color = color_choice
    color = c.active_color or c.options[0]
    player.props.setdefault(color, []).append(c)
    log(g, f"🏠 {player.name} played {c.name}")
    g["plays_left"] -= 1

def collect_payment(g, payer: Player, payee: Player, amt: int):
    """
    FIXED: Collect payment from bank first, then from properties if needed.
    No change given - payer may overpay.
    """
    if not payer.has_anything_on_table():
        log(g, f"💸 {payer.name} has nothing to pay!")
        return 0
    
    paid = 0
    
    # First: pay from bank (highest value first)
    payer.bank.sort(key=lambda x: x.value, reverse=True)
    while paid < amt and payer.bank:
        c = payer.bank.pop(0)
        payee.bank.append(c)
        paid += c.value
    
    # Second: if still owe money, pay from properties
    if paid < amt:
        # Get all properties as a flat list
        all_props = []
        for color, cards in list(payer.props.items()):
            for card in cards:
                all_props.append((color, card))
        
        # Sort by value (pay highest value first to minimize cards lost)
        all_props.sort(key=lambda x: x[1].value, reverse=True)
        
        while paid < amt and all_props:
            color, card = all_props.pop(0)
            # Remove from payer
            payer.props[color].remove(card)
            if not payer.props[color]:
                del payer.props[color]
            # Add to payee's properties
            dest_color = card.active_color or color
            payee.props.setdefault(dest_color, []).append(card)
            paid += card.value
            log(g, f"🏠 {payer.name} paid {card.name} property!")
    
    log(g, f"💸 {payer.name} paid ${paid}M total (owed ${amt}M)")
    return paid

def play_action(g, player, idx):
    opp = get_opponent(g)
    c = player.hand.pop(idx)
    aid = c.action_id
    g["deck"].discard_to_bottom([c])
    g["plays_left"] -= 1
    
    if aid == "PASS_GO":
        extra = g["deck"].draw(2)
        player.hand.extend(extra)
        log(g, f"▶️ {player.name} - Pass Go! Drew 2 cards")
    elif aid == "DOUBLE_RENT":
        player.double_rent_pending = True
        log(g, f"✖️ {player.name} - Double Rent active!")
    elif aid == "BIRTHDAY":
        log(g, f"🎂 {player.name} - It's My Birthday! Collecting $2M")
        collect_payment(g, opp, player, 2)
    elif aid == "DEBT_COLLECTOR":
        log(g, f"💰 {player.name} - Debt Collector! Collecting $5M")
        collect_payment(g, opp, player, 5)
    elif aid == "SLY_DEAL":
        candidates = [(col, c) for col, cards in opp.props.items() 
                      if len(cards) < PROPERTY_SETS[col] for c in cards]
        if candidates:
            col, card = candidates[0]
            opp.props[col].remove(card)
            if not opp.props[col]:
                del opp.props[col]
            player.props.setdefault(card.active_color or col, []).append(card)
            log(g, f"🦊 {player.name} stole {card.name}!")
        else:
            log(g, f"🦊 Nothing to steal!")
    elif aid == "DEAL_BREAKER":
        full = opp.full_sets()
        if full:
            color = full[0]
            stolen = opp.props.pop(color, [])
            player.props.setdefault(color, []).extend(stolen)
            log(g, f"💥 {player.name} stole {color} set!")
        else:
            log(g, f"💥 No complete sets to steal!")
    else:
        log(g, f"⚡ {player.name} played {c.name}")

def play_rent(g, player, idx, color):
    opp = get_opponent(g)
    c = player.hand.pop(idx)
    amt = calc_rent(player, color)
    
    if player.double_rent_pending:
        amt *= 2
        player.double_rent_pending = False
        log(g, f"✖️ Double rent applied!")
    
    g["deck"].discard_to_bottom([c])
    g["plays_left"] -= 1
    
    log(g, f"🏦 {player.name} charges ${amt}M rent for {color}!")
    collect_payment(g, opp, player, amt)

def check_win(g) -> bool:
    for name, p in g["players"].items():
        if len(p.full_sets()) >= 3:
            g["winner"] = name
            return True
    return False

def end_turn(g):
    """End current player's turn and switch to next player"""
    current = get_current_player(g)
    
    # Discard excess cards
    while len(current.hand) > MAX_HAND:
        idx = min(range(len(current.hand)), key=lambda i: current.hand[i].value)
        c = current.hand.pop(idx)
        g["deck"].discard_to_bottom([c])
        log(g, f"📤 {current.name} discarded {c.name}")
    
    # Switch to next player
    g["current_player_idx"] = 1 - g["current_player_idx"]
    g["phase"] = "TURN_START"
    g["plays_left"] = PLAYS_PER_TURN
    
    if g["current_player_idx"] == 0:
        g["round"] += 1

def cpu_turn(g):
    """CPU plays automatically"""
    cpu = get_current_player(g)
    
    # Draw
    draw_count = 5 if len(cpu.hand) == 0 else 2
    draw_cards(g, cpu, draw_count)
    
    plays = 3
    while plays > 0 and cpu.hand:
        # Play properties first
        prop_idx = next((i for i, c in enumerate(cpu.hand) if c.kind == "property"), -1)
        if prop_idx != -1:
            play_property(g, cpu, prop_idx)
            plays -= 1
            continue
        
        # Bank money
        money_idx = next((i for i, c in enumerate(cpu.hand) if c.kind == "money"), -1)
        if money_idx != -1:
            c = cpu.hand.pop(money_idx)
            cpu.bank.append(c)
            plays -= 1
            continue
        
        # Use good actions
        action_idx = next((i for i, c in enumerate(cpu.hand) 
                          if c.kind == "action" and getattr(c, 'action_id', '') in ['PASS_GO', 'BIRTHDAY', 'DEBT_COLLECTOR']), -1)
        if action_idx != -1:
            play_action(g, cpu, action_idx)
            plays -= 1
            continue
        
        # Bank anything else
        if cpu.hand:
            c = cpu.hand.pop(0)
            cpu.bank.append(c)
            plays -= 1
    
    log(g, f"🤖 CPU finished turn")
    end_turn(g)


# ============================================================
# STREAMLIT UI
# ============================================================

# Initialize game
if "game" not in st.session_state:
    st.session_state.game = None
    st.session_state.game_mode = None

# Mode selection
if st.session_state.game is None:
    st.markdown("""
    <div style="text-align:center; padding:40px 0;">
        <div style="display:inline-block; background:linear-gradient(145deg,#c41e3a,#8b0000); 
                    padding:20px 50px; border-radius:15px; border:4px solid #ffd700;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <div style="font-family:'Playfair Display',serif; font-size:48px; font-weight:900; color:#fff;
                        text-shadow:3px 3px 0 #000;">MONOPOLY</div>
            <div style="font-family:'Poppins',sans-serif; font-size:24px; font-weight:700; color:#ffd700;
                        letter-spacing:10px;">DEAL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 VS Computer")
        st.write("Play against the CPU")
        if st.button("▶️ Play vs CPU", use_container_width=True, key="cpu_mode"):
            st.session_state.game = init_game("vs_cpu")
            st.session_state.game_mode = "vs_cpu"
            st.rerun()
    
    with col2:
        st.markdown("### 👥 2 Players (Local)")
        st.write("Pass & play on same device")
        p1_name = st.text_input("Player 1 name:", value="Player 1")
        p2_name = st.text_input("Player 2 name:", value="Player 2")
        if st.button("▶️ Start 2P Game", use_container_width=True, key="2p_mode"):
            st.session_state.game = init_game("local_2p", [p1_name, p2_name])
            st.session_state.game_mode = "local_2p"
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 🌐 Play Online with Friends
    1. Deploy this app to **Streamlit Cloud** (free)
    2. Share the link with friends
    3. They can play on their own device!
    
    See README.md for deployment instructions.
    """)
    
    st.stop()

# Game is active
g = st.session_state.game
current_player = get_current_player(g)
opponent = get_opponent(g)
is_cpu_turn = getattr(current_player, 'is_cpu', False)

# Header
st.markdown(f"""
<div style="text-align:center; padding:10px 0 20px;">
    <div style="display:inline-block; background:linear-gradient(145deg,#c41e3a,#8b0000); 
                padding:10px 30px; border-radius:10px; border:3px solid #ffd700;
                box-shadow: 0 5px 15px rgba(0,0,0,0.4);">
        <span style="font-family:'Playfair Display',serif; font-size:28px; font-weight:900; color:#fff;
                    text-shadow:2px 2px 0 #000;">MONOPOLY DEAL</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Status bar
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🎯 Round", g["round"])
c2.metric("⚡ Plays", g["plays_left"])
c3.metric("🃏 Deck", len(g["deck"].cards))

p1_name = g["player_order"][0]
p2_name = g["player_order"][1]
p1_sets = len(g["players"][p1_name].full_sets())
p2_sets = len(g["players"][p2_name].full_sets())
c4.metric(f"🏆 {p1_name[:8]}", f"{p1_sets}/3")
c5.metric(f"{'🤖' if getattr(g['players'][p2_name], 'is_cpu', False) else '👤'} {p2_name[:8]}", f"{p2_sets}/3")

# Current turn indicator
turn_color = "#4CAF50" if current_player.name == g["player_order"][0] else "#2196F3"
st.markdown(f"""
<div style="text-align:center; padding:10px; margin:10px 0; 
            background:linear-gradient(145deg, {turn_color}40, {turn_color}20); 
            border-radius:10px; border:2px solid {turn_color};">
    <span style="font-size:18px; font-weight:bold; color:#2d1810;">
        🎲 {current_player.name}'s Turn
    </span>
</div>
""", unsafe_allow_html=True)

st.divider()

# Winner check
if g["winner"]:
    if g["winner"] == g["player_order"][0]:
        st.balloons()
    st.success(f"## 🏆 {g['winner']} WINS! 🏆")
    st.markdown(f"*Won in {g['round']} rounds with 3 complete property sets!*")
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.game = None
        st.rerun()
    st.stop()

# Turn logic
if g["phase"] == "TURN_START":
    draw_count = 5 if len(current_player.hand) == 0 else 2
    draw_cards(g, current_player, draw_count)
    g["phase"] = "PLAY"
    g["plays_left"] = PLAYS_PER_TURN
    st.rerun()

# CPU auto-play
if is_cpu_turn:
    cpu_turn(g)
    check_win(g)
    st.rerun()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Menu")
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.game = None
        st.rerun()
    st.divider()
    st.markdown("### 📜 Log")
    for entry in reversed(g["log"][-15:]):
        st.caption(entry)

# Opponent area
st.markdown(f"### {'🤖' if getattr(opponent, 'is_cpu', False) else '👤'} {opponent.name}'s Hand")
if getattr(opponent, 'is_cpu', False):
    render_card_backs(len(opponent.hand))
else:
    st.info(f"🙈 {len(opponent.hand)} cards (hidden)")

st.divider()

# Tables side by side
left, right = st.columns(2)

with left:
    st.markdown(f"### {'🤖' if getattr(opponent, 'is_cpu', False) else '👤'} {opponent.name}'s Table")
    st.markdown(f"**🏦 Bank:** ${opponent.bank_total()}M")
    if opponent.bank:
        render_cards(opponent.bank, height=150, scattered=True)
    for color in COLORS:
        cards = opponent.props.get(color, [])
        if cards:
            badge = "✅" if opponent.has_full_set(color) else ""
            st.markdown(f"**{color}** {badge}")
            render_cards(cards, height=150)

with right:
    st.markdown(f"### 👤 {current_player.name}'s Table")
    st.markdown(f"**🏦 Bank:** ${current_player.bank_total()}M")
    if current_player.bank:
        render_cards(current_player.bank, height=150, scattered=True)
    for color in COLORS:
        cards = current_player.props.get(color, [])
        if cards:
            badge = "✅" if current_player.has_full_set(color) else ""
            st.markdown(f"**{color}** {badge}")
            render_cards(cards, height=150)

st.divider()

# Current player's hand
st.markdown(f"### 🃏 {current_player.name}'s Hand ({len(current_player.hand)} cards)")

if g["plays_left"] <= 0:
    st.warning("⚠️ No plays left! Click **End Turn**.")

# End turn button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✅ END TURN", use_container_width=True, type="primary"):
        if len(current_player.hand) > MAX_HAND:
            st.error(f"❌ Discard to {MAX_HAND} cards first!")
        else:
            end_turn(g)
            check_win(g)
            st.rerun()

# Display hand with integrated buttons
if current_player.hand:
    disabled = g["plays_left"] <= 0
    
    # Create columns for each card (up to 7 cards max)
    num_cards = len(current_player.hand)
    cols = st.columns(min(num_cards, 7))
    
    for idx, card in enumerate(current_player.hand):
        col_idx = idx % 7
        with cols[col_idx]:
            # Render single card
            card_html = make_card_html(card)
            full_html = f"""<!DOCTYPE html><html><head>{CARD_STYLES}</head>
            <body style="justify-content:center; padding:5px;">{card_html}</body></html>"""
            components.html(full_html, height=160, scrolling=False)
            
            # Buttons directly under the card
            play_label = "▶️" if card.kind in ["action", "rent", "property"] else "💵"
            if st.button(play_label, key=f"play_{idx}", disabled=disabled, use_container_width=True):
                if card.kind == "money":
                    c = current_player.hand.pop(idx)
                    current_player.bank.append(c)
                    g["plays_left"] -= 1
                    log(g, f"💵 Banked ${c.value}M")
                elif card.kind == "property":
                    play_property(g, current_player, idx)
                elif card.kind == "rent":
                    if "Any" in card.rent_colors:
                        valid = list(current_player.props.keys())
                    else:
                        valid = [c for c in card.rent_colors if c in current_player.props]
                    if valid:
                        play_rent(g, current_player, idx, valid[0])
                    else:
                        st.toast("Need properties first!")
                elif card.kind == "action":
                    play_action(g, current_player, idx)
                elif card.kind == "building":
                    valid = [c for c in current_player.full_sets() if c not in ("Railroad", "Utility")]
                    if valid:
                        bc = current_player.hand.pop(idx)
                        current_player.buildings.setdefault(valid[0], {})[bc.building_type.lower()] = True
                        g["plays_left"] -= 1
                        log(g, f"🏗️ Built {bc.building_type}")
                    else:
                        st.toast("Need a full set!")
                st.rerun()
            
            if st.button("🏦", key=f"bank_{idx}", disabled=disabled, use_container_width=True):
                bank_card(g, current_player, idx)
                st.rerun()
else:
    st.info("Hand empty!")