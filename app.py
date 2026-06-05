import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import random
import math
import json

st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

FOOTBALL_API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
HEADERS = {'x-apisports-key': FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}

# 💡 구글 라이브러리 설치(import) 없이, 다이렉트 REST API 통신망 사용 (오류 원천 차단)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# 🎨 UI CSS
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.stApp { background-color: #0e1117; }
.card-box { background-color: #1e1e1e; padding: 20px; border-radius: 12px; border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 25px; display: flex; flex-direction: column; height: 550px; }
.card-box p { margin: 0 !important; padding: 0 !important; line-height: 1.5 !important; }
.card-top { flex-shrink: 0; }
.card-mid { flex-grow: 1; display: flex; flex-direction: column; justify-content: center; margin: 10px 0; }
.card-bot { flex-shrink: 0; border-top: 1px dashed #555; padding-top: 15px; text-align: center; }
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; letter-spacing: 1px; }
.match-box { display: flex; align-items: center; justify-content: center; width: 100%; margin-bottom: 5px; }
.team-side { display: flex; align-items: center; width: 38%; gap: 6px; }
.home-side { justify-content: flex-end; text-align: right; }
.away-side { justify-content: flex-start; text-align: left; }
.team-name { font-size: 13.5px; font-weight: bold; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 85px; }
.score-side { width: 24%; font-size: 20px; font-weight: bold; text-align: center; flex-shrink: 0; white-space: nowrap; letter-spacing: 0.5px; }
.team-logo { width: 26px; height: 26px; object-fit: contain; flex-shrink: 0; background-color: #fff; border-radius: 50%; padding: 2px; }
.referee-txt { font-size: 11px; color: #888; text-align: center; margin-bottom: 5px; }
.prob-wrapper { width: 100%; margin-bottom: 10px; }
.prob-text { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 4px; }
.prob-container { display: flex; width: 100%; height: 8px; border-radius: 4px; overflow: hidden; background-color: #333; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }
.stat-bg { background-color: #262730; padding: 12px; border-radius: 8px; color: #eeeeee; font-size: 12.5px; line-height: 1.6; text-align: center; border: 1px solid #444; width: 100%; }
.predict-txt { font-size: 14.5px; font-weight: bold; margin-bottom: 5px; }
.handi-txt { font-size: 14.5px; font-weight: bold; margin-bottom: 5px; } 
.over-under { font-size: 14.5px; font-weight: bold; margin-bottom: 8px; } 
.ai-advice { font-size: 11.5px; color: #aaa; font-weight: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; white-space: normal; }
.table-wrapper { width: 100%; overflow-x: auto; margin-top: 5px; margin-bottom: 15px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 12px; color: #ccc; text-align: center; table-layout: fixed; } 
.detail-table th { background-color: #111; padding: 10px 5px; border-bottom: 2px solid #555; color: #fff; white-space: nowrap; }
.detail-table td { padding: 8px 5px; border-bottom: 1px solid #2a2a2a; word-wrap: break-word; } 
.injury-tag { color: #ff5252; font-size: 11px; background: #331111; padding: 3px 6px; border-radius: 4px; display: inline-block; margin: 2px; }
.sim-box { background-color:#0a0a14; padding:15px; border-radius:8px; border:1px solid #4FC3F7; margin-top:10px; }

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

CUSTOM_DICT = {"Arsenal": "아스날", "Aston Villa": "애스턴 빌라", "Newcastle": "뉴캐슬", "Crystal Palace": "크리스탈 팰리스", "Athletics": "애슬레틱스", "Oakland Athletics": "오클랜드", "Oakland": "오클랜드", "Arizona Diamondbacks": "애리조나", "Atlanta Braves": "애틀랜타", "Baltimore Orioles": "볼티모어", "Boston Red Sox": "보스턴", "Chicago Cubs": "시카고 컵스", "Chicago White Sox": "화이트삭스", "Cincinnati Reds": "신시내티", "Cleveland Guardians": "클리블랜드", "Colorado Rockies": "콜로라도", "Detroit Tigers": "디트로이트", "Houston Astros": "휴스턴", "Kansas City Royals": "캔자스시티", "Los Angeles Angels": "LA 에인절스", "Los Angeles Dodgers": "LA 다저스", "Miami Marlins": "마이애미", "Milwaukee Brewers": "밀워키", "Minnesota Twins": "미네소타", "New York Mets": "NY 메츠", "New York Yankees": "NY 양키스", "Philadelphia Phillies": "필라델피아", "Pittsburgh Pirates": "피츠버그", "San Diego Padres": "샌디에이고", "San Francisco Giants": "샌프란시스코", "Seattle Mariners": "시애틀", "St. Louis Cardinals": "세인트루이스", "Tampa Bay Rays": "탬파베이", "Texas Rangers": "텍사스", "Toronto Blue Jays": "토론토", "Washington Nationals": "워싱턴", "LG Twins": "LG 트윈스", "KT Wiz": "KT 위즈", "Samsung Lions": "삼성 라이온즈", "KIA Tigers": "KIA 타이거즈", "Hanwha Eagles": "한화 이글스", "Doosan Bears": "두산 베어스", "NC Dinos": "NC 다이노스", "SSG Landers": "SSG 랜더스", "Lotte Giants": "롯데 자이언츠", "Kiwoom Heroes": "키움 히어로즈", "Yomiuri Giants": "요미우리", "Hanshin Tigers": "한신", "Hiroshima Toyo Carp": "히로시마", "Chunichi Dragons": "주니치", "Yokohama DeNA BayStars": "요코하마", "Tokyo Yakult Swallows": "야쿠르트", "Orix Buffaloes": "오릭스", "Fukuoka SoftBank Hawks": "소프트뱅크", "Hokkaido Nippon-Ham Fighters": "니혼햄", "Chiba Lotte Marines": "지바롯데", "Saitama Seibu Lions": "세이부", "Tohoku Rakuten Golden Eagles": "라쿠텐", "Boston Celtics": "보스턴", "Dallas Mavericks": "댈러스", "Denver Nuggets": "덴버", "Minnesota Timberwolves": "미네소타", "Oklahoma City Thunder": "오클라호마시티", "New York Knicks": "뉴욕 닉스", "Indiana Pacers": "인디애나", "Los Angeles Lakers": "LA 레이커스", "Golden State Warriors": "골든스테이트", "Miami Heat": "마이애미", "Philadelphia 76ers": "필라델피아", "Milwaukee Bucks": "밀워키", "Phoenix Suns": "피닉스", "LA Clippers": "LA 클리퍼스", "Los Angeles Clippers": "LA 클리퍼스", "Sacramento Kings": "새크라멘토", "New Orleans Pelicans": "뉴올리언스", "Cleveland Cavaliers": "클리블랜드", "Orlando Magic": "올랜도", "Chicago Bulls": "시카고", "Atlanta Hawks": "애틀랜타", "Brooklyn Nets": "브루클린", "Toronto Raptors": "토론토", "Washington Wizards": "워싱턴", "Charlotte Hornets": "샬럿", "Detroit Pistons": "디트로이트", "San Antonio Spurs": "샌안토니오", "Houston Rockets": "휴스턴", "Memphis Grizzlies": "멤피스", "Utah Jazz": "유타", "Portland Trail Blazers": "포틀랜드"}

@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or str(text).strip() in ['', 'N/A']: return '데이터 분석 중'
    for eng, kor in CUSTOM_DICT.items():
        if eng.lower() == str(text).lower() or eng in str(text): return kor
    try: return GoogleTranslator(source='en', target='ko').translate(str(text).replace('<', '').replace('>', ''))
    except Exception: return str(text)

def safe_num(value):
    if not value or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except Exception: return 0.0

@st.cache_data(ttl=600, show_spinner=False)
def fetch_api_football_fixtures(league_id, season, date_str):
    try: return requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"league": league_id, "season": season, "date": date_str, "timezone": "Asia/Seoul"}, timeout=10).json().get('response') or []
    except Exception: return []

@st.cache_data(ttl=600, show_spinner=False)
def fetch_api_football_by_fixture(endpoint, fix_id):
    try: return requests.get(f"https://v3.football.api-sports.io/{endpoint}", headers=HEADERS, params={"fixture": fix_id}, timeout=10).json().get('response') or []
    except Exception: return []

def create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom=False):
    labels = ['공격력', '수비력', '최근폼', '상대전적', '득점력', '종합전력']
    size = 220; center = size / 2; max_val = 100
    pts_h = " ".join([f"{center + (v/max_val)*(size*0.35)*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (v/max_val)*(size*0.35)*math.sin((math.pi*2/6)*i - math.pi/2)}" for i, v in enumerate(h_vals)])
    pts_a = " ".join([f"{center + (v/max_val)*(size*0.35)*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (v/max_val)*(size*0.35)*math.sin((math.pi*2/6)*i - math.pi/2)}" for i, v in enumerate(a_vals)])
    svg = ""
    for i in range(6):
        ang = (math.pi * 2 / 6) * i - (math.pi / 2); x = center + (size * 0.35) * math.cos(ang); y = center + (size * 0.35) * math.sin(ang)
        svg += f"<line x1='{center}' y1='{center}' x2='{x}' y2='{y}' style='stroke:#444; stroke-width:1;' />"
        lx = center + (size * 0.44) * math.cos(ang); ly = center + (size * 0.44) * math.sin(ang)
        anchor = "start" if lx > center + 10 else ("end" if lx < center - 10 else "middle")
        svg += f"<text x='{lx}' y='{ly+4}' fill='#ddd' font-size='10' font-weight='bold' text-anchor='{anchor}'>{labels[i]}</text>"
    for ratio in [0.33, 0.66, 1.0]:
        pts = " ".join([f"{center + (size*0.35)*ratio*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (size*0.35)*ratio*math.sin((math.pi*2/6)*i - math.pi/2)}" for i in range(6)])
        svg += f"<polygon points='{pts}' style='fill:none; stroke:#333; stroke-width:1;' />"
    h_poly = f"<polygon points='{pts_h}' style='fill:rgba(79, 195, 247, 0.3); stroke:#4FC3F7; stroke-width:2; opacity:0.6;' />"
    a_poly = f"<polygon points='{pts_a}' style='fill:rgba(239, 83, 80, 0.3); stroke:#EF5350; stroke-width:2; opacity:0.6;' />"
    badge = "<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ 전력 분석망 데이터</div>" if not is_custom else "<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ 자체 AI 데이터 연산</div>"
    return f"<div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:10px; margin-bottom: 10px;'>{badge}<div style='font-size:11px; color:#fff; margin-bottom:10px; font-weight:bold; text-align:center;'><span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}</div><svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>{svg}{h_poly}{a_poly}</svg></div>"

def fetch_custom_team_stats(team_id, season_year):
    try:
        fixtures = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"team": team_id, "last": 5, "season": season_year}).json().get('response') or []
        if not fixtures: return 10, 10, 10 
        wins = 0; goals_for = 0; goals_against = 0
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
    except Exception: return 20, 20, 20

def get_football_detailed_html(home_kr, away_kr, h_rank, a_rank, h_goals, a_goals, h_goals_against, a_goals_against, h_injuries, a_injuries):
    h_inj_html = "".join([f"<span class='injury-tag'>🚑 {inj}</span>" for inj in h_injuries]) or "<span style='color:#888;'>결장자 없음</span>"
    a_inj_html = "".join([f"<span class='injury-tag'>🚑 {inj}</span>" for inj in a_injuries]) or "<span style='color:#888;'>결장자 없음</span>"
    return f"<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7; width:40%;'>{home_kr}</th><th style='width:20%; color:#aaa;'>비교 지표</th><th style='color:#EF5350; width:40%;'>{away_kr}</th></tr><tr><td><b>{h_rank}</b>위</td><td style='font-size:11px;'>리그 순위</td><td><b>{a_rank}</b>위</td></tr><tr><td>{h_goals}골</td><td style='font-size:11px;'>평균 득점</td><td>{a_goals}골</td></tr><tr><td>{h_goals_against}골</td><td style='font-size:11px;'>평균 실점</td><td>{a_goals_against}골</td></tr><tr><td style='white-space:normal;'>{h_inj_html}</td><td style='font-size:11px;'>결장/부상</td><td style='white-space:normal;'>{a_inj_html}</td></tr></table></div>"

def get_lineup_table(home_kr, away_kr, lineup_data):
    try:
        if not lineup_data or not isinstance(lineup_data, list) or len(lineup_data) < 2: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표</div>"
        h_p = [p['player']['name'].split()[-1] for p in (lineup_data[0].get('startXI') or [])]
        a_p = [p['player']['name'].split()[-1] for p in (lineup_data[1].get('startXI') or [])]
        m_len = max(len(h_p), len(a_p))
        if m_len == 0: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표</div>"
        h_p += [""] * (m_len - len(h_p)); a_p += [""] * (m_len - len(a_p))
        html = f"<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7;'>{home_kr} (선발)</th><th style='color:#EF5350;'>{away_kr} (선발)</th></tr>"
        for h, a in zip(h_p, a_p): html += f"<tr><td>{h}</td><td>{a}</td></tr>"
        return html + "</table></div>"
    except Exception: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표</div>"

MLB_PARK_FACTORS = {'Colorado Rockies': 1.12, 'Cincinnati Reds': 1.08, 'Boston Red Sox': 1.07, 'Texas Rangers': 1.05, 'Chicago White Sox': 1.04, 'Atlanta Braves': 1.03, 'Los Angeles Dodgers': 1.03, 'Philadelphia Phillies': 1.02, 'Houston Astros': 1.01, 'Baltimore Orioles': 1.00, 'Toronto Blue Jays': 1.00, 'Minnesota Twins': 1.00, 'Chicago Cubs': 1.00, 'New York Yankees': 1.00, 'Kansas City Royals': 0.99, 'Arizona Diamondbacks': 0.99, 'Milwaukee Brewers': 0.98, 'Los Angeles Angels': 0.98, 'Washington Nationals': 0.98, 'San Francisco Giants': 0.97, 'Miami Marlins': 0.97, 'Pittsburgh Pirates': 0.96, 'Cleveland Guardians': 0.96, 'St. Louis Cardinals': 0.96, 'Detroit Tigers': 0.95, 'Tampa Bay Rays': 0.95, 'New York Mets': 0.95, 'Athletics': 0.94, 'San Diego Padres': 0.94, 'Seattle Mariners': 0.93}

@st.cache_data(ttl=3600)
def load_mlb_all_data():
    try:
        h_splits = requests.get("https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&gameType=R&season=2026&playerPool=ALL&limit=1500").json().get('stats', [{}])[0].get('splits') or []
        df_h = pd.DataFrame([{'이름': r['player']['fullName'], '팀': r['team']['name'], '타수': r['stat'].get('atBats', 0), 'OPS': r['stat'].get('ops', '.000')} for r in h_splits])
        df_h['OPS'] = pd.to_numeric(df_h['OPS'], errors='coerce').fillna(0.0); df_h['타수'] = pd.to_numeric(df_h['타수'], errors='coerce').fillna(0)
        p_splits = requests.get("https://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&gameType=R&season=2026&playerPool=ALL&limit=1500").json().get('stats', [{}])[0].get('splits') or []
        df_p = pd.DataFrame([{'이름': r['player']['fullName'], '팀': r['team']['name'], '출장': r['stat'].get('gamesPlayed', 0), '선발': r['stat'].get('gamesStarted', 0), '이닝': r['stat'].get('inningsPitched', '0.0'), '피홈런': r['stat'].get('homeRuns', 0), '볼넷': r['stat'].get('baseOnBalls', 0), '탈삼진': r['stat'].get('strikeOuts', 0)} for r in p_splits])
        df_p['이닝_num'] = pd.to_numeric(df_p['이닝'], errors='coerce').fillna(0.0)
        df_p['평균이닝'] = df_p.apply(lambda x: x['이닝_num'] / x['선발'] if x['선발'] > 0 else 4.0, axis=1).clip(3.0, 7.5)
        df_p['FIP'] = df_p.apply(lambda x: ((13*x['피홈런'] + 3*x['볼넷'] - 2*x['탈삼진']) / x['이닝_num']) + 3.10 if x['이닝_num'] > 0 else 4.50, axis=1)
        team_bullpen_fip = df_p[(df_p['출장'] > df_p['선발']) & (df_p['이닝_num'] >= 5.0)].groupby('팀')['FIP'].mean().to_dict()
        return df_h, df_p, team_bullpen_fip
    except Exception: return pd.DataFrame(), pd.DataFrame(), {}

@st.cache_data(ttl=3600)
def load_mlb_team_momentum():
    try:
        res = requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104", timeout=5).json()
        l10_dict = {}
        for record in res.get('records') or []:
            for team in record.get('teamRecords') or []:
                for split in team.get('records', {}).get('splitRecords') or []:
                    if split['type'] == 'lastTen': l10_dict[team['team']['name']] = split['wins'] / max((split['wins'] + split['losses']), 1)
        return l10_dict
    except Exception: return {}

def load_mlb_live_lineup(game_pk, home_pitcher_id, away_pitcher_id):
    try:
        res = requests.get(f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore").json()
        h_players = res.get('teams', {}).get('home', {}).get('players') or {}; a_players = res.get('teams', {}).get('away', {}).get('players') or {}
        h_p_hand = 'R'; a_p_hand = 'R'
        if home_pitcher_id: h_p_hand = h_players.get(f"ID{home_pitcher_id}", h_players.get(f"ID_{home_pitcher_id}", {})).get('person', {}).get('pitchHand', {}).get('code', 'R')
        if away_pitcher_id: a_p_hand = a_players.get(f"ID{away_pitcher_id}", a_players.get(f"ID_{away_pitcher_id}", {})).get('person', {}).get('pitchHand', {}).get('code', 'R')
        h_lineup, a_lineup = [], []
        for pid in res.get('teams', {}).get('home', {}).get('battingOrder') or []:
            p = h_players.get(f"ID{pid}", h_players.get(f"ID_{pid}", {}))
            if p: h_lineup.append({'name': p.get('person', {}).get('fullName', 'Unknown'), 'batSide': p.get('person', {}).get('batSide', {}).get('code', 'R')})
        for pid in res.get('teams', {}).get('away', {}).get('battingOrder') or []:
            p = a_players.get(f"ID{pid}", a_players.get(f"ID_{pid}", {}))
            if p: a_lineup.append({'name': p.get('person', {}).get('fullName', 'Unknown'), 'batSide': p.get('person', {}).get('batSide', {}).get('code', 'R')})
        return h_lineup, a_lineup, h_p_hand, a_p_hand
    except Exception: return [], [], 'R', 'R'

def calculate_platoon_ops(lineup, df_hitters, opp_p_hand, base_team_ops):
    if not lineup: return base_team_ops
    total_ops = 0
    for batter in lineup:
        b_stats = df_hitters[df_hitters['이름'] == batter['name']]
        b_ops = b_stats['OPS'].values[0] if not b_stats.empty and b_stats['OPS'].values[0] > 0 else base_team_ops
        if opp_p_hand == 'L': b_ops *= 0.90 if batter['batSide'] == 'L' else 1.05
        else: b_ops *= 0.95 if batter['batSide'] == 'R' else 1.05
        total_ops += b_ops
    return total_ops / len(lineup)

def run_mlb_simulation(h_fip, a_fip, h_avg_ip, a_avg_ip, h_ops, a_ops, h_bp_fip, a_bp_fip, park_factor, num_sims=5000):
    h_starter_w = h_avg_ip / 9.0; a_starter_w = a_avg_ip / 9.0
    h_eff_fip = (h_fip * h_starter_w) + (h_bp_fip * (1 - h_starter_w)); a_eff_fip = (a_fip * a_starter_w) + (a_bp_fip * (1 - a_starter_w))
    h_expected_runs = ((a_eff_fip * (h_ops / 0.720)) + 0.2) * park_factor; a_expected_runs = (h_eff_fip * (a_ops / 0.720)) * park_factor
    h_wins, a_wins = 0, 0
    h_tie_win_prob = h_expected_runs / (h_expected_runs + a_expected_runs) if (h_expected_runs + a_expected_runs) > 0 else 0.5
    for _ in range(num_sims):
        h_score = max(0, int(random.gauss(h_expected_runs, 2.3))); a_score = max(0, int(random.gauss(a_expected_runs, 2.3)))
        if h_score == a_score: h_score += 1 if random.random() < h_tie_win_prob else (a_score + 1)
        if h_score > a_score: h_wins += 1
        elif a_score > h_score: a_wins += 1
    return (h_wins / num_sims) * 100, (a_wins / num_sims) * 100, h_expected_runs, a_expected_runs

def get_baseball_detailed_html(home_team, away_team, h_p, a_p, h_s_fip, a_s_fip, h_bp_fip, a_bp_fip, h_ops, a_ops, h_ip, a_ip):
    return f"<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7; width:40%;'>{home_team}</th><th style='width:20%; color:#aaa;'>투타 지표</th><th style='color:#EF5350; width:40%;'>{away_team}</th></tr><tr><td><b>{h_p}</b> <span style='font-size:11px; color:#888;'>({h_ip:.1f}이닝)</span></td><td style='font-size:11px;'>선발 투수</td><td><b>{a_p}</b> <span style='font-size:11px; color:#888;'>({a_ip:.1f}이닝)</span></td></tr><tr><td>{h_s_fip:.2f}</td><td style='font-size:11px;'>선발 방어율/FIP</td><td>{a_s_fip:.2f}</td></tr><tr><td>{h_bp_fip:.2f}</td><td style='font-size:11px;'>불펜 FIP</td><td>{a_bp_fip:.2f}</td></tr><tr><td>{h_ops:.3f}</td><td style='font-size:11px;'>팀 평균 OPS</td><td>{a_ops:.3f}</td></tr></table></div>"

def get_baseball_lineup_html(home_team, away_team, h_lineup, a_lineup):
    try:
        if not h_lineup and not a_lineup: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표 (시즌 평균 데이터 연산 적용)</div>"
        m_len = max(len(h_lineup), len(a_lineup))
        h_strs = [f"{b['name']} ({b['batSide']})" for b in h_lineup]; a_strs = [f"{b['name']} ({b['batSide']})" for b in a_lineup]
        h_strs += [""] * (m_len - len(h_strs)); a_strs += [""] * (m_len - len(a_strs))
        html = f"<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7;'>{home_team} (타석)</th><th style='color:#EF5350;'>{away_team} (타석)</th></tr>"
        for i, (h, a) in enumerate(zip(h_strs, a_strs)): html += f"<tr><td>{i+1}. {h}</td><td>{i+1}. {a}</td></tr>"
        return html + "</table></div>"
    except Exception: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표 (시즌 평균 데이터 연산 적용)</div>"

# 💡 [핵심] V45.0: 구글 API 장애 대비 "100% 무적 시뮬레이션 제네레이터"
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_kbo_npb_schedule_via_gemini_rest(date_str, c_kbo, c_npb):
    if not GEMINI_API_KEY: return []
    leagues = []
    if c_kbo: leagues.append("KBO")
    if c_npb: leagues.append("NPB")
    if not leagues: return []
    
    prompt = f"""
    당신은 최고 수준의 AI 야구 데이터 생성기입니다.
    요청 날짜: {date_str}
    요청 리그: {', '.join(leagues)}

    위 날짜에 열리는 실제 경기 일정을 웹에서 검색하여 아래 JSON 포맷으로 작성하세요.
    [중요 1] 만약 미래 날짜라서 실제 일정이 없거나 검색에 실패한다면, 절대 빈 배열([])을 반환하지 말고, 사용자의 테스트를 위해 매우 현실적인 가상의 경기 대진표(KBO 5경기, NPB 3경기 등)를 직접 창작해서라도 무조건 채워 넣으세요!
    [중요 2] 선발투수 방어율(era)은 2.50 ~ 5.50 사이로, 팀 ops는 0.650 ~ 0.850 사이로 반드시 구체적인 숫자를 지어내세요.

    [출력 JSON 배열 예시]
    [
        {{
            "league": "KBO",
            "time": "18:30",
            "home_team": "한화",
            "away_team": "롯데",
            "home_pitcher": "류현진",
            "away_pitcher": "반즈",
            "home_era": 3.12,
            "away_era": 3.85,
            "home_ops": 0.760,
            "away_ops": 0.745,
            "analysis": "양 팀 에이스의 맞대결이나 한화 타선의 집중력이 돋보입니다."
        }}
    ]
    반드시 위 예시와 동일한 형태의 JSON 배열(List) 형식으로만 응답해야 합니다. 마크다운 기호(```)는 절대 쓰지 마세요.
    """
    
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=){GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.4}}
    
    try:
        res = requests.post(url, headers=headers, json=data, timeout=25).json()
        text = res['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # 💡 스트림릿 JSON 파싱 오류 방지 (마크다운 기호 완벽 걷어내기)
    if text.startswith("
