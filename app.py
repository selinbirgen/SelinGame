"""
Monopoly Deal - Realistic Tabletop Edition
Two players seated at opposite ends of the table, like a real card game on iPad
"""

import streamlit as st
import streamlit.components.v1 as components
import random
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

COLOR_HEX = {
    "Brown": "#8B4513", "Light Blue": "#87CEEB", "Pink": "#E91E63",
    "Orange": "#FF9800", "Red": "#F44336", "Yellow": "#FFEB3B",
    "Green": "#4CAF50", "Dark Blue": "#1565C0", "Railroad": "#455A64", "Utility": "#78909C"
}

MAX_HAND, PLAYS_PER_TURN = 7, 3

# ============================================================
# PAGE CONFIG - FULL SCREEN TABLETOP
# ============================================================

st.set_page_config(
    page_title="Monopoly Deal", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Hide all Streamlit UI elements for immersive experience
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
.stDeployButton { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] { padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Card:
    name: str
    value: int
    kind: str
    id: int = 0

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

@dataclass
class BuildingCard(Card):
    building_type: str = ""

# ============================================================
# DECK & PLAYER
# ============================================================

class Deck:
    def __init__(self):
        self.cards = []
        self._build()
        random.shuffle(self.cards)
    
    def draw(self, n):
        return [self.cards.pop() for _ in range(min(n, len(self.cards)))]
    
    def _build(self):
        card_id = 0
        props = [("Brown", 1, 2), ("Light Blue", 1, 3), ("Pink", 2, 3), ("Orange", 2, 3),
                 ("Red", 3, 3), ("Yellow", 3, 3), ("Green", 4, 3), ("Dark Blue", 4, 2),
                 ("Railroad", 2, 4), ("Utility", 2, 2)]
        for color, val, count in props:
            for _ in range(count):
                self.cards.append(PropertyCard(name=color, value=val, kind="property",
                                               id=card_id, options=[color], active_color=color))
                card_id += 1
        
        wilds = [("Wild", 1, ["Light Blue", "Brown"]), ("Wild", 2, ["Pink", "Orange"]),
                 ("Wild", 2, ["Red", "Yellow"]), ("Wild", 4, ["Dark Blue", "Green"]),
                 ("Wild", 0, COLORS)]
        for name, val, opts in wilds:
            self.cards.append(PropertyCard(name=name, value=val, kind="property", id=card_id,
                                           options=opts, active_color=opts[0], is_wild=True))
            card_id += 1
        
        for v, c in {1: 6, 2: 5, 3: 3, 4: 3, 5: 2, 10: 1}.items():
            for _ in range(c):
                self.cards.append(Card(name=f"${v}M", value=v, kind="money", id=card_id))
                card_id += 1
        
        actions = [("Deal Breaker", 5, "DEAL_BREAKER"), ("Sly Deal", 3, "SLY_DEAL"),
                   ("Debt Collector", 3, "DEBT_COLLECTOR"), ("Birthday", 2, "BIRTHDAY"),
                   ("Pass Go", 1, "PASS_GO"), ("Double Rent", 1, "DOUBLE_RENT")]
        for name, val, aid in actions:
            for _ in range(2):
                self.cards.append(ActionCard(name=name, value=val, kind="action", id=card_id, action_id=aid))
                card_id += 1
        
        rents = [("Rent", 1, ["Light Blue", "Brown"]), ("Rent", 1, ["Pink", "Orange"]),
                 ("Rent", 1, ["Red", "Yellow"]), ("Rent", 3, ["Any"])]
        for name, val, cols in rents:
            self.cards.append(RentCard(name=name, value=val, kind="rent", id=card_id, rent_colors=cols))
            card_id += 1

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bank = []
        self.props = {}
    
    def bank_total(self):
        return sum(c.value for c in self.bank)
    
    def full_sets(self):
        return [c for c in COLORS if len(self.props.get(c, [])) >= PROPERTY_SETS[c]]

# ============================================================
# GAME LOGIC
# ============================================================

def init_game(p1_name="Player 1", p2_name="Player 2"):
    d = Deck()
    p1, p2 = Player(p1_name), Player(p2_name)
    p1.hand = d.draw(5)
    p2.hand = d.draw(5)
    return {
        "deck": d,
        "p1": p1, "p2": p2,
        "current": 1,  # 1 or 2
        "plays_left": PLAYS_PER_TURN,
        "phase": "TURN_START",
        "round": 1,
        "winner": None,
        "log": []
    }

def get_current(g):
    return g["p1"] if g["current"] == 1 else g["p2"]

def get_opponent(g):
    return g["p2"] if g["current"] == 1 else g["p1"]

def log(g, msg):
    g["log"] = g["log"][-10:] + [msg]

def collect_payment(g, payer, payee, amt):
    paid = 0
    while paid < amt and payer.bank:
        c = payer.bank.pop(0)
        payee.bank.append(c)
        paid += c.value
    while paid < amt:
        found = False
        for color in list(payer.props.keys()):
            if payer.props[color]:
                c = payer.props[color].pop(0)
                if not payer.props[color]:
                    del payer.props[color]
                payee.props.setdefault(c.active_color or color, []).append(c)
                paid += c.value
                found = True
                break
        if not found:
            break
    return paid

def end_turn(g):
    g["current"] = 2 if g["current"] == 1 else 1
    g["phase"] = "TURN_START"
    g["plays_left"] = PLAYS_PER_TURN
    if g["current"] == 1:
        g["round"] += 1

def check_win(g):
    for p in [g["p1"], g["p2"]]:
        if len(p.full_sets()) >= 3:
            g["winner"] = p.name
            return True
    return False

# ============================================================
# TABLETOP HTML RENDERER
# ============================================================

def render_tabletop(g):
    """Render the full tabletop view with both players"""
    
    p1, p2 = g["p1"], g["p2"]
    current = get_current(g)
    is_p1_turn = g["current"] == 1
    
    # Generate card HTML for each area
    def card_html(card, flipped=False, rotated=False, small=False):
        if flipped:
            size = "width:50px;height:70px;" if small else "width:60px;height:85px;"
            rot = "transform:rotate(180deg);" if rotated else ""
            return f'''<div style="{size}{rot}border-radius:6px;
                background:repeating-linear-gradient(45deg,#c62828,#c62828 4px,#b71c1c 4px,#b71c1c 8px);
                box-shadow:0 2px 8px rgba(0,0,0,0.3);display:inline-block;margin:2px;
                position:relative;">
                <div style="position:absolute;inset:4px;background:#d32f2f;border-radius:3px;
                border:2px solid #ffcdd2;display:flex;align-items:center;justify-content:center;">
                <span style="color:#ffcdd2;font-weight:bold;font-size:14px;">M</span></div></div>'''
        
        size = "width:70px;height:100px;" if not small else "width:55px;height:78px;"
        rot = "transform:rotate(180deg);" if rotated else ""
        font = "font-size:9px;" if small else "font-size:11px;"
        
        if card.kind == "money":
            return f'''<div style="{size}{rot}border-radius:8px;background:#fff;
                box-shadow:0 3px 10px rgba(0,0,0,0.25);display:inline-flex;flex-direction:column;
                margin:3px;overflow:hidden;">
                <div style="background:linear-gradient(145deg,#2e7d32,#1b5e20);padding:4px;text-align:center;">
                    <span style="color:#fff;{font}font-weight:bold;">CASH</span></div>
                <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
                    background:linear-gradient(180deg,#e8f5e9,#c8e6c9);">
                    <span style="font-size:28px;font-weight:900;color:#1b5e20;">{card.value}</span>
                    <span style="font-size:8px;color:#2e7d32;">MILLION</span></div>
                <div style="background:#e8f5e9;padding:3px;text-align:center;border-top:1px solid #a5d6a7;">
                    <span style="color:#1b5e20;font-weight:bold;{font}">${card.value}M</span></div></div>'''
        
        elif card.kind == "property":
            color = card.active_color or "Brown"
            hex_c = COLOR_HEX.get(color, "#888")
            text_c = "#000" if color in ["Yellow", "Light Blue"] else "#fff"
            wild = "🃏" if getattr(card, 'is_wild', False) else ""
            return f'''<div style="{size}{rot}border-radius:8px;background:#fff;
                box-shadow:0 3px 10px rgba(0,0,0,0.25);display:inline-flex;flex-direction:column;
                margin:3px;overflow:hidden;">
                <div style="background:linear-gradient(145deg,{hex_c},{hex_c}cc);padding:4px;text-align:center;">
                    <span style="color:{text_c};{font}font-weight:bold;">{color[:8]}</span></div>
                <div style="flex:1;display:flex;align-items:center;justify-content:center;background:#f5f5f5;">
                    <span style="font-size:20px;">{wild or '🏠'}</span></div>
                <div style="background:#f0f0f0;padding:3px;text-align:center;border-top:1px solid #ddd;">
                    <span style="color:#333;font-weight:bold;{font}">${card.value}M</span></div></div>'''
        
        elif card.kind == "action":
            icons = {"DEAL_BREAKER":"💥","SLY_DEAL":"🦊","DEBT_COLLECTOR":"💰",
                     "BIRTHDAY":"🎂","PASS_GO":"▶️","DOUBLE_RENT":"✖️"}
            icon = icons.get(getattr(card,'action_id',''),'⚡')
            return f'''<div style="{size}{rot}border-radius:8px;background:#fff;
                box-shadow:0 3px 10px rgba(0,0,0,0.25);display:inline-flex;flex-direction:column;
                margin:3px;overflow:hidden;">
                <div style="background:linear-gradient(145deg,#e53935,#c62828);padding:4px;text-align:center;">
                    <span style="color:#fff;{font}font-weight:bold;">ACTION</span></div>
                <div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
                    background:linear-gradient(180deg,#ffebee,#ffcdd2);">
                    <span style="font-size:22px;">{icon}</span>
                    <span style="font-size:7px;color:#c62828;margin-top:2px;">{card.name[:10]}</span></div>
                <div style="background:#ffebee;padding:3px;text-align:center;border-top:1px solid #ef9a9a;">
                    <span style="color:#c62828;font-weight:bold;{font}">${card.value}M</span></div></div>'''
        
        elif card.kind == "rent":
            return f'''<div style="{size}{rot}border-radius:8px;background:#fff;
                box-shadow:0 3px 10px rgba(0,0,0,0.25);display:inline-flex;flex-direction:column;
                margin:3px;overflow:hidden;">
                <div style="background:linear-gradient(145deg,#5c6bc0,#3949ab);padding:4px;text-align:center;">
                    <span style="color:#fff;{font}font-weight:bold;">RENT</span></div>
                <div style="flex:1;display:flex;align-items:center;justify-content:center;
                    background:linear-gradient(180deg,#e8eaf6,#c5cae9);">
                    <span style="font-size:22px;">🏦</span></div>
                <div style="background:#e8eaf6;padding:3px;text-align:center;border-top:1px solid #9fa8da;">
                    <span style="color:#3949ab;font-weight:bold;{font}">${card.value}M</span></div></div>'''
        
        return f'<div style="{size}background:#ddd;border-radius:8px;margin:3px;"></div>'
    
    # Build property display
    def props_html(player, rotated=False):
        if not player.props:
            return ""
        html = ""
        for color, cards in player.props.items():
            for c in cards:
                html += card_html(c, rotated=rotated, small=True)
        return html
    
    # Build bank display
    def bank_html(player, rotated=False):
        return "".join([card_html(c, rotated=rotated, small=True) for c in player.bank])
    
    # Build hand display (only for active player at bottom)
    def hand_html(player):
        return "".join([card_html(c) for c in player.hand])
    
    # Deck display
    deck_count = len(g["deck"].cards)
    deck_html = f'''<div style="position:relative;width:70px;height:95px;">
        {''.join([f'<div style="position:absolute;top:{i}px;left:{i//2}px;width:60px;height:85px;border-radius:6px;background:repeating-linear-gradient(45deg,#c62828,#c62828 4px,#b71c1c 4px,#b71c1c 8px);box-shadow:0 2px 5px rgba(0,0,0,0.2);"><div style="position:absolute;inset:4px;background:#d32f2f;border-radius:3px;border:2px solid #ffcdd2;"></div></div>' for i in range(min(deck_count, 8))])}
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
            color:#ffcdd2;font-weight:bold;font-size:18px;text-shadow:1px 1px 2px #000;">M</div>
        <div style="position:absolute;bottom:-20px;left:50%;transform:translateX(-50%);
            color:#fff;font-size:11px;font-weight:bold;text-shadow:1px 1px 2px #000;">{deck_count}</div>
    </div>'''
    
    # Status indicators
    p1_sets = len(p1.full_sets())
    p2_sets = len(p2.full_sets())
    
    # Full tabletop HTML
    tabletop = f'''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Poppins',sans-serif; }}
        body {{
            background: 
                radial-gradient(ellipse at 50% 50%, #2d5a3d 0%, #1a472a 50%, #0d2818 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        
        /* Wood trim around table */
        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            border: 15px solid;
            border-image: linear-gradient(145deg, #8b6914, #5d4037, #8b6914) 1;
            pointer-events: none;
            z-index: 1000;
        }}
        
        .player-area {{
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .player-area.top {{
            transform: rotate(180deg);
            background: linear-gradient(180deg, rgba(0,0,0,0.3) 0%, transparent 100%);
        }}
        
        .player-area.bottom {{
            background: linear-gradient(0deg, rgba(0,0,0,0.3) 0%, transparent 100%);
        }}
        
        .player-info {{
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 10px 15px;
            color: #fff;
            min-width: 120px;
            text-align: center;
        }}
        
        .player-name {{
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        
        .player-stats {{
            font-size: 11px;
            opacity: 0.9;
        }}
        
        .cards-area {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            flex: 1;
            justify-content: center;
            align-items: center;
        }}
        
        .section-label {{
            background: rgba(0,0,0,0.4);
            color: #ffd700;
            padding: 3px 10px;
            border-radius: 5px;
            font-size: 10px;
            font-weight: 600;
            margin-right: 10px;
        }}
        
        .center-area {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 50px;
            padding: 20px;
        }}
        
        .deck-area {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .turn-indicator {{
            background: linear-gradient(145deg, #ffd700, #ff8c00);
            color: #000;
            padding: 15px 30px;
            border-radius: 15px;
            font-weight: 700;
            font-size: 16px;
            box-shadow: 0 5px 20px rgba(255,215,0,0.4);
            text-align: center;
        }}
        
        .plays-left {{
            font-size: 12px;
            margin-top: 5px;
            opacity: 0.8;
        }}
        
        .active-player {{
            box-shadow: 0 0 20px rgba(255,215,0,0.6);
            border: 2px solid #ffd700;
        }}
        
        .hand-area {{
            padding: 15px;
            background: rgba(0,0,0,0.2);
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 8px;
            min-height: 130px;
        }}
    </style>
    </head>
    <body>
        <!-- PLAYER 2 (TOP - rotated 180°) -->
        <div class="player-area top">
            <div class="player-info {'active-player' if not is_p1_turn else ''}">
                <div class="player-name">👤 {p2.name}</div>
                <div class="player-stats">🏆 {p2_sets}/3 sets • 💰 ${p2.bank_total()}M</div>
            </div>
            <div class="section-label">BANK</div>
            <div class="cards-area">{bank_html(p2, rotated=True)}</div>
            <div class="section-label">PROPERTIES</div>
            <div class="cards-area">{props_html(p2, rotated=True)}</div>
        </div>
        
        <!-- PLAYER 2 HAND (face down, rotated) -->
        <div class="hand-area" style="transform:rotate(180deg);">
            {''.join([card_html(c, flipped=True, rotated=True) for c in p2.hand])}
        </div>
        
        <!-- CENTER TABLE AREA -->
        <div class="center-area">
            <div class="deck-area">
                {deck_html}
                <div style="color:#fff;margin-top:25px;font-size:12px;">DECK</div>
            </div>
            
            <div class="turn-indicator">
                🎲 {current.name}'s Turn
                <div class="plays-left">⚡ {g['plays_left']} plays left • Round {g['round']}</div>
            </div>
        </div>
        
        <!-- PLAYER 1 HAND (face down if not their turn, face up if their turn) -->
        <div class="hand-area">
            {hand_html(p1) if is_p1_turn else ''.join([card_html(c, flipped=True) for c in p1.hand])}
        </div>
        
        <!-- PLAYER 1 (BOTTOM) -->
        <div class="player-area bottom">
            <div class="player-info {'active-player' if is_p1_turn else ''}">
                <div class="player-name">👤 {p1.name}</div>
                <div class="player-stats">🏆 {p1_sets}/3 sets • 💰 ${p1.bank_total()}M</div>
            </div>
            <div class="section-label">BANK</div>
            <div class="cards-area">{bank_html(p1)}</div>
            <div class="section-label">PROPERTIES</div>
            <div class="cards-area">{props_html(p1)}</div>
        </div>
    </body>
    </html>
    '''
    
    return tabletop

# ============================================================
# STREAMLIT UI
# ============================================================

# Initialize
if "game" not in st.session_state:
    st.session_state.game = None

# Start screen
if st.session_state.game is None:
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;min-height:80vh;flex-direction:column;">
        <div style="background:linear-gradient(145deg,#c41e3a,#8b0000);padding:30px 60px;border-radius:20px;
                    border:5px solid #ffd700;box-shadow:0 15px 50px rgba(0,0,0,0.5);text-align:center;">
            <div style="font-size:52px;font-weight:900;color:#fff;text-shadow:3px 3px 0 #000;
                        font-family:serif;letter-spacing:3px;">MONOPOLY</div>
            <div style="font-size:28px;font-weight:700;color:#ffd700;letter-spacing:12px;">DEAL</div>
        </div>
        <div style="margin-top:30px;color:#666;font-size:14px;">Tabletop Edition</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 👥 Enter Player Names")
        p1 = st.text_input("Player 1 (Bottom):", value="Player 1", key="p1_name")
        p2 = st.text_input("Player 2 (Top):", value="Player 2", key="p2_name")
        
        if st.button("🎮 START GAME", use_container_width=True, type="primary"):
            st.session_state.game = init_game(p1, p2)
            st.rerun()
    
    st.stop()

# Game active
g = st.session_state.game

# Check winner
if g["winner"]:
    st.balloons()
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;min-height:60vh;flex-direction:column;">
        <div style="font-size:72px;">🏆</div>
        <div style="font-size:36px;font-weight:bold;color:#ffd700;margin:20px 0;">{g['winner']} WINS!</div>
        <div style="color:#888;">Collected 3 complete property sets!</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.game = None
        st.rerun()
    st.stop()

# Turn start - draw cards
if g["phase"] == "TURN_START":
    player = get_current(g)
    draw_n = 5 if len(player.hand) == 0 else 2
    player.hand.extend(g["deck"].draw(draw_n))
    g["phase"] = "PLAY"
    g["plays_left"] = PLAYS_PER_TURN
    log(g, f"{player.name} drew {draw_n} cards")
    st.rerun()

# Render tabletop
components.html(render_tabletop(g), height=700, scrolling=False)

# Action buttons (below the table)
current = get_current(g)
st.markdown("---")

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.markdown(f"### 🎴 {current.name}'s Hand - Select a card to play")
    
    if g["plays_left"] <= 0:
        st.warning("⚠️ No plays left! End your turn.")
    
    # Card selection
    if current.hand:
        card_cols = st.columns(len(current.hand))
        for idx, card in enumerate(current.hand):
            with card_cols[idx]:
                # Card preview
                if card.kind == "money":
                    st.markdown(f"**💵 ${card.value}M**")
                elif card.kind == "property":
                    color = getattr(card, 'active_color', 'Property')
                    wild = " 🃏" if getattr(card, 'is_wild', False) else ""
                    st.markdown(f"**🏠 {color[:8]}{wild}**")
                elif card.kind == "action":
                    st.markdown(f"**⚡ {card.name[:10]}**")
                elif card.kind == "rent":
                    st.markdown(f"**🏦 Rent**")
                else:
                    st.markdown(f"**{card.name}**")
                
                # Play button
                if st.button("▶️ Play", key=f"play_{idx}", disabled=g["plays_left"]<=0, use_container_width=True):
                    opponent = get_opponent(g)
                    if card.kind == "money":
                        current.hand.pop(idx)
                        current.bank.append(card)
                    elif card.kind == "property":
                        current.hand.pop(idx)
                        color = card.active_color or card.options[0]
                        current.props.setdefault(color, []).append(card)
                    elif card.kind == "rent":
                        current.hand.pop(idx)
                        if "Any" in card.rent_colors:
                            colors = list(current.props.keys())
                        else:
                            colors = [c for c in card.rent_colors if c in current.props]
                        if colors:
                            color = colors[0]
                            count = len(current.props.get(color, []))
                            rent = RENT_VALUES.get(color, [1])
                            amt = rent[min(count, len(rent))-1] if count > 0 else 0
                            collect_payment(g, opponent, current, amt)
                            log(g, f"{current.name} collected ${amt}M rent!")
                    elif card.kind == "action":
                        current.hand.pop(idx)
                        aid = getattr(card, 'action_id', '')
                        if aid == "PASS_GO":
                            current.hand.extend(g["deck"].draw(2))
                            log(g, f"{current.name} drew 2 cards!")
                        elif aid == "BIRTHDAY":
                            collect_payment(g, opponent, current, 2)
                            log(g, f"Birthday! Collected $2M")
                        elif aid == "DEBT_COLLECTOR":
                            collect_payment(g, opponent, current, 5)
                            log(g, f"Debt Collector! Collected $5M")
                        elif aid == "SLY_DEAL":
                            for col, cards in list(opponent.props.items()):
                                if len(cards) < PROPERTY_SETS[col] and cards:
                                    stolen = cards.pop(0)
                                    if not opponent.props[col]:
                                        del opponent.props[col]
                                    current.props.setdefault(col, []).append(stolen)
                                    log(g, f"Stole {col} property!")
                                    break
                        elif aid == "DEAL_BREAKER":
                            full = opponent.full_sets()
                            if full:
                                col = full[0]
                                stolen = opponent.props.pop(col, [])
                                current.props.setdefault(col, []).extend(stolen)
                                log(g, f"Stole {col} set!")
                    
                    g["plays_left"] -= 1
                    check_win(g)
                    st.rerun()
                
                # Bank button
                if st.button("🏦 Bank", key=f"bank_{idx}", disabled=g["plays_left"]<=0, use_container_width=True):
                    c = current.hand.pop(idx)
                    current.bank.append(c)
                    g["plays_left"] -= 1
                    log(g, f"Banked ${c.value}M")
                    st.rerun()
    
    st.markdown("---")
    
    # End turn / Pass to opponent
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        opponent = get_opponent(g)
        if st.button(f"✅ END TURN - Pass to {opponent.name}", use_container_width=True, type="primary"):
            end_turn(g)
            st.rerun()

# Game log
with st.expander("📜 Game Log"):
    for entry in reversed(g["log"]):
        st.caption(entry)