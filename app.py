"""
Monopoly Deal - Premium 3D Edition (Streamlit)
Features: CSS 3D transforms, perspective effects, animations, premium card designs
"""

import streamlit as st
import streamlit.components.v1 as components
import random
import os
import base64
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

st.set_page_config(page_title="Monopoly Deal 3D", layout="wide", initial_sidebar_state="collapsed")

# ============================================================
# 3D CSS STYLES
# ============================================================

def inject_3d_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@400;500;600;700&family=JetBrains+Mono:wght@600&display=swap');
    
    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* ===== 3D TABLE BACKGROUND ===== */
    .stApp {
        background: 
            radial-gradient(ellipse at 50% 30%, rgba(26, 71, 42, 0.9) 0%, transparent 70%),
            radial-gradient(ellipse at 80% 80%, rgba(139, 69, 19, 0.15) 0%, transparent 50%),
            linear-gradient(180deg, #0a1f12 0%, #1a472a 40%, #0d2818 100%);
        background-attachment: fixed;
        perspective: 1500px;
        min-height: 100vh;
    }
    
    /* Felt texture */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        opacity: 0.04;
        pointer-events: none;
        z-index: 0;
    }
    
    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3 { 
        font-family: 'Playfair Display', serif !important; 
        color: #ffd700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    p, span, div, .stMarkdown { 
        font-family: 'Poppins', sans-serif !important;
        color: #f0f0f0 !important;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        background: linear-gradient(145deg, #ffd700, #ff8c00) !important;
        color: #1a1a1a !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.5) !important;
    }
    .stButton > button:disabled {
        background: linear-gradient(145deg, #444, #333) !important;
        color: #888 !important;
        box-shadow: none !important;
    }
    
    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #ffd700 !important;
        font-size: 28px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #aaa !important;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); border-radius: 5px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #ffd700, #ff8c00); border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

inject_3d_styles()

# ============================================================
# 3D CARD RENDERER (HTML Component)
# ============================================================

CARD_3D_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Poppins:wght@400;600;700&family=JetBrains+Mono:wght@600&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Poppins', sans-serif;
    background: transparent;
    perspective: 1000px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 10px;
    justify-content: flex-start;
    align-items: flex-end;
}

body.center { justify-content: center; }

/* ===== 3D CARD ===== */
.card-3d {
    width: 110px;
    height: 160px;
    position: relative;
    transform-style: preserve-3d;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    cursor: pointer;
}

.card-3d:hover {
    transform: translateY(-15px) rotateX(10deg) scale(1.08);
    z-index: 100;
}

.card-face {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 12px;
    backface-visibility: hidden;
    box-shadow: 
        0 5px 20px rgba(0,0,0,0.4),
        0 0 0 1px rgba(255,255,255,0.1) inset,
        0 2px 0 rgba(255,255,255,0.2) inset;
    overflow: hidden;
    background: linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%);
}

/* Card shine effect */
.card-face::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        45deg,
        transparent 40%,
        rgba(255,255,255,0.3) 50%,
        transparent 60%
    );
    transform: rotate(45deg);
    transition: all 0.5s;
    opacity: 0;
}

.card-3d:hover .card-face::before {
    opacity: 1;
    animation: shine 0.6s ease-out;
}

@keyframes shine {
    0% { transform: translateX(-100%) rotate(45deg); }
    100% { transform: translateX(100%) rotate(45deg); }
}

/* ===== CARD HEADER ===== */
.card-header {
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 5px 8px;
    position: relative;
}

.card-header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 8px;
    right: 8px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);
}

.card-title {
    font-family: 'Poppins', sans-serif;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: white;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    text-align: center;
    line-height: 1.2;
}

