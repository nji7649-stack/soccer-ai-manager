import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import random

st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

# 🎨 UI CSS
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

.stApp { background-color: #0e1117; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 12px;
    border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 25px;
    display: flex; flex-direction: column; justify-content: space-between; height: 100%;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; letter-spacing: 1px; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 8px; line-height: 1.3; }
.referee-txt { font-size: 11px; color: #888; text-align: center; margin-bottom: 15px; }
.stat-bg { background-color: #262730; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 13.5px; line-height: 1.7; text-align: center; margin-bottom: 10px; border: 1px solid #444;}
.predict-txt { font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; line-height: 1.6; }

.ai-advice { font-size: 11.5px; color: #aaa; font-weight: normal; margin-top: 5px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; white-space: normal; }
.over-under { font-size: 13px; color: #ddd; font-weight: normal; margin-top: 4px; }

.prob-container { display: flex; width: 100%; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 5px; margin-bottom: 15px; background-color: #333; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }
.prob-text { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 3px; }

.table-wrapper { overflow-x: auto; margin-top: 10px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 12px; color: #ccc; text-align: center; }
.detail-table th { background-color: #111; padding: 8px; border-bottom: 2px solid #555; color: #fff; white-space: nowrap; }
.detail-table td { padding: 6px 8px; border-bottom: 1px solid #2a2a2a; white-space: nowrap; }
.injury-tag { color: #ff5252; font-size: 11px; background: #331111; padding: 2px 6px; border-radius: 4px; display: inline-block; margin: 2px; }

/* 사이드바 원형 다크 아이콘 탭 */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex !important; flex-direction: row !important; justify-content: space-between !important;
    gap: 5px !important; width: 100% !important; margin-bottom: 10px;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    flex: 1 !important; display: flex !important; flex-direction: column !important; align-items: center !important;
    justify-content: center !important; background: transparent !important; border: none !important;
    padding: 5px 0 !important; cursor: pointer !important; margin: 0 !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label::before {
    font-family: "Font Awesome 6 Free"; font-weight: 900; font-size: 22px; color: #ffffff; background-color: #151515;
    width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    margin-bottom: 8px; transition: all 0.3s ease; border: 2px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.5);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1)::before { content: "\\f1e3"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2)::before { content: "\\f433"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3)::before { content: "\\f434"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4)::before { content: "\\f45f"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before { border-color: #666; transform: translateY(-2px); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before {
    border-color: #00E676 !important; color: #00E676 !important; background-color: #151515 !important;
    box-shadow: 0 0 15px rgba(0, 230, 118, 0.4) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 13px !important; font-weight: 700 !important; color: #888 !important; margin: 0 !important; text-align: center !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #00E676 !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

FOOTBALL_API_KEY = st.secrets["FOOTBALL_API_KEY"] if "FOOTBALL_API_KEY" in st.secrets else ""
HEADERS = {'x-apisports-key': FOOTBALL_API_KEY}

# ==========================================
# ⚙️ 공통 함수
# ==========================================
@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or str(text).strip() in ['', 'N/A']: return '데이터 분석 중'
    try: 
        safe_txt = str(text).replace('<', '').replace('>', '')
        return GoogleTranslator(source='en', target='ko').translate(safe_txt)
    except: return str(text)

def safe_num(value):
    if not value or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except: return 0.0

# ==========================================
# ⚽ 축구 전용 레이더 및 표 생성 함수
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
    
    html = f"""
    <div class='table-wrapper'>
        <table class='detail-table'>
            <tr><th style='color:#4FC3F7; width:40%;'>{home_kr}</th><th style='width:20%; color:#aaa;'>비교 지표</th><th style='color:#EF5350; width:40%;'>{away_kr}</th></tr>
            <tr><td><b>{h_rank}</b>위</td><td style='font-size:11px;'>리그 순위</td><td><b>{a_rank}</b>위</td></tr>
            <tr><td>{h_goals}골</td><td style='font-size:11px;'>평균 득점</td><td>{a_goals}골</td></tr>
            <tr><td>{h_goals_against}골</td><td style='font-size:11px;'>평균 실점</td><td>{a_goals_against}골</td></tr>
            <tr><td style='white-space:normal;'>{h_inj_html}</td><td style='font-size:11px;'>결장/부상</td><td style='white-space:normal;'>{a_inj_html}</td></tr>
        </table>
    </div>
    """
    return html

def get_lineup_table(home_kr, away_kr, lineup_data):
    if not lineup_data or len(lineup_data) < 2: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표</div>"
    h_p = [p['player']['name'].split()[-1] for p in lineup_data[0].get('startXI', [])]
    a_p = [p['player']['name'].split()[-1] for p in lineup_data[1].get('startXI', [])]
    m_len = max(len(h_p), len(a_p))
    h_p += [""] * (m_len - len(h_p)); a_p += [""] * (m_len - len(a_p))
    html = "<div class='table-wrapper'><table class='detail-table'>"
    html += f"<tr><th style='color:#4FC3F7;'>{home_kr} (선발)</th><th style='color:#EF5350;'>{away_kr} (선발)</th></tr>"
    for h, a in zip(h_p, a_p): html += f"<tr><td>{h}</td><td>{a}</td></tr>"
    html += "</table></div>"
    return html

def create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom=False):
    labels = ['공격력', '수비력', '최근폼', '상대전적', '득점력', '종합전력']
    size = 220; center = size / 2; max_val = 100
    def get_poly(vals, bc, fc):
        pts = []
        for i, val in enumerate(vals):
            ang = (math.pi * 2 / 6) * i - (math.pi / 2)
            r = (val / max_val) * (size * 0.35)
            pts.append(f"{center + r * math.cos(ang)},{center + r * math.sin(ang)}")
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
        r = (size * 0.35) * ratio
        pts = [f"{center + r * math.cos((math.pi*2/6)*i - math.pi/2)},{center + r * math.sin((math.pi*2/6)*i - math.pi/2)}" for i in range(6)]
        svg += f"<polygon points='{' '.join(pts)}' style='fill:none; stroke:#333; stroke-width:1;' />"
    h_poly = get_poly(h_vals, "#4FC3F7", "rgba(79, 195, 247, 0.3)") 
    a_poly = get_poly(a_vals, "#EF5350", "rgba(239, 83, 80, 0.3)") 
    badge = "<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ 자체 데이터 연산</div>" if is_custom else ""
    return f"<div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:10px;'>{badge}<div style='font-size:11px; color:#fff; margin-bottom:10px; font-weight:bold; text-align:center;'><span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}</div><svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>{svg}{h_poly}{a_poly}</svg></div>"

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
        hitter_url = "https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&gameType=R&season=2026&playerPool=ALL&limit=1500"
        h_splits = requests.get(hitter_url).json()['stats'][0]['splits']
        hitter_list = [{'이름': r['player']['fullName'], '팀': r['team']['name'], '타수': r['stat'].get('atBats', 0), 'OPS': r['stat'].get('ops', '.000')} for r in h_splits]
        df_h = pd.DataFrame(hitter_list)
        df_h['OPS'] = pd.to_numeric(df_h['OPS'], errors='coerce').fillna(0.0)
        df_h['타수'] = pd.to_numeric(df_h['타수'], errors='coerce').fillna(0)
        
        pitcher_url = "https://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&gameType=R&season=2026&playerPool=ALL&limit=1500"
        p_splits = requests.get(pitcher_url).json()['stats'][0]['splits']
        pitcher_list = [{'이름': r['player']['fullName'], '팀': r['team']['name'], '출장': r['stat'].get('gamesPlayed', 0), '선발': r['stat'].get('gamesStarted', 0), '이닝': r['stat'].get('inningsPitched', '0.0'), '피홈런': r['stat'].get('homeRuns', 0), '볼넷': r['stat'].get('baseOnBalls', 0), '탈삼진': r['stat'].get('strikeOuts', 0)} for r in p_splits]
        df_p = pd.DataFrame(pitcher_list)
        df_p['이닝_num'] = pd.to_numeric(df_p['이닝'], errors='coerce').fillna(0.0)
        df_p['평균이닝'] = df_p.apply(lambda x: x['이닝_num'] / x['선발'] if x['선발'] > 0 else 4.0, axis=1).clip(3.0, 7.5)
        df_p['FIP'] = df_p.apply(lambda x: ((13*x['피홈런'] + 3*x['볼넷'] - 2*x['탈삼진']) / x['이닝_num']) + 3.10 if x['이닝_num'] > 0 else 4.50, axis=1)
        
        df_bullpen = df_p[(df_p['출장'] > df_p['선발']) & (df_p['이닝_num'] >= 5.0)]
        team_bullpen_fip = df_bullpen.groupby('팀')['FIP'].mean().to_dict()
        return df_h, df_p, team_bullpen_fip
    except: return pd.DataFrame(), pd.DataFrame(), {}

@st.cache_data(ttl=3600)
def load_mlb_team_momentum():
    url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104"
    try:
        res = requests.get(url, timeout=5).json()
        l10_dict = {}
        for record in res.get('records', []):
            for team in record.get('teamRecords', []):
                name = team['team']['name']
                splits = team.get('records', {}).get('splitRecords', [])
                l10_win_rate = 0.5
                for split in splits:
                    if split['type'] == 'lastTen':
                        if (split['wins'] + split['losses']) > 0: l10_win_rate = split['wins'] / (split['wins'] + split['losses'])
                        break
                l10_dict[name] = l10_win_rate
        return l10_dict
    except: return {}

def load_mlb_live_lineup(game_pk):
    try:
        url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
        res = requests.get(url).json()
        home_order = res['teams']['home'].get('battingOrder', [])
        away_order = res['teams']['away'].get('battingOrder', [])
        h_players = res['teams']['home']['players']
        a_players = res['teams']['away']['players']
        h_lookup = {p['person']['id']: p['person']['fullName'] for k, p in h_players.items() if 'person' in p}
        a_lookup = {p['person']['id']: p['person']['fullName'] for k, p in a_players.items() if 'person' in p}
        return [h_lookup.get(pid, 'Unknown') for pid in home_order], [a_lookup.get(pid, 'Unknown') for pid in away_order]
    except: return [], []

def run_mlb_simulation(h_fip, a_fip, h_avg_ip, a_avg_ip, h_ops, a_ops, h_bp_fip, a_bp_fip, h_momentum, a_momentum, park_factor, num_sims=5000):
    h_starter_weight = h_avg_ip / 9.0
    a_starter_weight = a_avg_ip / 9.0
    h_eff_fip = (h_fip * h_starter_weight) + (h_bp_fip * (1 - h_starter_weight))
    a_eff_fip = (a_fip * a_starter_weight) + (a_bp_fip * (1 - a_starter_weight))
    h_attack = (h_ops / 0.720) * h_momentum if h_ops > 0 else 1.0 * h_momentum
    a_attack = (a_ops / 0.720) * a_momentum if a_ops > 0 else 1.0 * a_momentum
    h_expected_runs = ((a_eff_fip * h_attack) + 0.2) * park_factor
    a_expected_runs = (h_eff_fip * a_attack) * park_factor
    
    h_wins, a_wins = 0, 0
    h_tie_win_prob = h_expected_runs / (h_expected_runs + a_expected_runs) if (h_expected_runs + a_expected_runs) > 0 else 0.5
    for _ in range(num_sims):
        h_score = max(0, int(random.gauss(h_expected_runs, 2.3)))
        a_score = max(0, int(random.gauss(a_expected_runs, 2.3)))
        if h_score == a_score:
            if random.random() < h_tie_win_prob: h_score += 1
            else: a_score += 1
        if h_score > a_score: h_wins += 1
        elif a_score > h_score: a_wins += 1
    return (h_wins / num_sims) * 100, (a_wins / num_sims) * 100, h_expected_runs, a_expected_runs

def get_baseball_detailed_html(home_team, away_team, h_p, a_p, h_s_fip, a_s_fip, h_bp_fip, a_bp_fip, h_ops, a_ops, h_ip, a_ip):
    return f"""
    <div class='table-wrapper'>
        <table class='detail-table'>
            <tr><th style='color:#4FC3F7; width:40%;'>{home_team}</th><th style='width:20%; color:#aaa;'>투타 지표</th><th style='color:#EF5350; width:40%;'>{away_team}</th></tr>
            <tr><td><b>{h_p}</b> <span style='font-size:11px; color:#888;'>({h_ip:.1f}이닝)</span></td><td style='font-size:11px;'>선발 투수</td><td><b>{a_p}</b> <span style='font-size:11px; color:#888;'>({a_ip:.1f}이닝)</span></td></tr>
            <tr><td>{h_s_fip:.2f}</td><td style='font-size:11px;'>선발 FIP</td><td>{a_s_fip:.2f}</td></tr>
            <tr><td>{h_bp_fip:.2f}</td><td style='font-size:11px;'>불펜 FIP</td><td>{a_bp_fip:.2f}</td></tr>
            <tr><td>{h_ops:.3f}</td><td style='font-size:11px;'>타선 OPS</td><td>{a_ops:.3f}</td></tr>
        </table>
    </div>
    """

def get_baseball_lineup_html(home_team, away_team, h_lineup, a_lineup):
    if not h_lineup or not a_lineup: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표 (Team Average 연산 적용)</div>"
    m_len = max(len(h_lineup), len(a_lineup))
    h_lineup += [""] * (m_len - len(h_lineup)); a_lineup += [""] * (m_len - len(a_lineup))
    html = "<div class='table-wrapper'><table class='detail-table'>"
    html += f"<tr><th style='color:#4FC3F7;'>{home_team} (타순)</th><th style='color:#EF5350;'>{away_team} (타순)</th></tr>"
    for i, (h, a) in enumerate(zip(h_lineup, a_lineup)): html += f"<tr><td>{i+1}. {h}</td><td>{i+1}. {a}</td></tr>"
    html += "</table></div>"
    return html

# ==========================================
# 📺 메인 UI 렌더링
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 AI 종합 스포츠 분석실 PRO MAX (V27.1)</h1>", unsafe_allow_html=True)

st.sidebar.markdown("### 🏆 스포츠 종목 선택")
selected_sport = st.sidebar.radio("종목 선택", ["축구", "야구", "농구", "배구"], horizontal=True, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 검색 날짜 설정")
selected_date = st.sidebar.date_input("날짜를 선택하세요", datetime.today(), label_visibility="collapsed")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# 💡 세션 상태 초기화 (탭 간섭 방지)
if 'analyzed_data_list' not in st.session_state: st.session_state['analyzed_data_list'] = []

# ==========================================
# ⚽ 축구 로직 (완전 복구)
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

    with st.sidebar.expander("🌏 아시아 및 기타", expanded=True):
        l_292 = st.checkbox("K리그1 (KOR 1부)", value=False)
        l_293 = st.checkbox("K리그2 (KOR 2부)", value=False)
        l_98 = st.checkbox("J1리그 (JPN)", value=False)

    selected_leagues = []
    if l_2: selected_leagues.append("2"); 
    if l_3: selected_leagues.append("3")
    if l_1: selected_leagues.append("1"); 
    if l_10: selected_leagues.append("10")
    if l_39: selected_leagues.append("39"); 
    if l_140: selected_leagues.append("140")
    if l_135: selected_leagues.append("135"); 
    if l_78: selected_leagues.append("78")
    if l_61: selected_leagues.append("61"); 
    if l_88: selected_leagues.append("88")
    if l_119: selected_leagues.append("119"); 
    if l_292: selected_leagues.append("292")
    if l_293: selected_leagues.append("293"); 
    if l_98: selected_leagues.append("98")

    LEAGUE_MAP = {"2":"챔피언스리그", "3":"유로파리그", "1":"월드컵", "10":"A매치", "39":"프리미어리그", "140":"라리가", "135":"세리에A", "78":"분데스리가", "61":"리그1", "88":"에레디비시", "119":"스코티시", "292":"K리그1", "293":"K리그2", "98":"J1리그"}
    AUTUMN_TO_SPRING_LEAGUES = ["2", "3", "39", "140", "135", "78", "61", "88", "119"]

    if analyze_button:
        if not selected_leagues: st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요."); st.stop()
        progress_bar = st.progress(0); status_text = st.empty()
        total_leagues = len(selected_leagues); new_data_list = []
        
        for idx, league_id in enumerate(selected_leagues):
            status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 정밀 데이터 스캔 중... ({idx+1}/{total_leagues})")
            progress_bar.progress((idx) / total_leagues)
            calc_season_year = str(selected_date.year - 1) if league_id in AUTUMN_TO_SPRING_LEAGUES and selected_date.month < 7 else str(selected_date.year)
            querystring = {"league": league_id, "season": calc_season_year, "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
            
            try:
                res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params=querystring, timeout=10).json()
                fixtures = res.get('response', [])
                for match in fixtures:
                    fix_id = str(match['fixture']['id'])
                    home_id = match['teams']['home']['id']; away_id = match['teams']['away']['id']
                    home_kr = translate_to_ko(match['teams']['home']['name']); away_kr = translate_to_ko(match['teams']['away']['name'])
                    referee = str(match['fixture']['referee']).split(',')[0] if match['fixture']['referee'] else "배정 전"
                    venue = match['fixture']['venue']['name'] or "미정"
                    
                    status_short = match['fixture']['status']['short']
                    is_finished = status_short in ['FT', 'AET', 'PEN']
                    is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P']
                    elapsed_time = match['fixture']['status'].get('elapsed', '')
                    try: match_time = datetime.strptime(match['fixture']['date'][:16], "%Y-%m-%dT%H:%M").strftime("%H:%M")
                    except: match_time = "시간미정"
                    
                    if is_live and elapsed_time: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#ff5252; font-size:12px;'>[진행중: {elapsed_time}분]</span>"
                    elif is_finished: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#aaa; font-size:12px;'>[경기 종료]</span>"
                    else: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time})"
                    
                    h_goal = match['goals']['home'] if match['goals']['home'] is not None else 0
                    a_goal = match['goals']['away'] if match['goals']['away'] is not None else 0
                    
                    if is_finished: match_display = f"{home_kr} <span style='color:#00E676; margin:0 10px; font-size:24px;'>{h_goal} : {a_goal}</span> {away_kr}"
                    elif is_live: match_display = f"{home_kr} <span style='color:#ff5252; margin:0 10px; font-size:24px;'>{h_goal} : {a_goal}</span> {away_kr}"
                    else: match_display = f"{home_kr} <span style='color:#888; font-size:16px; margin:0 10px;'>VS</span> {away_kr}"

                    pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    odds_res = requests.get("https://v3.football.api-sports.io/odds", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    injuries_res = requests.get("https://v3.football.api-sports.io/injuries", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    
                    h_inj = [translate_to_ko(inj['player']['name']) for inj in injuries_res if inj['team']['id'] == home_id]
                    a_inj = [translate_to_ko(inj['player']['name']) for inj in injuries_res if inj['team']['id'] == away_id]

                    if not pred_res: continue
                    pred_data = pred_res[0]; comparison = pred_data.get('comparison', {})
                    h_rank = pred_data.get('teams',{}).get('home',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                    a_rank = pred_data.get('teams',{}).get('away',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                    h_goals_avg = pred_data.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                    a_goals_avg = pred_data.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                    h_goals_against_avg = pred_data.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')
                    a_goals_against_avg = pred_data.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')

                    win_prob = pred_data.get('predictions', {}).get('percent', {})
                    p_h = win_prob.get('home', '33%').replace('%','')
                    p_d = win_prob.get('draw', '33%').replace('%','')
                    p_a = win_prob.get('away', '33%').replace('%','')

                    h_vals = [safe_num(comparison.get('att', {}).get('home')), safe_num(comparison.get('def', {}).get('home')), safe_num(comparison.get('form', {}).get('home')), safe_num(comparison.get('h2h', {}).get('home')), safe_num(comparison.get('goals', {}).get('home')), safe_num(comparison.get('total', {}).get('home'))]
                    a_vals = [safe_num(comparison.get('att', {}).get('away')), safe_num(comparison.get('def', {}).get('away')), safe_num(comparison.get('form', {}).get('away')), safe_num(comparison.get('h2h', {}).get('away')), safe_num(comparison.get('goals', {}).get('away')), safe_num(comparison.get('total', {}).get('away'))]
                    
                    is_custom = False
                    if sum(h_vals) < 10 or sum(a_vals) < 10:
                        c_h_form, c_h_att, c_h_def = fetch_custom_team_stats(home_id, calc_season_year)
                        c_a_form, c_a_att, c_a_def = fetch_custom_team_stats(away_id, calc_season_year)
                        c_h_total = (c_h_att + c_h_def + c_h_form) / 3; c_a_total = (c_a_att + c_a_def + c_a_form) / 3
                        h_vals = [c_h_att, c_h_def, c_h_form, 50, c_h_att, c_h_total]
                        a_vals = [c_a_att, c_a_def, c_a_form, 50, c_a_att, c_a_total]
                        is_custom = True

                    radar_html = create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom)
                    lineup_html = get_lineup_table(home_kr, away_kr, lineup_data)
                    detail_html = get_football_detailed_html(home_kr, away_kr, h_rank, a_rank, h_goals_avg, a_goals_avg, h_goals_against_avg, a_goals_against_avg, h_inj, a_inj)

                    odds_h, odds_d, odds_a = 0.0, 0.0, 0.0
                    if odds_res:
                        for bet in odds_res[0].get('bookmakers', [])[0].get('bets', []):
                            if bet['name'] == 'Match Winner':
                                for val in bet['values']:
                                    if str(val['value']) == 'Home': odds_h = float(val['odd'])
                                    elif str(val['value']) == 'Draw': odds_d = float(val['odd'])
                                    elif str(val['value']) == 'Away': odds_a = float(val['odd'])
                                break
                    
                    h_power = (h_vals[0] + h_vals[2] + h_vals[3]) - (len(h_inj) * 3)
                    a_power = (a_vals[0] + a_vals[2] + a_vals[3]) - (len(a_inj) * 3)

                    if h_power > a_power + 15: pred_winner, win_pick, pick_color = "home", f"🟢 {home_kr} 전력 우세", "#00E676"
                    elif a_power > h_power + 15: pred_winner, win_pick, pick_color = "away", f"🔵 {away_kr} 전력 우세", "#4FC3F7"
                    else: pred_winner, win_pick, pick_color = "draw", "🟡 팽팽한 무승부", "#ff9800"

                    if is_finished:
                        actual = "home" if h_goal > a_goal else ("away" if a_goal > h_goal else "draw")
                        win_pick += " (결과 확인)"

                    odds_text = f"<b style='color:#ff9800;'>{odds_h}</b> | 무 <b>{odds_d}</b> | 원정 <b style='color:#ff9800;'>{odds_a}</b>" if odds_h > 0 else "해외 배당 미발매"
                    stat_box = f"<span style='color:#aaa;'>해외 배당:</span> 홈 {odds_text}<br><span style='color:#aaa;'>최종 산출 파워:</span> {home_kr} <b>{int(h_power)}점</b> vs <b>{int(a_power)}점</b> {away_kr}"
                    advice = translate_to_ko(pred_data['predictions'].get('advice', '데이터 분석 완료'))
                    
                    under_over_val = pred_data['predictions'].get('under_over', '')
                    if under_over_val: over_under = f"🔥 예상 기준점: {under_over_val.replace('-', '').replace('+', '')} {'언더' if '-' in under_over_val else '오버'}"
                    else: over_under = "🔥 2.5 기준 오버 (자체예측)" if (h_vals[4] + a_vals[4]) >= 120 else "❄️ 2.5 기준 언더 (자체예측)"

                    new_data_list.append({"sport": "축구", "league": top_league_display, "match_display": match_display, "stat_box": stat_box, "referee": referee, "venue": venue, "p_h": p_h, "p_d": p_d, "p_a": p_a, "win_pick": win_pick, "pick_color": pick_color, "control_pick": advice, "over_under": over_under, "radar_html": radar_html, "lineup_html": lineup_html, "detail_html": detail_html})
            except: pass
        progress_bar.progress(1.0); status_text.text("✅ 축구 데이터 스캔 완료!"); time.sleep(1); status_text.empty(); progress_bar.empty()
        st.session_state['analyzed_data_list'] = new_data_list

# ==========================================
# ⚾ 야구(MLB) 로직
# ==========================================
elif selected_sport == "야구":
    analyze_button = st.sidebar.button("🚀 MLB 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚾ 야구 리그 선택")
    with st.sidebar.expander("미국 야구", expanded=True): st.checkbox("메이저리그 (MLB)", value=True, disabled=True)
    with st.sidebar.expander("아시아 야구 (준비중)", expanded=False): st.checkbox("한국 프로야구 (KBO)", value=False, disabled=True)

    if analyze_button:
        progress_bar = st.progress(0); status_text = st.empty()
        status_text.text(f"🔍 MLB 실시간 스탯 불러오는 중... (1/2)")
        df_h, df_p, team_bp_fip = load_mlb_all_data()
        momentum_dict = load_mlb_team_momentum()
        progress_bar.progress(0.5)
        
        us_date = selected_date - timedelta(days=1)
        schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={us_date.strftime('%Y-%m-%d')}&hydrate=probablePitcher"
        
        try:
            res = requests.get(schedule_url, timeout=5).json()
            games_data = res.get('dates', [{}])[0].get('games', []) if res.get('dates') else []
            new_data_list = []
            
            for idx, game in enumerate(games_data):
                status_text.text(f"🔍 MLB 매치업 엔진 가동 중... ({idx+1}/{len(games_data)})")
                progress_bar.progress(0.5 + (0.5 * (idx / len(games_data))))
                
                game_pk = game.get('gamePk')
                away_team = game['teams']['away']['team']['name']; home_team = game['teams']['home']['team']['name']
                away_pitcher = game['teams']['away'].get('probablePitcher', {}).get('fullName', 'TBD'); home_pitcher = game['teams']['home'].get('probablePitcher', {}).get('fullName', 'TBD')
                venue = game.get('venue', {}).get('name', '미정')
                
                status_code = game['status']['abstractGameState']
                h_score = game['teams']['home'].get('score', 0); a_score = game['teams']['away'].get('score', 0)
                try: match_time = (datetime.strptime(game.get('gameDate'), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=9)).strftime("%H:%M")
                except: match_time = "시간미정"
                
                if status_code == 'Final': 
                    top_league_display = f"MLB ({match_time}) <br><span style='color:#aaa; font-size:12px;'>[경기 종료]</span>"
                    match_display = f"{home_team} <span style='color:#00E676; margin:0 10px; font-size:24px;'>{h_score} : {a_score}</span> {away_team}"
                elif status_code == 'Live': 
                    top_league_display = f"MLB ({match_time}) <br><span style='color:#ff5252; font-size:12px;'>[진행중]</span>"
                    match_display = f"{home_team} <span style='color:#ff5252; margin:0 10px; font-size:24px;'>{h_score} : {a_score}</span> {away_team}"
                else: 
                    top_league_display = f"MLB ({match_time})"
                    match_display = f"{home_team} <span style='color:#888; font-size:16px; margin:0 10px;'>VS</span> {away_team}"

                h_p_data = df_p[df_p['이름'] == home_pitcher]
                a_p_data = df_p[df_p['이름'] == away_pitcher]
                h_s_fip = h_p_data['FIP'].values[0] if not h_p_data.empty else 4.50
                a_s_fip = a_p_data['FIP'].values[0] if not a_p_data.empty else 4.50
                h_s_ip = h_p_data['평균이닝'].values[0] if not h_p_data.empty else 5.0
                a_s_ip = a_p_data['평균이닝'].values[0] if not a_p_data.empty else 5.0
                h_bp_fip = team_bp_fip.get(home_team, 4.00)
                a_bp_fip = team_bp_fip.get(away_team, 4.00)
                h_ops = df_h[(df_h['팀'] == home_team) & (df_h['타수'] > 50)]['OPS'].mean() or 0.720
                a_ops = df_h[(df_h['팀'] == away_team) & (df_h['타수'] > 50)]['OPS'].mean() or 0.720
                h_momentum = 1.0 + (momentum_dict.get(home_team, 0.5) - 0.5) * 0.1
                a_momentum = 1.0 + (momentum_dict.get(away_team, 0.5) - 0.5) * 0.1
                pf = MLB_PARK_FACTORS.get(home_team, 1.00)

                h_lineup, a_lineup = load_mlb_live_lineup(game_pk)

                h_win_prob, a_win_prob, h_exp_runs, a_exp_runs = run_mlb_simulation(
                    h_s_fip, a_s_fip, h_s_ip, a_s_ip, h_ops, a_ops, h_bp_fip, a_bp_fip, h_momentum, a_momentum, pf
                )
                
                odds_h = max(1.10, min(round(0.94 / (h_win_prob/100), 2), 6.00)) if h_win_prob > 0 else 0
                odds_a = max(1.10, min(round(0.94 / (a_win_prob/100), 2), 6.00)) if a_win_prob > 0 else 0
                
                if h_win_prob > a_win_prob + 10: win_pick = f"🟢 {home_team} 승리 유력"; pick_color = "#00E676"
                elif a_win_prob > h_win_prob + 10: win_pick = f"🔵 {away_team} 승리 유력"; pick_color = "#4FC3F7"
                else: win_pick = "🟡 팽팽한 투수/타격전 (접전)"; pick_color = "#ff9800"
                
                if status_code == 'Final': win_pick += " (결과 확인)"

                stat_box = f"<span style='color:#aaa;'>AI 산출 배당:</span> 홈 <b style='color:#ff9800;'>{odds_h:.2f}</b> | 원정 <b style='color:#ff9800;'>{odds_a:.2f}</b><br><span style='color:#aaa;'>기대 득점:</span> {home_team} <b>{h_exp_runs:.1f}점</b> vs <b>{a_exp_runs:.1f}점</b> {away_team}"
                
                # 💡 핵심: 언더/오버 텍스트 강화 (기준점은 8.5로 가정)
                total_exp_runs = h_exp_runs + a_exp_runs
                if total_exp_runs > 9.0: over_under = f"🔥 예상 총 득점: {total_exp_runs:.1f}점 (기준점 8.5 대비 <b>오버 확률 높음</b>)"
                elif total_exp_runs < 8.0: over_under = f"❄️ 예상 총 득점: {total_exp_runs:.1f}점 (기준점 8.5 대비 <b>언더 확률 높음</b>)"
                else: over_under = f"⚠️ 예상 총 득점: {total_exp_runs:.1f}점 (기준점 8.5 근접 접전)"
                
                advice = "양 팀 선발투수의 FIP와 팀 전체 타선의 가상 OPS를 5,000회 몬테카를로 시뮬레이션 한 결과입니다."

                detail_html = get_baseball_detailed_html(home_team, away_team, home_pitcher, away_pitcher, h_s_fip, a_s_fip, h_bp_fip, a_bp_fip, h_ops, a_ops, h_s_ip, a_s_ip)
                lineup_html = get_baseball_lineup_html(home_team, away_team, h_lineup, a_lineup)

                new_data_list.append({"sport": "야구", "league": top_league_display, "match_display": match_display, "stat_box": stat_box, "referee": "TBD", "venue": venue, "p_h": f"{h_win_prob:.1f}", "p_d": "0", "p_a": f"{a_win_prob:.1f}", "win_pick": win_pick, "pick_color": pick_color, "control_pick": advice, "over_under": over_under, "lineup_html": lineup_html, "detail_html": detail_html})
            progress_bar.progress(1.0); status_text.text("✅ MLB 궁극의 데이터 스캔 완료!"); time.sleep(1); status_text.empty(); progress_bar.empty()
            st.session_state['analyzed_data_list'] = new_data_list
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 🏀 농구 / 🏐 배구
# ==========================================
elif selected_sport == "농구":
    st.sidebar.button("🚀 농구 데이터 딥-스캔 시작", use_container_width=True, disabled=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏀 농구 리그 선택 (준비중)")
elif selected_sport == "배구":
    st.sidebar.button("🚀 배구 데이터 딥-스캔 시작", use_container_width=True, disabled=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏐 배구 리그 선택 (준비중)")

# ==========================================
# 📺 공통 렌더링 엔진
# ==========================================
if st.session_state.get('analyzed_data_list'):
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_data_list']):
        with cols[idx % 3]:
            # 축구와 야구의 확률 바 구분 (야구는 무승부 제거)
            if data['sport'] == "야구":
                prob_bar = f"<div class='prob-text'><span>홈 승 {data['p_h']}%</span><span>원정 승 {data['p_a']}%</span></div><div class='prob-container'><div class='prob-home' style='width: {data['p_h']}%;'></div><div class='prob-away' style='width: {data['p_a']}%;'></div></div>"
            else:
                prob_bar = f"<div class='prob-text'><span>승 {data['p_h']}%</span><span>무 {data['p_d']}%</span><span>패 {data['p_a']}%</span></div><div class='prob-container'><div class='prob-home' style='width: {data['p_h']}%;'></div><div class='prob-draw' style='width: {data['p_d']}%;'></div><div class='prob-away' style='width: {data['p_a']}%;'></div></div>"
            
            html_str = f"<div style='height: 100%;'><div class='card-box'><div><div class='league-txt'>{data['league']}</div><div class='match-txt'>{data['match_display']}</div><div class='referee-txt'>🏟️ {data['venue']}</div>{prob_bar}<div class='stat-bg'>{data['stat_box']}</div></div><div class='predict-txt'><div style='color: {data['pick_color']}; margin-bottom: 3px;'>🎯 {data['win_pick']}</div><div class='over-under'>{data['over_under']}</div><div class='ai-advice'>⚔️ 요약: {data['control_pick']}</div></div></div></div>"
            st.markdown(html_str, unsafe_allow_html=True)
            
            with st.expander("🔍 상세 지표 & 선발 라인업 확인"):
                st.markdown(data['detail_html'], unsafe_allow_html=True)
                if data['sport'] == "축구": st.markdown(data.get('radar_html', ''), unsafe_allow_html=True)
                st.markdown(data['lineup_html'], unsafe_allow_html=True)
            st.write("")
elif st.session_state.get('analyzed_data_list') == []: st.markdown("")
