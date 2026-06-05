import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import random
import math

st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

# 🎨 UI CSS
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.stApp { background-color: #0e1117; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 12px; 
    border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 25px;
    display: flex; flex-direction: column; height: 530px; 
}
.card-box p { margin: 0 !important; padding: 0 !important; line-height: 1.5 !important; }
.card-top { flex-shrink: 0; }
.card-mid { flex-grow: 1; display: flex; flex-direction: column; justify-content: center; margin: 15px 0; }
.card-bot { flex-shrink: 0; border-top: 1px dashed #555; padding-top: 15px; text-align: center; }
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; letter-spacing: 1px; }
.match-box { display: flex; align-items: center; justify-content: center; width: 100%; margin-bottom: 5px; }
.team-side { display: flex; align-items: center; flex: 1; gap: 8px; width: 42%; }
.home-side { justify-content: flex-end; text-align: right; }
.away-side { justify-content: flex-start; text-align: left; }
.team-name { font-size: 14.5px; font-weight: bold; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95px; }
.score-side { font-size: 24px; font-weight: bold; padding: 0 5px; width: 16%; text-align: center; flex-shrink: 0; white-space: nowrap; }
.team-logo { width: 26px; height: 26px; object-fit: contain; flex-shrink: 0; }
.referee-txt { font-size: 11px; color: #888; text-align: center; margin-bottom: 5px; }
.prob-wrapper { width: 100%; margin-bottom: 15px; }
.prob-text { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 4px; }
.prob-container { display: flex; width: 100%; height: 8px; border-radius: 4px; overflow: hidden; background-color: #333; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }
.stat-bg { background-color: #262730; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 12.5px; line-height: 1.6; text-align: center; border: 1px solid #444; width: 100%; }
.predict-txt { font-size: 15px; font-weight: bold; margin-bottom: 6px; }
.over-under { font-size: 13px; font-weight: bold; margin-bottom: 8px; } 
.ai-advice { font-size: 11.5px; color: #aaa; font-weight: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; white-space: normal; }
.table-wrapper { width: 100%; overflow-x: auto; margin-top: 5px; margin-bottom: 15px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 12px; color: #ccc; text-align: center; table-layout: fixed; } 
.detail-table th { background-color: #111; padding: 10px 5px; border-bottom: 2px solid #555; color: #fff; white-space: nowrap; }
.detail-table td { padding: 8px 5px; border-bottom: 1px solid #2a2a2a; word-wrap: break-word; } 
.injury-tag { color: #ff5252; font-size: 11px; background: #331111; padding: 3px 6px; border-radius: 4px; display: inline-block; margin: 2px; }
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] { display: flex !important; flex-direction: row !important; justify-content: space-between !important; gap: 5px !important; width: 100% !important; margin-bottom: 10px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { flex: 1 !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; background: transparent !important; border: none !important; padding: 5px 0 !important; cursor: pointer !important; margin: 0 !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label::before { font-family: "Font Awesome 6 Free"; font-weight: 900; font-size: 22px; color: #ffffff; background-color: #151515; width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; transition: all 0.3s ease; border: 2px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1)::before { content: "\\f1e3"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2)::before { content: "\\f433"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3)::before { content: "\\f434"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4)::before { content: "\\f45f"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before { border-color: #666; transform: translateY(-2px); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before { border-color: #00E676 !important; color: #00E676 !important; background-color: #151515 !important; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4) !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 13px !important; font-weight: 700 !important; color: #888 !important; margin: 0 !important; text-align: center !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #00E676 !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

FOOTBALL_API_KEY = st.secrets["FOOTBALL_API_KEY"] if "FOOTBALL_API_KEY" in st.secrets else ""
HEADERS = {'x-apisports-key': FOOTBALL_API_KEY}

CUSTOM_DICT = {
    "Arsenal": "아스날", "Aston Villa": "애스턴 빌라", "Newcastle": "뉴캐슬", "Crystal Palace": "크리스탈 팰리스",
    "Athletics": "애슬레틱스", "Oakland Athletics": "오클랜드", "Oakland": "오클랜드",
    "Arizona Diamondbacks": "애리조나", "Atlanta Braves": "애틀랜타", "Baltimore Orioles": "볼티모어",
    "Boston Red Sox": "보스턴", "Chicago Cubs": "시카고 컵스", "Chicago White Sox": "화이트삭스",
    "Cincinnati Reds": "신시내티", "Cleveland Guardians": "클리블랜드", "Colorado Rockies": "콜로라도",
    "Detroit Tigers": "디트로이트", "Houston Astros": "휴스턴", "Kansas City Royals": "캔자스시티",
    "Los Angeles Angels": "LA 에인절스", "Los Angeles Dodgers": "LA 다저스", "Miami Marlins": "마이애미",
    "Milwaukee Brewers": "밀워키", "Minnesota Twins": "미네소타", "New York Mets": "NY 메츠",
    "New York Yankees": "NY 양키스", "Philadelphia Phillies": "필라델피아",
    "Pittsburgh Pirates": "피츠버그", "San Diego Padres": "샌디에이고", "San Francisco Giants": "샌프란시스코",
    "Seattle Mariners": "시애틀", "St. Louis Cardinals": "세인트루이스", "Tampa Bay Rays": "탬파베이",
    "Texas Rangers": "텍사스", "Toronto Blue Jays": "토론토", "Washington Nationals": "워싱턴",
    "LG Twins": "LG 트윈스", "KT Wiz": "KT 위즈", "Samsung Lions": "삼성 라이온즈", "KIA Tigers": "KIA 타이거즈",
    "Hanwha Eagles": "한화 이글스", "Doosan Bears": "두산 베어스", "NC Dinos": "NC 다이노스", "SSG Landers": "SSG 랜더스",
    "Lotte Giants": "롯데 자이언츠", "Kiwoom Heroes": "키움 히어로즈", "Yomiuri Giants": "요미우리", "Hanshin Tigers": "한신", 
    "Hiroshima Toyo Carp": "히로시마", "Chunichi Dragons": "주니치", "Yokohama DeNA BayStars": "요코하마", 
    "Tokyo Yakult Swallows": "야쿠르트", "Orix Buffaloes": "오릭스", "Fukuoka SoftBank Hawks": "소프트뱅크", 
    "Hokkaido Nippon-Ham Fighters": "니혼햄", "Chiba Lotte Marines": "지바롯데", "Saitama Seibu Lions": "세이부", 
    "Tohoku Rakuten Golden Eagles": "라쿠텐"
}

@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or str(text).strip() in ['', 'N/A']: return '데이터 분석 중'
    for eng, kor in CUSTOM_DICT.items():
        if eng.lower() == str(text).lower() or eng in str(text): return kor
    try: return GoogleTranslator(source='en', target='ko').translate(str(text).replace('<', '').replace('>', ''))
    except: return str(text)

def safe_num(value):
    if not value or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except: return 0.0

def create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom=False):
    labels = ['공격력', '수비력', '최근폼', '상대전적', '득점력', '종합전력']
    size = 220; center = size / 2; max_val = 100
    def get_poly(vals, bc, fc):
        pts = [f"{center + (v/max_val)*(size*0.35)*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (v/max_val)*(size*0.35)*math.sin((math.pi*2/6)*i - math.pi/2)}" for i, v in enumerate(vals)]
        return f"<polygon points='{' '.join(pts)}' style='fill:{fc}; stroke:{bc}; stroke-width:2; opacity:0.6;' />"
    svg = ""
    for i in range(6):
        ang = (math.pi * 2 / 6) * i - (math.pi / 2)
        x = center + (size * 0.35) * math.cos(ang); y = center + (size * 0.35) * math.sin(ang)
        svg += f"<line x1='{center}' y1='{center}' x2='{x}' y2='{y}' style='stroke:#444; stroke-width:1;' />"
        lx = center + (size * 0.44) * math.cos(ang); ly = center + (size * 0.44) * math.sin(ang)
        anchor = "start" if lx > center + 10 else ("end" if lx < center - 10 else "middle")
        svg += f"<text x='{lx}' y='{ly+4}' fill='#ddd' font-size='10' font-weight='bold' text-anchor='{anchor}'>{labels[i]}</text>"
    for ratio in [0.33, 0.66, 1.0]:
        pts = [f"{center + (size*0.35)*ratio*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (size*0.35)*ratio*math.sin((math.pi*2/6)*i - math.pi/2)}" for i in range(6)]
        svg += f"<polygon points='{' '.join(pts)}' style='fill:none; stroke:#333; stroke-width:1;' />"
    h_poly = get_poly(h_vals, "#4FC3F7", "rgba(79, 195, 247, 0.3)") 
    a_poly = get_poly(a_vals, "#EF5350", "rgba(239, 83, 80, 0.3)") 
    badge = "<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ AI 전력 분석망 가동</div>"
    return f"<div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:10px; margin-bottom: 10px;'>{badge}<div style='font-size:11px; color:#fff; margin-bottom:10px; font-weight:bold; text-align:center;'><span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}</div><svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>{svg}{h_poly}{a_poly}</svg></div>"

# ==========================================
# ⚽ 축구 전용 함수
# ==========================================
def fetch_custom_team_stats(team_id, season_year):
    try:
        url = "https://v3.football.api-sports.io/fixtures"
        res = requests.get(url, headers=HEADERS, params={"team": team_id, "last": 5, "season": season_year}).json()
        fixtures = res.get('response', [])
        if not fixtures: return 10, 10, 10 
        wins, goals_for, goals_against = 0, 0, 0
        for match in fixtures:
            is_home = match['teams']['home']['id'] == team_id
            h_g = match['goals']['home'] if match['goals']['home'] is not None else 0
            a_g = match['goals']['away'] if match['goals']['away'] is not None else 0
            if is_home:
                goals_for += h_g; goals_against += a_g
                if h_g > a_g: wins += 1
            else:
                goals_for += a_g; goals_against += h_g
                if a_g > h_g: wins += 1
        return (wins / 5) * 100, min((goals_for / 15) * 100, 100), max(100 - (goals_against / 10) * 100, 0)
    except: return 20, 20, 20

def get_football_detailed_html(home_kr, away_kr, h_rank, a_rank, h_goals, a_goals, h_goals_against, a_goals_against, h_injuries, a_injuries):
    h_inj_html = "".join([f"<span class='injury-tag'>🚑 {inj}</span>" for inj in h_injuries]) or "<span style='color:#888;'>결장자 없음</span>"
    a_inj_html = "".join([f"<span class='injury-tag'>🚑 {inj}</span>" for inj in a_injuries]) or "<span style='color:#888;'>결장자 없음</span>"
    return f"""<div class='table-wrapper'><table class='detail-table'>
        <tr><th style='color:#4FC3F7; width:40%;'>{home_kr}</th><th style='width:20%; color:#aaa;'>비교 지표</th><th style='color:#EF5350; width:40%;'>{away_kr}</th></tr>
        <tr><td><b>{h_rank}</b>위</td><td style='font-size:11px;'>리그 순위</td><td><b>{a_rank}</b>위</td></tr>
        <tr><td>{h_goals}골</td><td style='font-size:11px;'>평균 득점</td><td>{a_goals}골</td></tr>
        <tr><td>{h_goals_against}골</td><td style='font-size:11px;'>평균 실점</td><td>{a_goals_against}골</td></tr>
        <tr><td style='white-space:normal;'>{h_inj_html}</td><td style='font-size:11px;'>결장/부상</td><td style='white-space:normal;'>{a_inj_html}</td></tr>
    </table></div>"""

def get_lineup_table(home_kr, away_kr, lineup_data):
    if not lineup_data or len(lineup_data) < 2: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표</div>"
    h_p = [p['player']['name'].split()[-1] for p in lineup_data[0].get('startXI', [])]
    a_p = [p['player']['name'].split()[-1] for p in lineup_data[1].get('startXI', [])]
    m_len = max(len(h_p), len(a_p))
    h_p += [""] * (m_len - len(h_p)); a_p += [""] * (m_len - len(a_p))
    html = "<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7;'>{home} (선발)</th><th style='color:#EF5350;'>{away} (선발)</th></tr>".format(home=home_kr, away=away_kr)
    for h, a in zip(h_p, a_p): html += f"<tr><td>{h}</td><td>{a}</td></tr>"
    html += "</table></div>"
    return html

# ==========================================
# ⚾ 야구(MLB) 전용 함수
# ==========================================
MLB_PARK_FACTORS = {
    'Colorado Rockies': 1.12, 'Cincinnati Reds': 1.08, 'Boston Red Sox': 1.07, 'Texas Rangers': 1.05,
    'Chicago White Sox': 1.04, 'Atlanta Braves': 1.03, 'Los Angeles Dodgers': 1.03, 'Philadelphia Phillies': 1.02,
    'Houston Astros': 1.01, 'Baltimore Orioles': 1.00, 'Toronto Blue Jays': 1.00, 'Minnesota Twins': 1.00,
    'Chicago Cubs': 1.00, 'New York Yankees': 1.00, 'Kansas City Royals': 0.99, 'Arizona Diamondbacks': 0.99,
    'Milwaukee Brewers': 0.98, 'Los Angeles Angels': 0.98, 'Washington Nationals': 0.98, 'San Francisco Giants': 0.97,
    'Miami Marlins': 0.97, 'Pittsburgh Pirates': 0.96, 'Cleveland Guardians': 0.96, 'St. Louis Cardinals': 0.96,
    'Detroit Tigers': 0.95, 'Tampa Bay Rays': 0.95, 'New York Mets': 0.95, 'Athletics': 0.94,
    'San Diego Padres': 0.94, 'Seattle Mariners': 0.93
}

@st.cache_data(ttl=3600)
def load_mlb_all_data():
    try:
        h_splits = requests.get("https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&gameType=R&season=2026&playerPool=ALL&limit=1500").json()['stats'][0]['splits']
        df_h = pd.DataFrame([{'이름': r['player']['fullName'], '팀': r['team']['name'], '타수': r['stat'].get('atBats', 0), 'OPS': r['stat'].get('ops', '.000')} for r in h_splits])
        df_h['OPS'] = pd.to_numeric(df_h['OPS'], errors='coerce').fillna(0.0)
        df_h['타수'] = pd.to_numeric(df_h['타수'], errors='coerce').fillna(0)
        
        p_splits = requests.get("https://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&gameType=R&season=2026&playerPool=ALL&limit=1500").json()['stats'][0]['splits']
        df_p = pd.DataFrame([{'이름': r['player']['fullName'], '팀': r['team']['name'], '출장': r['stat'].get('gamesPlayed', 0), '선발': r['stat'].get('gamesStarted', 0), '이닝': r['stat'].get('inningsPitched', '0.0'), '피홈런': r['stat'].get('homeRuns', 0), '볼넷': r['stat'].get('baseOnBalls', 0), '탈삼진': r['stat'].get('strikeOuts', 0)} for r in p_splits])
        df_p['이닝_num'] = pd.to_numeric(df_p['이닝'], errors='coerce').fillna(0.0)
        df_p['평균이닝'] = df_p.apply(lambda x: x['이닝_num'] / x['선발'] if x['선발'] > 0 else 4.0, axis=1).clip(3.0, 7.5)
        df_p['FIP'] = df_p.apply(lambda x: ((13*x['피홈런'] + 3*x['볼넷'] - 2*x['탈삼진']) / x['이닝_num']) + 3.10 if x['이닝_num'] > 0 else 4.50, axis=1)
        
        team_bullpen_fip = df_p[(df_p['출장'] > df_p['선발']) & (df_p['이닝_num'] >= 5.0)].groupby('팀')['FIP'].mean().to_dict()
        return df_h, df_p, team_bullpen_fip
    except: return pd.DataFrame(), pd.DataFrame(), {}

@st.cache_data(ttl=3600)
def load_mlb_team_momentum():
    try:
        res = requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104", timeout=5).json()
        l10_dict = {}
        for record in res.get('records', []):
            for team in record.get('teamRecords', []):
                for split in team.get('records', {}).get('splitRecords', []):
                    if split['type'] == 'lastTen':
                        l10_dict[team['team']['name']] = split['wins'] / (split['wins'] + split['losses']) if (split['wins'] + split['losses']) > 0 else 0.5
        return l10_dict
    except: return {}

def load_mlb_live_lineup(game_pk, home_pitcher_id, away_pitcher_id):
    try:
        res = requests.get(f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore").json()
        h_players = res.get('teams', {}).get('home', {}).get('players', {})
        a_players = res.get('teams', {}).get('away', {}).get('players', {})
        
        h_p_hand = 'R'
        if home_pitcher_id:
            p_obj = h_players.get(f"ID{home_pitcher_id}", h_players.get(f"ID_{home_pitcher_id}", {}))
            h_p_hand = p_obj.get('person', {}).get('pitchHand', {}).get('code', 'R')
            
        a_p_hand = 'R'
        if away_pitcher_id:
            p_obj = a_players.get(f"ID{away_pitcher_id}", a_players.get(f"ID_{away_pitcher_id}", {}))
            a_p_hand = p_obj.get('person', {}).get('pitchHand', {}).get('code', 'R')

        h_lineup, a_lineup = [], []
        for pid in res.get('teams', {}).get('home', {}).get('battingOrder', []):
            p = h_players.get(f"ID{pid}", h_players.get(f"ID_{pid}", {}))
            if p: h_lineup.append({'name': p.get('person', {}).get('fullName', 'Unknown'), 'batSide': p.get('person', {}).get('batSide', {}).get('code', 'R')})
                
        for pid in res.get('teams', {}).get('away', {}).get('battingOrder', []):
            p = a_players.get(f"ID{pid}", a_players.get(f"ID_{pid}", {}))
            if p: a_lineup.append({'name': p.get('person', {}).get('fullName', 'Unknown'), 'batSide': p.get('person', {}).get('batSide', {}).get('code', 'R')})
                
        return h_lineup, a_lineup, h_p_hand, a_p_hand
    except:
        return [], [], 'R', 'R'

def calculate_platoon_ops(lineup, df_hitters, opp_p_hand, base_team_ops):
    if not lineup: return base_team_ops
    total_ops = 0
    for batter in lineup:
        b_stats = df_hitters[df_hitters['이름'] == batter['name']]
        b_ops = b_stats['OPS'].values[0] if not b_stats.empty and b_stats['OPS'].values[0] > 0 else base_team_ops
        if opp_p_hand == 'L':
            if batter['batSide'] == 'L': b_ops *= 0.90 
            elif batter['batSide'] in ['R', 'S']: b_ops *= 1.05 
        else: 
            if batter['batSide'] == 'R': b_ops *= 0.95 
            elif batter['batSide'] in ['L', 'S']: b_ops *= 1.05 
        total_ops += b_ops
    return total_ops / len(lineup)

def run_mlb_simulation(h_fip, a_fip, h_avg_ip, a_avg_ip, h_ops, a_ops, h_bp_fip, a_bp_fip, park_factor, num_sims=5000):
    h_starter_w = h_avg_ip / 9.0; a_starter_w = a_avg_ip / 9.0
    h_eff_fip = (h_fip * h_starter_w) + (h_bp_fip * (1 - h_starter_w))
    a_eff_fip = (a_fip * a_starter_w) + (a_bp_fip * (1 - a_starter_w))
    h_expected_runs = ((a_eff_fip * (h_ops / 0.720)) + 0.2) * park_factor
    a_expected_runs = (h_eff_fip * (a_ops / 0.720)) * park_factor
    h_wins, a_wins = 0, 0
    h_tie_win_prob = h_expected_runs / (h_expected_runs + a_expected_runs) if (h_expected_runs + a_expected_runs) > 0 else 0.5
    for _ in range(num_sims):
        h_score = max(0, int(random.gauss(h_expected_runs, 2.3)))
        a_score = max(0, int(random.gauss(a_expected_runs, 2.3)))
        if h_score == a_score: h_score += 1 if random.random() < h_tie_win_prob else (a_score + 1)
        if h_score > a_score: h_wins += 1
        elif a_score > h_score: a_wins += 1
    return (h_wins / num_sims) * 100, (a_wins / num_sims) * 100, h_expected_runs, a_expected_runs

def get_baseball_detailed_html(home_team, away_team, h_p, a_p, h_s_fip, a_s_fip, h_bp_fip, a_bp_fip, h_ops, a_ops, h_ip, a_ip):
    return f"""<div class='table-wrapper'><table class='detail-table'>
        <tr><th style='color:#4FC3F7; width:40%;'>{home_team}</th><th style='width:20%; color:#aaa;'>투타 지표</th><th style='color:#EF5350; width:40%;'>{away_team}</th></tr>
        <tr><td><b>{h_p}</b> <span style='font-size:11px; color:#888;'>({h_ip:.1f}이닝)</span></td><td style='font-size:11px;'>선발 투수</td><td><b>{a_p}</b> <span style='font-size:11px; color:#888;'>({a_ip:.1f}이닝)</span></td></tr>
        <tr><td>{h_s_fip:.2f}</td><td style='font-size:11px;'>선발 FIP</td><td>{a_s_fip:.2f}</td></tr>
        <tr><td>{h_bp_fip:.2f}</td><td style='font-size:11px;'>불펜 FIP</td><td>{a_bp_fip:.2f}</td></tr>
        <tr><td>{h_ops:.3f}</td><td style='font-size:11px;'>보정 OPS</td><td>{a_ops:.3f}</td></tr>
    </table></div>"""

def get_baseball_lineup_html(home_team, away_team, h_lineup, a_lineup):
    if not h_lineup or not a_lineup: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표 (시즌 평균 데이터 연산 적용)</div>"
    m_len = max(len(h_lineup), len(a_lineup))
    h_strs = [f"{b['name']} ({b['batSide']})" for b in h_lineup]
    a_strs = [f"{b['name']} ({b['batSide']})" for b in a_lineup]
    h_strs += [""] * (m_len - len(h_strs)); a_strs += [""] * (m_len - len(a_strs))
    html = f"<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7;'>{home_team} (타석)</th><th style='color:#EF5350;'>{away_team} (타석)</th></tr>"
    for i, (h, a) in enumerate(zip(h_strs, a_strs)): html += f"<tr><td>{i+1}. {h}</td><td>{i+1}. {a}</td></tr>"
    return html + "</table></div>"

# ==========================================
# 📺 메인 UI 렌더링 시작
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 AI 종합 스포츠 분석실 PRO MAX (V30.1)</h1>", unsafe_allow_html=True)

st.sidebar.markdown("### 🏆 스포츠 종목 선택")
selected_sport = st.sidebar.radio("종목 선택", ["축구", "야구", "농구", "배구"], horizontal=True, label_visibility="collapsed")
st.sidebar.markdown("---")

kst_now = datetime.utcnow() + timedelta(hours=9)
st.sidebar.markdown("### 📅 검색 날짜 설정 (KST 기준)")
selected_date = st.sidebar.date_input("날짜를 선택하세요", kst_now.date(), label_visibility="collapsed")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if 'analyzed_data_list' not in st.session_state: 
    st.session_state['analyzed_data_list'] = []

# ==========================================
# ⚽ 축구 로직
# ==========================================
if selected_sport == "축구":
    analyze_button = st.sidebar.button("🚀 축구 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚽ 축구 리그 선택")
    
    with st.sidebar.expander("🌟 국제 대회 (UEFA/FIFA)", expanded=True):
        l_2 = st.checkbox("챔피언스리그 (UCL)", value=False)
        l_3 = st.checkbox("유로파리그 (UEL)", value=False)
        l_1 = st.checkbox("월드컵 (World Cup)", value=False)
        l_10 = st.checkbox("A매치 친선전", value=True)

    with st.sidebar.expander("🌍 유럽 주요 1부 리그", expanded=True):
        l_39 = st.checkbox("프리미어리그 (ENG)", value=True)
        l_140 = st.checkbox("라리가 (ESP)", value=True)
        l_135 = st.checkbox("세리에 A (ITA)", value=False)
        l_78 = st.checkbox("분데스리가 (GER)", value=False)
        l_61 = st.checkbox("리그 1 (FRA)", value=False)
        l_88 = st.checkbox("에레디비시 (NED)", value=False)
        l_119 = st.checkbox("스코티시 프리미어십 (SCO)", value=False)

    selected_leagues = [lid for lid, selected in zip(["2","3","1","10","39","140","135","78","61","88","119"], 
                                                     [l_2, l_3, l_1, l_10, l_39, l_140, l_135, l_78, l_61, l_88, l_119]) if selected]
    LEAGUE_MAP = {"2":"챔피언스리그", "3":"유로파리그", "1":"월드컵", "10":"A매치", "39":"프리미어리그", "140":"라리가", "135":"세리에A", "78":"분데스리가", "61":"리그1", "88":"에레디비시", "119":"스코티시"}
    AUTUMN_TO_SPRING_LEAGUES = ["2", "3", "39", "140", "135", "78", "61", "88", "119"]

    if analyze_button:
        if not selected_leagues: st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요."); st.stop()
        
        st.session_state['analyzed_data_list'] = []
        progress_bar = st.progress(0); status_text = st.empty()
        total_leagues = len(selected_leagues); new_data_list = []
        
        for idx, league_id in enumerate(selected_leagues):
            status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 정밀 데이터 스캔 중... ({idx+1}/{total_leagues})")
            progress_bar.progress((idx) / total_leagues)
            
            calc_season_year = str(selected_date.year - 1) if league_id in AUTUMN_TO_SPRING_LEAGUES and selected_date.month < 7 else str(selected_date.year)
            querystring = {"league": league_id, "season": calc_season_year, "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
            
            try:
                res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params=querystring, timeout=10).json()
                for match in res.get('response', []):
                    fix_id = str(match['fixture']['id'])
                    home_id = match['teams']['home']['id']; away_id = match['teams']['away']['id']
                    
                    home_en = match['teams']['home']['name']; away_en = match['teams']['away']['name']
                    home_kr = translate_to_ko(home_en); away_kr = translate_to_ko(away_en)
                    home_logo = match['teams']['home']['logo']; away_logo = match['teams']['away']['logo']
                    
                    referee = str(match['fixture']['referee']).split(',')[0] if match['fixture']['referee'] else "배정 전"
                    venue = match['fixture']['venue']['name'] or "미정"
                    status_short = match['fixture']['status']['short']
                    
                    try:
                        timestamp = match['fixture']['timestamp']
                        utc_time = datetime.utcfromtimestamp(timestamp)
                        kst_time = utc_time + timedelta(hours=9)
                        match_time = kst_time.strftime("%H:%M")
                        is_past_start_time = datetime.utcnow() >= utc_time 
                    except: 
                        match_time = "시간미정"
                        is_past_start_time = True
                        
                    is_finished = status_short in ['FT', 'AET', 'PEN']
                    is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P'] and is_past_start_time
                    elapsed_time = match['fixture']['status'].get('elapsed', '')
                    
                    if is_live and elapsed_time: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#ff5252; font-size:12px;'>[진행중: {elapsed_time}분]</span>"
                    elif is_finished: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#aaa; font-size:12px;'>[경기 종료]</span>"
                    else: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time})"
                    
                    h_g = match['goals']['home'] if match['goals']['home'] is not None else 0
                    a_g = match['goals']['away'] if match['goals']['away'] is not None else 0
                    
                    h_logo_html = f"<img src='{home_logo}' class='team-logo'>"
                    a_logo_html = f"<img src='{away_logo}' class='team-logo'>"
                    
                    if is_finished: score_color = "#00E676"; score_text = f"{h_g}:{a_g}"
                    elif is_live: score_color = "#ff5252"; score_text = f"{h_g}:{a_g}"
                    else: score_color = "#888888"; score_text = "VS"

                    match_display = f"<div class='match-box'><div class='team-side home-side'>{h_logo_html}<div class='team-name' title='{home_kr}'>{home_kr}</div></div><div class='score-side' style='color:{score_color};'>{score_text}</div><div class='team-side away-side'><div class='team-name' title='{away_kr}'>{away_kr}</div>{a_logo_html}</div></div>"

                    pred_data = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    if not pred_data: continue
                    pred = pred_data[0]; comp = pred.get('comparison', {})
                    
                    odds_res = requests.get("https://v3.football.api-sports.io/odds", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    inj_res = requests.get("https://v3.football.api-sports.io/injuries", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    
                    h_inj = [translate_to_ko(i['player']['name']) for i in inj_res if i['team']['id'] == home_id]
                    a_inj = [translate_to_ko(i['player']['name']) for i in inj_res if i['team']['id'] == away_id]
                    
                    h_rank = pred.get('teams',{}).get('home',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                    a_rank = pred.get('teams',{}).get('away',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                    h_avg_f = pred.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                    a_avg_f = pred.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                    h_avg_a = pred.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')
                    a_avg_a = pred.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')

                    wp = pred.get('predictions', {}).get('percent', {})
                    p_h = wp.get('home', '33%').replace('%',''); p_d = wp.get('draw', '33%').replace('%',''); p_a = wp.get('away', '33%').replace('%','')

                    h_vals = [safe_num(comp.get('att', {}).get('home')), safe_num(comp.get('def', {}).get('home')), safe_num(comp.get('form', {}).get('home')), safe_num(comp.get('h2h', {}).get('home')), safe_num(comp.get('goals', {}).get('home')), safe_num(comp.get('total', {}).get('home'))]
                    a_vals = [safe_num(comp.get('att', {}).get('away')), safe_num(comp.get('def', {}).get('away')), safe_num(comp.get('form', {}).get('away')), safe_num(comp.get('h2h', {}).get('away')), safe_num(comp.get('goals', {}).get('away')), safe_num(comp.get('total', {}).get('away'))]
                    
                    is_custom = False
                    if sum(h_vals) < 10 or sum(a_vals) < 10:
                        cf_h, ca_h, cd_h = fetch_custom_team_stats(home_id, calc_season_year)
                        cf_a, ca_a, cd_a = fetch_custom_team_stats(away_id, calc_season_year)
                        h_vals = [ca_h, cd_h, cf_h, 50, ca_h, (ca_h+cd_h+cf_h)/3]
                        a_vals = [ca_a, cd_a, cf_a, 50, ca_a, (ca_a+cd_a+cf_a)/3]
                        is_custom = True

                    radar_html = create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom)
                    detail_html = get_football_detailed_html(home_kr, away_kr, h_rank, a_rank, h_avg_f, a_avg_f, h_avg_a, a_avg_a, h_inj, a_inj)

                    odds_h = odds_d = odds_a = 0.0
                    if odds_res:
                        for b in odds_res[0].get('bookmakers', [])[0].get('bets', []):
                            if b['name'] == 'Match Winner':
                                for v in b['values']:
                                    if str(v['value']) == 'Home': odds_h = float(v['odd'])
                                    elif str(v['value']) == 'Draw': odds_d = float(v['odd'])
                                    elif str(v['value']) == 'Away': odds_a = float(v['odd'])
                                break
                    
                    h_power = sum(h_vals[:3])
                    a_power = sum(a_vals[:3])

                    if h_power > a_power + 15: win_pick, pick_color = f"🟢 {home_kr} 승 유력", "#00E676"; pred_winner = "home"
                    elif a_power > h_power + 15: win_pick, pick_color = f"🔵 {away_kr} 승 유력", "#4FC3F7"; pred_winner = "away"
                    else: win_pick, pick_color = "🟡 팽팽한 무승부", "#ff9800"; pred_winner = "draw"

                    if is_finished:
                        actual = "home" if h_g > a_g else ("away" if a_g > h_g else "draw")
                        if actual == pred_winner: win_pick += " (적중)"; pick_color = "#ffcc00"
                        else: win_pick += " (미적중)"; pick_color = "#ff5252"

                    odds_text = f"<b style='color:#ff9800;'>{odds_h}</b> | 무 <b>{odds_d}</b> | 원정 <b style='color:#ff9800;'>{odds_a}</b>" if odds_h > 0 else "해외 배당 미발매"
                    stat_box = f"<span style='color:#aaa;'>해외 배당:</span> 홈 {odds_text}<br><span style='color:#aaa;'>최종 산출 파워:</span> {home_kr} <b>{int(h_power)}점</b> vs <b>{int(a_power)}점</b> {away_kr}"
                    
                    under_over_val = pred.get('predictions', {}).get('under_over', '')
                    ou_line = 2.5
                    pred_is_over = True
                    
                    if under_over_val:
                        if '-' in under_over_val: pred_is_over = False; ou_line = float(under_over_val.replace('-', '').strip())
                        elif '+' in under_over_val: pred_is_over = True; ou_line = float(under_over_val.replace('+', '').strip())
                    else:
                        pred_is_over = (h_vals[4] + a_vals[4]) >= 120

                    ou_color = "#ddd"
                    ou_text_prefix = f"🔥 기준점 {ou_line} {'오버' if pred_is_over else '언더'}"

                    if is_finished:
                        actual_is_over = (h_g + a_g) > ou_line
                        if actual_is_over == pred_is_over:
                            over_under = f"{ou_text_prefix} (적중)"
                            ou_color = "#FFF59D" 
                        else:
                            over_under = f"{ou_text_prefix} (미적중)"
                            ou_color = "#F48FB1" 
                    else: over_under = ou_text_prefix

                    advice = translate_to_ko(pred.get('predictions', {}).get('advice', '분석 완료'))
                    ref_text = f"👨‍⚖️ 주심: {referee} | 🏟️ {venue}"

                    new_data_list.append({"sport": "축구", "league": top_league_display, "match_display": match_display, "stat_box": stat_box, "referee": ref_text, "venue": venue, "p_h": p_h, "p_d": p_d, "p_a": p_a, "win_pick": win_pick, "pick_color": pick_color, "ou_color": ou_color, "control_pick": advice, "over_under": over_under, "radar_html": radar_html, "lineup_html": get_lineup_table(home_kr, away_kr, lineup_data), "detail_html": detail_html})
            except: pass
        
        progress_bar.progress(1.0); status_text.text("✅ 축구 데이터 스캔 완료!"); time.sleep(1); status_text.empty(); progress_bar.empty()
        st.session_state['analyzed_data_list'] = new_data_list

# ==========================================
# ⚾ 야구(MLB/KBO/NPB 하이브리드 로직)
# ==========================================
elif selected_sport == "야구":
    analyze_button = st.sidebar.button("🚀 종합 야구 데이터 스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚾ 야구 리그 선택")
    
    with st.sidebar.expander("미국 야구 (정밀 시뮬레이션)", expanded=True): 
        c_mlb = st.checkbox("메이저리그 (MLB)", value=True)
    with st.sidebar.expander("아시아 야구 (API-Baseball 연동)", expanded=True): 
        c_kbo = st.checkbox("한국 프로야구 (KBO)", value=True)
        c_npb = st.checkbox("일본 프로야구 (NPB)", value=False)

    if analyze_button:
        st.session_state['analyzed_data_list'] = []
        progress_bar = st.progress(0); status_text = st.empty()
        new_data_list = []
        
        # 1. MLB 처리 로직
        if c_mlb:
            status_text.text(f"🔍 MLB 실시간 스탯 불러오는 중...")
            df_h, df_p, team_bp_fip = load_mlb_all_data()
            momentum_dict = load_mlb_team_momentum()
            progress_bar.progress(0.2)
            
            start_date_str = (selected_date - timedelta(days=1)).strftime('%Y-%m-%d')
            end_date_str = (selected_date + timedelta(days=1)).strftime('%Y-%m-%d')
            schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start_date_str}&endDate={end_date_str}&hydrate=probablePitcher"
            
            try:
                res = requests.get(schedule_url, timeout=5).json()
                all_games = []
                for date_data in res.get('dates', []):
                    all_games.extend(date_data.get('games', []))
                
                for idx, game in enumerate(all_games):
                    status_text.text(f"🔍 MLB 매치업 엔진 가동 중... ({idx+1}/{len(all_games)})")
                    progress_bar.progress(0.2 + (0.3 * (idx / max(len(all_games), 1))))
                    
                    try: 
                        utc_time = datetime.strptime(game.get('gameDate'), "%Y-%m-%dT%H:%M:%SZ")
                        kst_time = utc_time + timedelta(hours=9)
                        if kst_time.date() != selected_date: continue
                        match_time = kst_time.strftime("%H:%M")
                        is_past_start_time = datetime.utcnow() >= utc_time
                    except: 
                        match_time = "시간미정"
                        is_past_start_time = True
                    
                    game_pk = game.get('gamePk')
                    away_team = game['teams']['away']['team']['name']; home_team = game['teams']['home']['team']['name']
                    away_id = game['teams']['away']['team']['id']; home_id = game['teams']['home']['team']['id']
                    away_pitcher = game['teams']['away'].get('probablePitcher', {}).get('fullName', 'TBD'); home_pitcher = game['teams']['home'].get('probablePitcher', {}).get('fullName', 'TBD')
                    
                    home_pitcher_id = game['teams']['home'].get('probablePitcher', {}).get('id')
                    away_pitcher_id = game['teams']['away'].get('probablePitcher', {}).get('id')
                    
                    venue = game.get('venue', {}).get('name', '미정')
                    home_kr = translate_to_ko(home_team); away_kr = translate_to_ko(away_team)
                    status_code = game['status']['abstractGameState']
                    h_score = game['teams']['home'].get('score', 0); a_score = game['teams']['away'].get('score', 0)
                    
                    if status_code == 'Final': 
                        top_league_display = f"MLB ({match_time}) <br><span style='color:#aaa; font-size:12px;'>[경기 종료]</span>"
                        status_type = "finished"
                    elif status_code == 'Live' and is_past_start_time: 
                        top_league_display = f"MLB ({match_time}) <br><span style='color:#ff5252; font-size:12px;'>[진행중]</span>"
                        status_type = "live"
                    else: 
                        top_league_display = f"MLB ({match_time})"
                        status_type = "upcoming"
                        
                    h_logo_html = f"<img src='https://www.mlbstatic.com/team-logos/{home_id}.svg' class='team-logo'>"
                    a_logo_html = f"<img src='https://www.mlbstatic.com/team-logos/{away_id}.svg' class='team-logo'>"

                    if status_type == "finished": score_color = "#00E676"; score_text = f"{h_score}:{a_score}"
                    elif status_type == "live": score_color = "#ff5252"; score_text = f"{h_score}:{a_score}"
                    else: score_color = "#888888"; score_text = "VS"

                    match_display = f"<div class='match-box'><div class='team-side home-side'>{h_logo_html}<div class='team-name' title='{home_kr}'>{home_kr}</div></div><div class='score-side' style='color:{score_color};'>{score_text}</div><div class='team-side away-side'><div class='team-name' title='{away_kr}'>{away_kr}</div>{a_logo_html}</div></div>"

                    h_p_data = df_p[df_p['이름'] == home_pitcher]
                    a_p_data = df_p[df_p['이름'] == away_pitcher]
                    h_s_fip = h_p_data['FIP'].values[0] if not h_p_data.empty else 4.50
                    a_s_fip = a_p_data['FIP'].values[0] if not a_p_data.empty else 4.50
                    h_s_ip = h_p_data['평균이닝'].values[0] if not h_p_data.empty else 5.0
                    a_s_ip = a_p_data['평균이닝'].values[0] if not a_p_data.empty else 5.0
                    h_bp_fip = team_bp_fip.get(home_team, 4.00)
                    a_bp_fip = team_bp_fip.get(away_team, 4.00)
                    
                    h_lineup, a_lineup, h_p_hand, a_p_hand = load_mlb_live_lineup(game_pk, home_pitcher_id, away_pitcher_id)
                    
                    h_base_ops = df_h[(df_h['팀'] == home_team) & (df_h['타수'] > 50)]['OPS'].mean() or 0.720
                    a_base_ops = df_h[(df_h['팀'] == away_team) & (df_h['타수'] > 50)]['OPS'].mean() or 0.720
                    
                    h_platoon_ops = calculate_platoon_ops(h_lineup, df_h, a_p_hand, h_base_ops)
                    a_platoon_ops = calculate_platoon_ops(a_lineup, df_h, h_p_hand, a_base_ops)
                    
                    h_momentum = momentum_dict.get(home_team, 0.5) 
                    a_momentum = momentum_dict.get(away_team, 0.5)
                    h_recent_modifier = 1.0 + (h_momentum - 0.5) * 0.5
                    a_recent_modifier = 1.0 + (a_momentum - 0.5) * 0.5
                    
                    h_final_ops = (h_platoon_ops * 0.7) + (h_platoon_ops * h_recent_modifier * 0.3)
                    a_final_ops = (a_platoon_ops * 0.7) + (a_platoon_ops * a_recent_modifier * 0.3)
                    pf = MLB_PARK_FACTORS.get(home_team, 1.00)

                    h_win_prob, a_win_prob, h_exp_runs, a_exp_runs = run_mlb_simulation(h_s_fip, a_s_fip, h_s_ip, a_s_ip, h_final_ops, a_final_ops, h_bp_fip, a_bp_fip, pf)
                    
                    odds_h = max(1.10, min(round(0.94 / (h_win_prob/100), 2), 6.00)) if h_win_prob > 0 else 0
                    odds_a = max(1.10, min(round(0.94 / (a_win_prob/100), 2), 6.00)) if a_win_prob > 0 else 0
                    
                    if h_win_prob > a_win_prob + 10: win_pick, pick_color = f"🟢 {home_kr} 승 유력", "#00E676"
                    elif a_win_prob > h_win_prob + 10: win_pick, pick_color = f"🔵 {away_kr} 승 유력", "#4FC3F7"
                    else: win_pick, pick_color = "🟡 팽팽한 접전", "#ff9800"
                    
                    if status_type == 'finished':
                        actual = "home" if h_score > a_score else "away"
                        if (actual == "home" and h_win_prob > a_win_prob) or (actual == "away" and a_win_prob > h_win_prob): win_pick += " (적중)"; pick_color = "#ffcc00"
                        else: win_pick += " (미적중)"; pick_color = "#ff5252"

                    stat_box = f"<span style='color:#aaa;'>AI 배당:</span> 홈 <b style='color:#ff9800;'>{odds_h:.2f}</b> | 원정 <b style='color:#ff9800;'>{odds_a:.2f}</b><br><span style='color:#aaa;'>기대 득점:</span> {home_kr} <b>{h_exp_runs:.1f}</b> vs <b>{a_exp_runs:.1f}</b> {away_kr}"
                    
                    total_exp_runs = h_exp_runs + a_exp_runs
                    ou_line = 8.5
                    ou_color = "#ddd"
                    
                    if total_exp_runs > 9.0: pred_is_over = True; ou_text = f"🔥 총 {total_exp_runs:.1f}점 (기준 8.5 오버)"
                    elif total_exp_runs < 8.0: pred_is_over = False; ou_text = f"❄️ 총 {total_exp_runs:.1f}점 (기준 8.5 언더)"
                    else: pred_is_over = None; ou_text = f"⚠️ 총 {total_exp_runs:.1f}점 (기준 8.5 패스)"

                    if status_type == 'finished':
                        actual_total = h_score + a_score
                        if pred_is_over is not None:
                            actual_is_over = actual_total > ou_line
                            if actual_is_over == pred_is_over:
                                over_under = f"{ou_text} (적중)"
                                ou_color = "#FFF59D" 
                            else:
                                over_under = f"{ou_text} (미적중)"
                                ou_color = "#F48FB1" 
                        else: over_under = ou_text
                    else: over_under = ou_text
                    
                    advice = "플래툰(좌우 상성)과 최근 기세(30%)를 추가 반영한 심층 시뮬레이션입니다."

                    detail_html = get_baseball_detailed_html(home_kr, away_kr, home_pitcher, away_pitcher, h_s_fip, a_s_fip, h_bp_fip, a_bp_fip, h_final_ops, a_final_ops, h_s_ip, a_s_ip)
                    lineup_html = get_baseball_lineup_html(home_kr, away_kr, h_lineup, a_lineup)
                    ref_text = f"🏟️ {venue} | 投: {home_pitcher}({h_p_hand}) vs {away_pitcher}({a_p_hand})"

                    new_data_list.append({"sport": "야구", "league": top_league_display, "match_display": match_display, "stat_box": stat_box, "referee": ref_text, "venue": venue, "p_h": f"{h_win_prob:.0f}", "p_d": "0", "p_a": f"{a_win_prob:.0f}", "win_pick": win_pick, "pick_color": pick_color, "ou_color": ou_color, "control_pick": advice, "over_under": over_under, "lineup_html": lineup_html, "detail_html": detail_html, "radar_html": ""})
            except: pass

        # 2. KBO/NPB 처리 로직
        if c_kbo or c_npb:
            BASEBALL_URL = "https://v1.baseball.api-sports.io/"
            api_leagues = []
            if c_kbo: api_leagues.append(("5", "KBO"))
            if c_npb: api_leagues.append(("2", "NPB")) 
            
            for idx, (l_id, l_name) in enumerate(api_leagues):
                status_text.text(f"🔍 {l_name} 유료 API(팀 전력) 스캔 중...")
                progress_bar.progress(0.6 + (0.4 * (idx / len(api_leagues))))
                querystring = {"league": l_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
                
                try:
                    res = requests.get(BASEBALL_URL + "games", headers=HEADERS, params=querystring, timeout=10).json()
                    for match in res.get('response', []):
                        game_id = str(match['id'])
                        home_en = match['teams']['home']['name']
                        away_en = match['teams']['away']['name']
                        home_kr = translate_to_ko(home_en); away_kr = translate_to_ko(away_en)
                        
                        try:
                            timestamp = match['timestamp']
                            utc_time = datetime.utcfromtimestamp(timestamp)
                            kst_time = utc_time + timedelta(hours=9)
                            match_time = kst_time.strftime("%H:%M")
                            is_past_start_time = datetime.utcnow() >= utc_time 
                        except: match_time = "시간미정"; is_past_start_time = True
                            
                        status_short = match['status']['short']
                        is_finished = status_short in ['FT', 'AOT', 'F/O']
                        is_live = status_short not in ['NS', 'FT', 'AOT', 'CANC', 'PST', 'F/O'] and is_past_start_time
                        
                        top_display = f"{l_name} ({match_time}) "
                        if is_finished: top_display += "<br><span style='color:#aaa; font-size:12px;'>[경기 종료]</span>"
                        elif is_live: top_display += "<br><span style='color:#ff5252; font-size:12px;'>[진행중]</span>"
                        
                        h_score = match['scores']['home']['total'] if match['scores']['home']['total'] is not None else 0
                        a_score = match['scores']['away']['total'] if match['scores']['away']['total'] is not None else 0
                        score_color = "#00E676" if is_finished else ("#ff5252" if is_live else "#888")
                        score_text = f"{h_score}:{a_score}" if is_finished or is_live else "VS"
                        
                        h_logo_html = f"<img src='{match['teams']['home']['logo']}' class='team-logo'>"
                        a_logo_html = f"<img src='{match['teams']['away']['logo']}' class='team-logo'>"
                        match_display = f"<div class='match-box'><div class='team-side home-side'>{h_logo_html}<div class='team-name' title='{home_kr}'>{home_kr}</div></div><div class='score-side' style='color:{score_color};'>{score_text}</div><div class='team-side away-side'><div class='team-name' title='{away_kr}'>{away_kr}</div>{a_logo_html}</div></div>"
                        
                        odds_res = requests.get(BASEBALL_URL + "odds", headers=HEADERS, params={"game": game_id}).json()
                        odds_h = odds_a = 0.0; ou_line = 8.5
                        if odds_res and odds_res.get('response'):
                            for b in odds_res['response'][0].get('bookmakers', [])[0].get('bets', []):
                                if b['name'] == 'Home/Away':
                                    for v in b['values']:
                                        if str(v['value']) == 'Home': odds_h = float(v['odd'])
                                        elif str(v['value']) == 'Away': odds_a = float(v['odd'])
                                elif b['name'] == 'Over/Under':
                                    for v in b['values']:
                                        if 'Over' in str(v['value']):
                                            try: ou_line = float(str(v['value']).replace('Over', '').strip())
                                            except: pass
                                            break

                        pred_res = requests.get(BASEBALL_URL + "predictions", headers=HEADERS, params={"game": game_id}).json()
                        p_h, p_a = 50, 50
                        radar_html = ""
                        advice = "상위 팀 전력 분석 완료"
                        
                        if pred_res and pred_res.get('response'):
                            pred = pred_res['response'][0]
                            wp = pred.get('predictions', {}).get('percent', {})
                            p_h = safe_num(wp.get('home', '50')); p_a = safe_num(wp.get('away', '50'))
                            
                            comp = pred.get('comparison', {})
                            h_vals = [safe_num(comp.get('att', {}).get('home')), safe_num(comp.get('def', {}).get('home')), safe_num(comp.get('form', {}).get('home')), safe_num(comp.get('h2h', {}).get('home')), 50, 50]
                            a_vals = [safe_num(comp.get('att', {}).get('away')), safe_num(comp.get('def', {}).get('away')), safe_num(comp.get('form', {}).get('away')), safe_num(comp.get('h2h', {}).get('away')), 50, 50]
                            
                            h_vals[4] = (h_vals[0] + h_vals[2]) / 2  
                            h_vals[5] = sum(h_vals[:5]) / 5          
                            a_vals[4] = (a_vals[0] + a_vals[2]) / 2
                            a_vals[5] = sum(a_vals[:5]) / 5
                            
                            radar_html = create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom=False)
                            advice = translate_to_ko(pred.get('predictions', {}).get('advice', advice))
                        else:
                            if odds_h > 0 and odds_a > 0:
                                raw_h = (1 / odds_h) * 100; raw_a = (1 / odds_a) * 100
                                p_h = round((raw_h / (raw_h + raw_a)) * 100); p_a = 100 - p_h
                            else: p_h, p_a = 55, 45 
                                
                        if p_h > p_a + 5: win_pick, pick_color = f"🟢 {home_kr} 승 유력", "#00E676"
                        elif p_a > p_h + 5: win_pick, pick_color = f"🔵 {away_kr} 승 유력", "#4FC3F7"
                        else: win_pick, pick_color = "🟡 팽팽한 접전", "#ff9800"
                        
                        if is_finished:
                            actual = "home" if h_score > a_score else "away"
                            if (actual == "home" and p_h > p_a) or (actual == "away" and p_a > p_h): win_pick += " (적중)"; pick_color = "#ffcc00"
                            else: win_pick += " (미적중)"; pick_color = "#ff5252"

                        h_exp = 4.5 * (p_h/50); a_exp = 4.5 * (p_a/50)
                        total_exp_runs = h_exp + a_exp
                        
                        if total_exp_runs > ou_line + 0.5: pred_is_over = True; ou_text = f"🔥 총 {total_exp_runs:.1f}점 (기준 {ou_line} 오버)"
                        elif total_exp_runs < ou_line - 0.5: pred_is_over = False; ou_text = f"❄️ 총 {total_exp_runs:.1f}점 (기준 {ou_line} 언더)"
                        else: pred_is_over = None; ou_text = f"⚠️ 총 {total_exp_runs:.1f}점 (기준 {ou_line} 패스)"
                        
                        ou_color = "#ddd"
                        if is_finished:
                            actual_total = h_score + a_score
                            if pred_is_over is not None:
                                if (actual_total > ou_line) == pred_is_over: ou_text += " (적중)"; ou_color = "#FFF59D"
                                else: ou_text += " (미적중)"; ou_color = "#F48FB1"

                        odds_text = f"홈 <b style='color:#ff9800;'>{odds_h}</b> | 원정 <b style='color:#ff9800;'>{odds_a}</b>" if odds_h > 0 else "해외 배당 미발매"
                        stat_box = f"<span style='color:#aaa;'>해외 배당:</span> {odds_text}<br><span style='color:#aaa;'>AI 산출 확률:</span> {home_kr} <b>{p_h:.0f}%</b> vs <b>{p_a:.0f}%</b> {away_kr}"
                        
                        detail_html = f"<div style='text-align:center; padding:10px; color:#aaa;'>아시아 야구(KBO/NPB)는 API 제공사의 정책으로 인해<br>개인 선수 기록(라인업)이 블라인드 처리됩니다.<br>대신 <b>팀 전체의 기세(Form)와 상대 전적(H2H)</b>을 분석한<br>전력 레이더망 데이터가 적용되었습니다.</div>"
                        
                        ref_text = f"🏟️ {home_kr} 홈 구장"
                        
                        new_data_list.append({"sport": "야구", "league": top_display, "match_display": match_display, "stat_box": stat_box, "referee": ref_text, "venue": "", "p_h": f"{p_h:.0f}", "p_d": "0", "p_a": f"{p_a:.0f}", "win_pick": win_pick, "pick_color": pick_color, "ou_color": ou_color, "control_pick": advice, "over_under": ou_text, "lineup_html": "", "detail_html": detail_html, "radar_html": radar_html})
                except: pass

        if not new_data_list: st.info(f"해당 날짜({selected_date})에 한국시간 기준으로 시작하는 경기가 없습니다.")
        progress_bar.progress(1.0); status_text.text("✅ 궁극의 데이터 스캔 완료!"); time.sleep(1); status_text.empty(); progress_bar.empty()
        st.session_state['analyzed_data_list'] = new_data_list

# ==========================================
# 🏀 농구 / 🏐 배구 (추후 업데이트)
# ==========================================
elif selected_sport in ["농구", "배구"]:
    st.sidebar.button(f"🚀 {selected_sport} 데이터 딥-스캔 시작", use_container_width=True, disabled=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {selected_sport} 리그 선택 (준비중)")

# ==========================================
# 📺 공통 렌더링 엔진 (결과 출력)
# ==========================================
if st.session_state.get('analyzed_data_list'):
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_data_list']):
        with cols[idx % 3]:
            if data['sport'] == "야구":
                prob_bar = f"<div class='prob-wrapper'><div class='prob-text'><span>홈 승 {data['p_h']}%</span><span>원정 승 {data['p_a']}%</span></div><div class='prob-container'><div class='prob-home' style='width: {data['p_h']}%;'></div><div class='prob-away' style='width: {data['p_a']}%;'></div></div></div>"
            else:
                prob_bar = f"<div class='prob-wrapper'><div class='prob-text'><span>승 {data['p_h']}%</span><span>무 {data['p_d']}%</span><span>패 {data['p_a']}%</span></div><div class='prob-container'><div class='prob-home' style='width: {data['p_h']}%;'></div><div class='prob-draw' style='width: {data['p_d']}%;'></div><div class='prob-away' style='width: {data['p_a']}%;'></div></div></div>"
            
            html_str = f"""
            <div style='height: 100%;'>
                <div class='card-box'>
                    <div class='card-top'>
                        <div class='league-txt'>{data['league']}</div>
                        {data['match_display']}
                        <div class='referee-txt'>{data['referee']}</div>
                    </div>
                    <div class='card-mid'>
                        {prob_bar}
                        <div class='stat-bg'>{data['stat_box']}</div>
                    </div>
                    <div class='card-bot'>
                        <div class='predict-txt' style='color: {data['pick_color']};'>🎯 {data['win_pick']}</div>
                        <div class='over-under' style='color: {data['ou_color']};'>{data['over_under']}</div>
                        <div class='ai-advice'>⚔️ {data['control_pick']}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_str, unsafe_allow_html=True)
            
            # 💡 핵심: 축구와 야구(KBO/NPB) 모두 레이더 차트가 렌더링되도록 제한(if data['sport']=="축구") 삭제
            with st.expander("🔍 상세 지표 & 선발 명단 확인"):
                if data.get('radar_html'): st.markdown(data['radar_html'], unsafe_allow_html=True)
                if data.get('detail_html'): st.markdown(data['detail_html'], unsafe_allow_html=True)
                if data.get('lineup_html'): st.markdown(data['lineup_html'], unsafe_allow_html=True)
            st.write("")
elif st.session_state.get('analyzed_data_list') == []: st.markdown("")