.card-title.dark { color: #1a1a1a; text-shadow: none; }

/* ===== CARD BODY ===== */
.card-body {
    height: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8px;
    background: linear-gradient(180deg, #fafafa 0%, #f0f0f0 100%);
}

/* ===== CARD FOOTER ===== */
.card-footer {
    height: 35px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(180deg, #f8f8f8, #e8e8e8);
    border-top: 1px solid #ddd;
}

.value-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #2e7d32;
    background: linear-gradient(145deg, #e8f5e9, #c8e6c9);
    padding: 4px 14px;
    border-radius: 15px;
    border: 2px solid #a5d6a7;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* ===== MONEY CARD ===== */
.money .card-header {
    background: linear-gradient(145deg, #43a047, #2e7d32);
}

.money .card-body {
    background: 
        repeating-linear-gradient(45deg, transparent, transparent 8px, rgba(46,125,50,0.03) 8px, rgba(46,125,50,0.03) 16px),
        linear-gradient(180deg, #f1f8e9 0%, #dcedc8 100%);
}

.money-value {
    font-family: 'Playfair Display', serif;
    font-size: 44px;
    font-weight: 900;
    color: #2e7d32;
    text-shadow: 2px 2px 0 rgba(46,125,50,0.2);
    line-height: 1;
}

.money-label {
    font-size: 10px;
    font-weight: 600;
    color: #558b2f;
    letter-spacing: 3px;
    margin-top: 2px;
}

/* ===== ACTION CARD ===== */
.action .card-header {
    background: linear-gradient(145deg, #ef5350, #c62828);
}

.action .card-body {
    background: linear-gradient(180deg, #ffebee 0%, #ffcdd2 100%);
}

.action-icon {
    font-size: 34px;
    filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.2));
}

.action-name {
    font-size: 9px;
    font-weight: 600;
    color: #c62828;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 4px;
    text-align: center;
}

/* ===== RENT CARD ===== */
.rent .card-header {
    background: linear-gradient(145deg, #7e57c2, #5e35b1);
}

.rent .card-body {
    background: linear-gradient(180deg, #ede7f6 0%, #d1c4e9 100%);
}

.rent-icon { font-size: 32px; }

.rent-dots {
    display: flex;
    gap: 6px;
    margin-top: 8px;
}

.rent-dot {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3), inset 0 -2px 5px rgba(0,0,0,0.2);
}

/* ===== BUILDING CARD ===== */
.building .card-header {
    background: linear-gradient(145deg, #8d6e63, #5d4037);
}

.building .card-body {
    background: linear-gradient(180deg, #efebe9 0%, #d7ccc8 100%);
}

.building-icon { font-size: 38px; }
.building-label { font-size: 9px; color: #5d4037; font-weight: 600; margin-top: 4px; }

/* ===== PROPERTY CARD ===== */
.property .rent-table {
    background: white;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 9px;
    color: #333;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.1), 0 1px 2px rgba(255,255,255,0.8);
    width: 90%;
}

.rent-row {
    display: flex;
    justify-content: space-between;
    padding: 2px 0;
    border-bottom: 1px dotted #ccc;
}

.rent-row:last-child { border-bottom: none; }

/* ===== WILD CARD ===== */
.wild .card-header {
    background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3, #54a0ff, #5f27cd);
    background-size: 300% 100%;
    animation: rainbow 3s linear infinite;
}

@keyframes rainbow {
    0% { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}

.wild-label {
    font-size: 9px;
    font-weight: 600;
    color: #666;
    margin-top: 5px;
}

/* ===== FACE DOWN CARD ===== */
.card-back {
    width: 85px;
    height: 120px;
    border-radius: 10px;
    position: relative;
    transform-style: preserve-3d;
    transition: all 0.3s ease;
    cursor: default;
}

.card-back:hover {
    transform: translateY(-5px) rotateY(5deg);
}

.card-back .card-face {
    background: 
        repeating-linear-gradient(45deg, #c62828, #c62828 8px, #b71c1c 8px, #b71c1c 16px);
    display: flex;
    align-items: center;
    justify-content: center;
}

.card-back .card-face::after {
    content: '';
    position: absolute;
    inset: 8px;
    background: linear-gradient(145deg, #d32f2f, #c62828);
    border-radius: 6px;
    border: 3px solid #ffcdd2;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.3);
}

.card-back-logo {
    position: relative;
    z-index: 1;
    font-family: 'Playfair Display', serif;
    font-size: 32px;
    font-weight: 900;
    color: #ffcdd2;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
}

/* ===== ANIMATIONS ===== */
@keyframes dealCard {
    0% { transform: translateY(-100px) rotateX(90deg) scale(0.5); opacity: 0; }
    100% { transform: translateY(0) rotateX(0) scale(1); opacity: 1; }
}

.card-3d {
    animation: dealCard 0.5s ease-out backwards;
}

.card-3d:nth-child(1) { animation-delay: 0s; }
.card-3d:nth-child(2) { animation-delay: 0.05s; }
.card-3d:nth-child(3) { animation-delay: 0.1s; }
.card-3d:nth-child(4) { animation-delay: 0.15s; }
.card-3d:nth-child(5) { animation-delay: 0.2s; }
.card-3d:nth-child(6) { animation-delay: 0.25s; }
.card-3d:nth-child(7) { animation-delay: 0.3s; }
</style>
"""

def make_card_html(card) -> str:
    """Generate 3D card HTML"""
    if card.kind == "money":
        return f'''
        <div class="card-3d">
            <div class="card-face money">
                <div class="card-header"><span class="card-title">CASH</span></div>
                <div class="card-body">
                    <div class="money-value">{card.value}</div>
                    <div class="money-label">MILLION</div>
                </div>
                <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
            </div>
        </div>'''
    
    elif card.kind == "property":
        color = card.active_color or (card.options[0] if card.options else "Brown")
        hex_color = COLOR_HEX.get(color, "#888")
        is_wild = getattr(card, 'is_wild', False)
        text_class = "dark" if color in ["Yellow", "Light Blue"] else ""
        
        if is_wild:
            opts = getattr(card, 'options', [])
            label = " / ".join(opts[:2]) if len(opts) <= 2 else "ANY"
            return f'''
            <div class="card-3d">
                <div class="card-face property wild">
                    <div class="card-header"><span class="card-title">WILD</span></div>
                    <div class="card-body">
                        <div style="font-size:36px;">🃏</div>
                        <div class="wild-label">{label}</div>
                    </div>
                    <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
                </div>
            </div>'''
        else:
            rents = RENT_VALUES.get(color, [1])
            rent_rows = "".join([f'<div class="rent-row"><span>{i+1} prop:</span><span>${r}M</span></div>' for i, r in enumerate(rents)])
            name = card.name.replace(" Property", "")[:12]
            return f'''
            <div class="card-3d">
                <div class="card-face property">
                    <div class="card-header" style="background: linear-gradient(145deg, {hex_color}, {hex_color}cc);">
                        <span class="card-title {text_class}">{name}</span>
                    </div>
                    <div class="card-body">
                        <div class="rent-table">{rent_rows}</div>
                    </div>
                    <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
                </div>
            </div>'''
    
    elif card.kind == "action":
        icons = {"DEAL_BREAKER": "💥", "SLY_DEAL": "🦊", "FORCED_DEAL": "🔄", "JUST_SAY_NO": "🚫",
                 "DEBT_COLLECTOR": "💰", "BIRTHDAY": "🎂", "DOUBLE_RENT": "✖️", "PASS_GO": "▶️"}
        icon = icons.get(getattr(card, 'action_id', ''), "⚡")
        return f'''
        <div class="card-3d">
            <div class="card-face action">
                <div class="card-header"><span class="card-title">ACTION</span></div>
                <div class="card-body">
                    <div class="action-icon">{icon}</div>
                    <div class="action-name">{card.name}</div>
                </div>
                <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
            </div>
        </div>'''
    
    elif card.kind == "rent":
        rent_colors = getattr(card, 'rent_colors', [])
        if "Any" in rent_colors:
            dots = '<div style="font-size:11px;color:#5e35b1;font-weight:600;">ANY COLOR</div>'
        else:
            dots = '<div class="rent-dots">' + "".join([f'<div class="rent-dot" style="background: {COLOR_HEX.get(c,"#888")};"></div>' for c in rent_colors[:2]]) + '</div>'
        return f'''
        <div class="card-3d">
            <div class="card-face rent">
                <div class="card-header"><span class="card-title">RENT</span></div>
                <div class="card-body">
                    <div class="rent-icon">🏦</div>
                    {dots}
                </div>
                <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
            </div>
        </div>'''
    
    elif card.kind == "building":
        btype = getattr(card, 'building_type', 'HOUSE')
        icon = "🏠" if btype == "HOUSE" else "🏨"
        label = "+$3M Rent" if btype == "HOUSE" else "+$4M Rent"
        return f'''
        <div class="card-3d">
            <div class="card-face building">
                <div class="card-header"><span class="card-title">{btype}</span></div>
                <div class="card-body">
                    <div class="building-icon">{icon}</div>
                    <div class="building-label">{label}</div>
                </div>
                <div class="card-footer"><span class="value-badge">${card.value}M</span></div>
            </div>
        </div>'''
    
    return '<div class="card-3d"><div class="card-face"><div class="card-body">?</div></div></div>'

def render_cards_3d(cards, height=185, center=False):
    """Render cards with 3D effects"""
    if not cards:
        return
    cards_html = "".join([make_card_html(c) for c in cards])
    body_class = "center" if center else ""
    html = f"<!DOCTYPE html><html><head>{CARD_3D_STYLES}</head><body class='{body_class}'>{cards_html}</body></html>"
    components.html(html, height=height, scrolling=False)

def render_card_backs_3d(count, height=145):
    """Render face-down cards with 3D effects"""
    if count <= 0:
        return
    backs = "".join([f'''
        <div class="card-back">
            <div class="card-face">
                <span class="card-back-logo">M</span>
            </div>
        </div>
    ''' for _ in range(count)])
    html = f"<!DOCTYPE html><html><head>{CARD_3D_STYLES}</head><body class='center'>{backs}</body></html>"
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
        # Properties
        props = [("Brown", 1, 2), ("Light Blue", 1, 3), ("Pink", 2, 3), ("Orange", 2, 3),
                 ("Red", 3, 3), ("Yellow", 3, 3), ("Green", 4, 3), ("Dark Blue", 4, 2),
                 ("Railroad", 2, 4), ("Utility", 2, 2)]
        for color, val, count in props:
            for _ in range(count):
                self.cards.append(PropertyCard(name=f"{color} Property", value=val, kind="property",
                                               options=[color], active_color=color))
        
        # Wilds
        wilds = [("LtBlue/Brown", 1, ["Light Blue", "Brown"]), ("LtBlue/Rail", 1, ["Light Blue", "Railroad"]),
                 ("Pink/Orange", 2, ["Pink", "Orange"]), ("Pink/Orange", 2, ["Pink", "Orange"]),
                 ("Red/Yellow", 2, ["Red", "Yellow"]), ("Red/Yellow", 2, ["Red", "Yellow"]),
                 ("DkBlue/Green", 4, ["Dark Blue", "Green"]), ("Green/Rail", 4, ["Green", "Railroad"]),
                 ("Rail/Utility", 2, ["Railroad", "Utility"]), ("Any Color", 0, COLORS), ("Any Color", 0, COLORS)]
        for name, val, opts in wilds:
            self.cards.append(PropertyCard(name=name, value=val, kind="property", options=opts,
                                           active_color=opts[0], is_wild=True))
        
        # Money
        for v, c in {1: 6, 2: 5, 3: 3, 4: 3, 5: 2, 10: 1}.items():
            for _ in range(c):
                self.cards.append(Card(name=f"${v}M", value=v, kind="money"))
        
        # Actions
        actions = [("Deal Breaker", 5, "DEAL_BREAKER", 2), ("Forced Deal", 3, "FORCED_DEAL", 3),
                   ("Sly Deal", 3, "SLY_DEAL", 3), ("Just Say No", 4, "JUST_SAY_NO", 3),
                   ("Debt Collector", 3, "DEBT_COLLECTOR", 3), ("It's My Birthday", 2, "BIRTHDAY", 3),
                   ("Double Rent", 1, "DOUBLE_RENT", 2), ("Pass Go", 1, "PASS_GO", 10)]
        for name, val, aid, count in actions:
            for _ in range(count):
                self.cards.append(ActionCard(name=name, value=val, kind="action", action_id=aid))
        
        # Buildings
        for _ in range(3):
            self.cards.append(BuildingCard(name="House", value=3, kind="building", building_type="HOUSE"))
        for _ in range(2):
            self.cards.append(BuildingCard(name="Hotel", value=4, kind="building", building_type="HOTEL"))
        
        # Rent
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

    def prop_count(self, color: str) -> int:
        return len(self.props.get(color, []))

    def has_full_set(self, color: str) -> bool:
        return self.prop_count(color) >= PROPERTY_SETS[color]

    def full_sets(self) -> List[str]:
        return [c for c in COLORS if self.has_full_set(c)]


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

def init_game():
    d = Deck()
    h, c = Player("You"), Player("CPU")
    h.hand.extend(d.draw(5))
    c.hand.extend(d.draw(5))
    return {
        "deck": d, "players": {"You": h, "CPU": c},
        "turn": "You", "plays_left": PLAYS_PER_TURN,
        "phase": "TURN_START", "log": ["🎮 Game started!"], "winner": None, "round": 1
    }

def log(g, msg):
    g["log"].append(msg)

def draw_cards(g, name, count):
    p = g["players"][name]
    drawn = g["deck"].draw(count)
    p.hand.extend(drawn)
    log(g, f"🎴 {name} drew {len(drawn)} cards")

def bank_card(g, name, idx):
    p = g["players"][name]
    c = p.hand.pop(idx)
    p.bank.append(c)
    log(g, f"🏦 {name} banked {c.name}")
    g["plays_left"] -= 1

def play_property(g, name, idx, color_choice=None):
    p = g["players"][name]
    c = p.hand.pop(idx)
    if hasattr(c, 'is_wild') and c.is_wild and color_choice:
        c.active_color = color_choice
    color = c.active_color or c.options[0]
    p.props.setdefault(color, []).append(c)
    log(g, f"🏠 {name} played {c.name}")
    g["plays_left"] -= 1

def auto_pay(g, payer: Player, payee: Player, amt: int):
    paid = 0
    payer.bank.sort(key=lambda x: x.value, reverse=True)
    while paid < amt and payer.bank:
        c = payer.bank.pop(0)
        payee.bank.append(c)
        paid += c.value
    log(g, f"💸 {payer.name} paid ${paid}M")

def play_action(g, name, idx):
    p = g["players"][name]
    opp = g["players"]["CPU" if name == "You" else "You"]
    c = p.hand.pop(idx)
    aid = c.action_id
    g["deck"].discard_to_bottom([c])
    g["plays_left"] -= 1
    
    if aid == "PASS_GO":
        extra = g["deck"].draw(2)
        p.hand.extend(extra)
        log(g, f"▶️ Pass Go! Drew 2 cards")
    elif aid == "DOUBLE_RENT":
        p.double_rent_pending = True
        log(g, f"✖️ Double Rent activated!")
    elif aid == "BIRTHDAY":
        log(g, f"🎂 Birthday! Everyone pays $2M")
        auto_pay(g, opp, p, 2)
    elif aid == "DEBT_COLLECTOR":
        log(g, f"💰 Debt Collector - $5M")
        auto_pay(g, opp, p, 5)
    elif aid == "SLY_DEAL":
        candidates = [(col, c) for col, cards in opp.props.items() 
                      if len(cards) < PROPERTY_SETS[col] for c in cards]
        if candidates:
            col, card = candidates[0]
            opp.props[col].remove(card)
            if not opp.props[col]:
                del opp.props[col]
            p.props.setdefault(card.active_color or col, []).append(card)
            log(g, f"🦊 Stole {card.name}!")
        else:
            log(g, f"🦊 Nothing to steal")
    elif aid == "DEAL_BREAKER":
        full = opp.full_sets()
        if full:
            color = full[0]
            stolen = opp.props.pop(color, [])
            p.props.setdefault(color, []).extend(stolen)
            log(g, f"💥 Stole {color} set!")
        else:
            log(g, f"💥 No sets to steal")
    else:
        log(g, f"⚡ {c.name}")

def check_win(g) -> bool:
    for n, p in g["players"].items():
        if len(p.full_sets()) >= 3:
            g["winner"] = n
            return True
    return False

def cpu_turn(g):
    p = g["players"]["CPU"]
    
    # Draw 2 cards (or 5 if hand is empty)
    draw_count = 5 if len(p.hand) == 0 else 2
    drawn = g["deck"].draw(draw_count)
    p.hand.extend(drawn)
    log(g, f"🤖 CPU drew {len(drawn)} cards (has {len(p.hand)} now)")
    
    plays = 3
    actions_taken = []
    
    while plays > 0 and p.hand:
        # Priority 1: Play properties
        prop_idx = next((i for i, c in enumerate(p.hand) if c.kind == "property"), -1)
        if prop_idx != -1:
            card = p.hand[prop_idx]
            play_property(g, "CPU", prop_idx)
            actions_taken.append(f"played {card.name}")
            plays -= 1
            continue
        
        # Priority 2: Bank money
        money_idx = next((i for i, c in enumerate(p.hand) if c.kind == "money"), -1)
        if money_idx != -1:
            card = p.hand[money_idx]
            p.hand.pop(money_idx)
            p.bank.append(card)
            actions_taken.append(f"banked ${card.value}M")
            plays -= 1
            continue
        
        # Priority 3: Play action cards
        action_idx = next((i for i, c in enumerate(p.hand) if c.kind == "action" and getattr(c, 'action_id', '') in ['PASS_GO', 'BIRTHDAY', 'DEBT_COLLECTOR']), -1)
        if action_idx != -1:
            card = p.hand[action_idx]
            play_action(g, "CPU", action_idx)
            actions_taken.append(f"used {card.name}")
            plays -= 1
            continue
        
        # Priority 4: Bank anything else
        if p.hand:
            card = p.hand.pop(0)
            p.bank.append(card)
            actions_taken.append(f"banked {card.name}")
            plays -= 1
    
    # Log CPU actions
    if actions_taken:
        log(g, f"🤖 CPU: {', '.join(actions_taken[:3])}")
    
    # Discard excess cards
    while len(p.hand) > MAX_HAND:
        idx = min(range(len(p.hand)), key=lambda i: p.hand[i].value)
        c = p.hand.pop(idx)
        g["deck"].discard_to_bottom([c])
        log(g, f"🤖 CPU discarded {c.name}")
    
    g["round"] += 1
    g["turn"] = "You"
    g["phase"] = "TURN_START"
    g["plays_left"] = PLAYS_PER_TURN
    log(g, f"🎯 Round {g['round']} - Your turn!")


# ============================================================
# STREAMLIT UI
# ============================================================

if "game" not in st.session_state:
    st.session_state.game = init_game()

g = st.session_state.game
human = g["players"]["You"]
cpu = g["players"]["CPU"]

# ===== HEADER =====
st.markdown("""
<div style="text-align:center; padding:20px 0 30px;">
    <div style="display:inline-block; background:linear-gradient(145deg,#c41e3a 0%,#8b0000 100%); 
                padding:15px 50px; border-radius:15px; border:4px solid #ffd700;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5), inset 0 2px 0 rgba(255,255,255,0.2);">
        <div style="font-family:'Playfair Display',serif; font-size:42px; font-weight:900; color:#fff;
                    text-shadow:3px 3px 0 #000, -1px -1px 0 #000; letter-spacing:3px;">MONOPOLY</div>
        <div style="font-family:'Poppins',sans-serif; font-size:20px; font-weight:700; color:#ffd700;
                    letter-spacing:10px; text-shadow:2px 2px 0 #000;">DEAL</div>
    </div>
    <div style="margin-top:10px; color:#888; font-size:13px; letter-spacing:2px;">
        ✨ PREMIUM 3D EDITION ✨
    </div>
</div>
""", unsafe_allow_html=True)

# ===== STATUS BAR =====
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🎯 Round", g["round"])
c2.metric("⚡ Plays", g["plays_left"])
c3.metric("🃏 Deck", len(g["deck"].cards))
c4.metric("🏆 You", f"{len(human.full_sets())}/3")
c5.metric("🤖 CPU", f"{len(cpu.full_sets())}/3")

st.divider()

# ===== WINNER =====
if g["winner"]:
    if g["winner"] == "You":
        st.balloons()
        st.success("## 🎉🏆 YOU WIN! 🏆🎉")
    else:
        st.error("## 🤖 CPU Wins!")
    if st.button("🔄 Play Again", use_container_width=True):
        st.session_state.game = init_game()
        st.rerun()
    st.stop()

# ===== TURN LOGIC =====
if g["turn"] == "You" and g["phase"] == "TURN_START":
    draw_cards(g, "You", 2 if human.hand else 5)
    g["phase"] = "PLAY"
    g["plays_left"] = PLAYS_PER_TURN
    st.rerun()

if g["turn"] == "CPU":
    cpu_turn(g)
    check_win(g)
    st.rerun()

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### ⚙️ Menu")
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.game = init_game()
        st.rerun()
    st.divider()
    st.markdown("### 📜 Log")
    for entry in reversed(g["log"][-12:]):
        st.caption(entry)

# ===== CPU AREA =====
st.markdown(f"### 🤖 CPU Hand ({len(cpu.hand)} cards)")
render_card_backs_3d(len(cpu.hand))

st.divider()

# ===== TABLES =====
left, right = st.columns(2)

with left:
    st.markdown("### 🤖 CPU Table")
    st.markdown(f"**🏦 Bank:** ${cpu.bank_total()}M")
    if cpu.bank:
        render_cards_3d(cpu.bank, height=180)
    for color in COLORS:
        cards = cpu.props.get(color, [])
        if cards:
            badge = "✅" if cpu.has_full_set(color) else ""
            st.markdown(f"**{color}** {badge}")
            render_cards_3d(cards, height=180)

with right:
    st.markdown("### 👤 Your Table")
    st.markdown(f"**🏦 Bank:** ${human.bank_total()}M")
    if human.bank:
        render_cards_3d(human.bank, height=180)
    for color in COLORS:
        cards = human.props.get(color, [])
        if cards:
            badge = "✅" if human.has_full_set(color) else ""
            st.markdown(f"**{color}** {badge}")
            render_cards_3d(cards, height=180)

st.divider()

# ===== YOUR HAND =====
st.markdown(f"### 🃏 Your Hand ({len(human.hand)} cards)")

if g["plays_left"] <= 0:
    st.warning("⚠️ No plays left! Click **End Turn**.")

# End turn
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✅ END TURN", use_container_width=True, type="primary"):
        if len(human.hand) > MAX_HAND:
            st.error(f"❌ Discard to {MAX_HAND} cards!")
        else:
            g["turn"] = "CPU"
            g["plays_left"] = PLAYS_PER_TURN
            check_win(g)
            st.rerun()

# Hand display
if human.hand:
    render_cards_3d(human.hand, height=200)
    
    st.markdown("**Select card:**")
    cols_per_row = 5
    for row_start in range(0, len(human.hand), cols_per_row):
        cols = st.columns(cols_per_row)
        for i in range(cols_per_row):
            idx = row_start + i
            if idx < len(human.hand):
                card = human.hand[idx]
                with cols[i]:
                    if card.kind == "money":
                        st.caption(f"💵 ${card.value}M")
                    elif card.kind == "property":
                        st.caption(f"🏠 {card.active_color[:6] if card.active_color else 'Wild'}")
                    elif card.kind == "action":
                        st.caption(f"⚡ {card.name[:8]}")
                    elif card.kind == "rent":
                        st.caption(f"🏦 Rent")
                    elif card.kind == "building":
                        st.caption(f"🏗️ {card.name}")
                    
                    disabled = g["plays_left"] <= 0
                    b1, b2 = st.columns(2)
                    
                    with b1:
                        if st.button("▶️", key=f"p{idx}", disabled=disabled):
                            if card.kind == "money":
                                c = human.hand.pop(idx)
                                human.bank.append(c)
                                g["plays_left"] -= 1
                                log(g, f"💵 Banked {c.name}")
                            elif card.kind == "property":
                                play_property(g, "You", idx)
                            elif card.kind == "rent":
                                rc = card
                                if "Any" in rc.rent_colors:
                                    valid = list(human.props.keys())
                                else:
                                    valid = [c for c in rc.rent_colors if c in human.props]
                                if valid:
                                    human.hand.pop(idx)
                                    amt = calc_rent(human, valid[0])
                                    if human.double_rent_pending:
                                        amt *= 2
                                        human.double_rent_pending = False
                                    auto_pay(g, cpu, human, amt)
                                    g["plays_left"] -= 1
                                    log(g, f"🏦 Collected ${amt}M rent!")
                                else:
                                    st.toast("Need properties first!")
                            elif card.kind == "action":
                                play_action(g, "You", idx)
                            elif card.kind == "building":
                                valid = [c for c in human.full_sets() if c not in ("Railroad", "Utility")]
                                if valid:
                                    bc = card
                                    human.hand.pop(idx)
                                    human.buildings.setdefault(valid[0], {})
                                    human.buildings[valid[0]][bc.building_type.lower()] = True
                                    g["plays_left"] -= 1
                                    log(g, f"🏗️ Built {bc.building_type} on {valid[0]}")
                                else:
                                    st.toast("Need a full set!")
                            st.rerun()
                    
                    with b2:
                        if st.button("🏦", key=f"b{idx}", disabled=disabled):
                            bank_card(g, "You", idx)
                            st.rerun()
else:
    st.info("Hand empty!")