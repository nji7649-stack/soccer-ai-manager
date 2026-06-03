import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import random
from collections import Counter
import time
import math
from deep_translator import GoogleTranslator

st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

# 🎨 UI CSS: 축구의 '프리미엄 다크 테마'와 폰트어썸 아이콘 탭 완벽 적용
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

/* 확률 바 (Probability Bar) */
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
# ⚙️ 공통 함수 (번역 등)
# ==========================================
@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or str(text).strip() in ['', 'N/A']: return '데이터 분석 중'
    try: 
        safe_txt = str(text).replace('<', '').replace('>', '')
        return GoogleTranslator(source='en', target='ko').translate(safe_txt)
    except:
        return str(text)

def safe_num(value):
    if not value or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except: return 0.0

# ==========================================
# ⚽ 축구 전용 함수 (기존 유지)
# ==========================================
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

# ==========================================
# ⚾ 야구(MLB) 전용 함수 및 설정 (감독님 제공 로직)
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

POSITION_TRANSLATIONS = {'P': '투수', 'C': '포수', '1B': '1루수', '2B': '2루수', '3B': '3루수', 'SS': '유격수', 'LF': '좌익수', 'CF': '중견수', 'RF': '우익수', 'DH': '지명타자', 'B': '야수'}

@st.cache_data(ttl=3600)
def load_mlb_all_data():
    try:
        hitter_url = "https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&gameType=R&season=2026&playerPool=ALL&limit=1500"
        h_splits = requests.get(hitter_url).json()['stats'][0]['splits']
        hitter_list = [{
            '이름': r['player']['fullName'], '팀': r['team']['name'], 
            '타수': r['stat'].get('atBats', 0), '타율': r['stat'].get('avg', '.000'), 'OPS': r['stat'].get('ops', '.000')
        } for r in h_splits]
        df_h = pd.DataFrame(hitter_list)
        df_h['OPS'] = pd.to_numeric(df_h['OPS'], errors='coerce').fillna(0.0)
        df_h['타수'] = pd.to_numeric(df_h['타수'], errors='coerce').fillna(0)
        
        pitcher_url = "https://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&gameType=R&season=2026&playerPool=ALL&limit=1500"
        p_splits = requests.get(pitcher_url).json()['stats'][0]['splits']
        pitcher_list = [{
            '이름': r['player']['fullName'], '팀': r['team']['name'], 
            '출장': r['stat'].get('gamesPlayed', 0), '선발': r['stat'].get('gamesStarted', 0), 
            '이닝': r['stat'].get('inningsPitched', '0.0'), '피홈런': r['stat'].get('homeRuns', 0), 
            '볼넷': r['stat'].get('baseOnBalls', 0), '탈삼진': r['stat'].get('strikeOuts', 0), 'ERA': r['stat'].get('era', '99.99')
        } for r in p_splits]
        df_p = pd.DataFrame(pitcher_list)
        df_p['이닝_num'] = pd.to_numeric(df_p['이닝'], errors='coerce').fillna(0.0)
        df_p['평균이닝'] = df_p.apply(lambda x: x['이닝_num'] / x['선발'] if x['선발'] > 0 else 4.0, axis=1).clip(3.0, 7.5)
        df_p['FIP'] = df_p.apply(lambda x: ((13*x['피홈런'] + 3*x['볼넷'] - 2*x['탈삼진']) / x['이닝_num']) + 3.10 if x['이닝_num'] > 0 else 4.50, axis=1)
        
        df_bullpen = df_p[(df_p['출장'] > df_p['선발']) & (df_p['이닝_num'] >= 5.0)]
        team_bullpen_fip = df_bullpen.groupby('팀')['FIP'].mean().to_dict()
        return df_h, df_p, team_bullpen_fip
    except:
        return pd.DataFrame(), pd.DataFrame(), {}

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
                        if (split['wins'] + split['losses']) > 0:
                            l10_win_rate = split['wins'] / (split['wins'] + split['losses'])
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
        h_pitchers = res['teams']['home'].get('pitchers', [])
        a_pitchers = res['teams']['away'].get('pitchers', [])
        h_starter_hand = res['teams']['home']['players'].get(f"ID_{h_pitchers[0]}", {}).get('person', {}).get('pitchHand', {}).get('code', 'R') if h_pitchers else 'R'
        a_starter_hand = res['teams']['away']['players'].get(f"ID_{a_pitchers[0]}", {}).get('person', {}).get('pitchHand', {}).get('code', 'R') if a_pitchers else 'R'
        
        if len(home_order) == 0 or len(away_order) == 0: return [], [], h_starter_hand, a_starter_hand
        
        h_players = res['teams']['home']['players']
        a_players = res['teams']['away']['players']
        h_lookup = {p['person']['id']: p['person']['fullName'] for k, p in h_players.items() if 'person' in p}
        a_lookup = {p['person']['id']: p['person']['fullName'] for k, p in a_players.items() if 'person' in p}
        
        home_lineup = [h_lookup.get(pid, 'Unknown') for pid in home_order]
        away_lineup = [a_lookup.get(pid, 'Unknown') for pid in away_order]
        return home_lineup, away_lineup, h_starter_hand, a_starter_hand
    except:
        return [], [], 'R', 'R'

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

# 💡 야구 전용 상세 HTML 생성 함수
def get_baseball_detailed_html(home_team, away_team, h_p, a_p, h_s_fip, a_s_fip, h_bp_fip, a_bp_fip, h_ops, a_ops, h_ip, a_ip):
    html = f"""
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
    return html

def get_baseball_lineup_html(home_team, away_team, h_lineup, a_lineup):
    if not h_lineup or not a_lineup: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표 (Team Average 연산 적용)</div>"
    m_len = max(len(h_lineup), len(a_lineup))
    h_lineup += [""] * (m_len - len(h_lineup)); a_lineup += [""] * (m_len - len(a_lineup))
    
    html = "<div class='table-wrapper'><table class='detail-table'>"
    html += f"<tr><th style='color:#4FC3F7;'>{home_team} (타순)</th><th style='color:#EF5350;'>{away_team} (타순)</th></tr>"
    for i, (h, a) in enumerate(zip(h_lineup, a_lineup)): html += f"<tr><td>{i+1}. {h}</td><td>{i+1}. {a}</td></tr>"
    html += "</table></div>"
    return html


# --- 💡 메인 화면 타이틀 ---
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 통합 스포츠 AI 분석실 (V27.0 PRO MAX)</h1>", unsafe_allow_html=True)

# --- 💡 사이드바 ---
st.sidebar.markdown("### 🏆 스포츠 종목 선택")
selected_sport = st.sidebar.radio("종목 선택", ["축구", "야구", "농구", "배구"], horizontal=True, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 검색 날짜 설정")
selected_date = st.sidebar.date_input("날짜를 선택하세요", datetime.today(), label_visibility="collapsed")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ⚽ 축구 로직 (이전 버전 완벽 유지)
# ==========================================
if selected_sport == "축구":
    analyze_button = st.sidebar.button("🚀 축구 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚽ 축구 리그 선택")
    
    with st.sidebar.expander("🌟 국제 대회", expanded=True): l_2 = st.checkbox("챔피언스리그", value=False); l_10 = st.checkbox("A매치", value=True)
    with st.sidebar.expander("🌍 유럽 1부 리그", expanded=True): l_39 = st.checkbox("프리미어리그 (ENG)", value=True); l_140 = st.checkbox("라리가 (ESP)", value=True)
    
    if analyze_button:
        st.warning("⚠️ 튜토리얼 데모 버전입니다. 풀 버전은 기존 코드를 참고하세요.")

# ==========================================
# ⚾ 야구 로직 (MLB 전용 - 축구 UI 완벽 이식)
# ==========================================
elif selected_sport == "야구":
    analyze_button = st.sidebar.button("🚀 MLB 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚾ 야구 리그 선택")
    
    with st.sidebar.expander("미국 야구 (동기화 완료)", expanded=True):
        st.checkbox("메이저리그 (MLB)", value=True, disabled=True)
        
    with st.sidebar.expander("아시아 야구 (준비중)", expanded=False):
        st.checkbox("한국 프로야구 (KBO)", value=False, disabled=True)
        st.checkbox("일본 프로야구 (NPB)", value=False, disabled=True)

    if analyze_button:
        progress_bar = st.progress(0); status_text = st.empty()
        status_text.text(f"🔍 MLB 실시간 데이터 및 스탯 스캔 중... (1/2)")
        
        # 데이터베이스 로딩
        df_h, df_p, team_bp_fip = load_mlb_all_data()
        momentum_dict = load_mlb_team_momentum()
        progress_bar.progress(0.5)
        
        # 오늘 일정 로딩 (미국 시간 맞춰서 변환)
        us_date = selected_date - timedelta(days=1)
        date_str = us_date.strftime("%Y-%m-%d")
        schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}&hydrate=probablePitcher"
        
        try:
            res = requests.get(schedule_url, timeout=5).json()
            games_data = res.get('dates', [{}])[0].get('games', []) if res.get('dates') else []
            new_data_list = []
            
            for idx, game in enumerate(games_data):
                status_text.text(f"🔍 MLB 매치업 엔진 가동 중... ({idx+1}/{len(games_data)})")
                progress_bar.progress(0.5 + (0.5 * (idx / len(games_data))))
                
                game_pk = game.get('gamePk')
                away_team = game['teams']['away']['team']['name']
                home_team = game['teams']['home']['team']['name']
                away_id = game['teams']['away']['team']['id']
                home_id = game['teams']['home']['team']['id']
                away_pitcher = game['teams']['away'].get('probablePitcher', {}).get('fullName', 'TBD')
                home_pitcher = game['teams']['home'].get('probablePitcher', {}).get('fullName', 'TBD')
                venue = game.get('venue', {}).get('name', '미정')
                
                status_code = game['status']['abstractGameState']
                h_score = game['teams']['home'].get('score', 0)
                a_score = game['teams']['away'].get('score', 0)
                
                try: 
                    utc_time = datetime.strptime(game.get('gameDate'), "%Y-%m-%dT%H:%M:%SZ")
                    match_time = (utc_time + timedelta(hours=9)).strftime("%H:%M")
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

                # 💡 감독님의 몬테카를로 엔진(AI 알고리즘) 적용
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

                # 라인업 불러오기
                h_lineup, a_lineup, _, _ = load_mlb_live_lineup(game_pk)

                # 확률 계산 (5000회 시뮬레이션)
                h_win_prob, a_win_prob, h_exp_runs, a_exp_runs = run_mlb_simulation(
                    h_s_fip, a_s_fip, h_s_ip, a_s_ip, h_ops, a_ops, h_bp_fip, a_bp_fip, h_momentum, a_momentum, pf
                )
                
                # 축구 형식의 UI 변수 생성
                odds_h = max(1.10, min(round(0.94 / (h_win_prob/100), 2), 6.00)) if h_win_prob > 0 else 0
                odds_a = max(1.10, min(round(0.94 / (a_win_prob/100), 2), 6.00)) if a_win_prob > 0 else 0
                
                if h_win_prob > a_win_prob + 10: win_pick = f"🟢 {home_team} 승리 유력"; pick_color = "#00E676"
                elif a_win_prob > h_win_prob + 10: win_pick = f"🔵 {away_team} 승리 유력"; pick_color = "#4FC3F7"
                else: win_pick = "🟡 팽팽한 투수/타격전 (접전)"; pick_color = "#ff9800"
                
                if status_code == 'Final':
                    actual = "home" if h_score > a_score else "away"
                    win_pick += " (적중)" if (actual == "home" and h_win_prob > a_win_prob) or (actual == "away" and a_win_prob > h_win_prob) else " (미적중)"

                stat_box = f"<span style='color:#aaa;'>AI 산출 배당:</span> 홈 <b style='color:#ff9800;'>{odds_h:.2f}</b> | 원정 <b style='color:#ff9800;'>{odds_a:.2f}</b><br><span style='color:#aaa;'>기대 득점:</span> {home_team} <b>{h_exp_runs:.1f}점</b> vs <b>{a_exp_runs:.1f}점</b> {away_team}"
                over_under = f"🔥 예상 기준점: {round((h_exp_runs + a_exp_runs) * 2) / 2} 점"
                advice = "양 팀 선발투수의 FIP와 팀 전체 타선의 가상 OPS를 5,000회 몬테카를로 시뮬레이션 한 결과입니다."

                detail_html = get_baseball_detailed_html(home_team, away_team, home_pitcher, away_pitcher, h_s_fip, a_s_fip, h_bp_fip, a_bp_fip, h_ops, a_ops, h_s_ip, a_s_ip)
                lineup_html = get_baseball_lineup_html(home_team, away_team, h_lineup, a_lineup)

                new_data_list.append({
                    "league": top_league_display, "match_display": match_display, "stat_box": stat_box,
                    "referee": f"TBD", "venue": venue, "p_h": f"{h_win_prob:.1f}", "p_d": "0", "p_a": f"{a_win_prob:.1f}",
                    "win_pick": win_pick, "pick_color": pick_color, "control_pick": advice, 
                    "over_under": over_under, "lineup_html": lineup_html, "detail_html": detail_html
                })
            
            progress_bar.progress(1.0); status_text.text("✅ MLB 궁극의 데이터 스캔 완료!"); time.sleep(1); status_text.empty(); progress_bar.empty()
            st.session_state['analyzed_data_list'] = new_data_list
            
        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

    # 💡 렌더링 엔진 (축구의 카드형 디자인 100% 동일 적용)
    if st.session_state.get('analyzed_data_list'):
        cols = st.columns(3)
        for idx, data in enumerate(st.session_state['analyzed_data_list']):
            with cols[idx % 3]:
                # 야구는 무승부가 없으므로 막대를 2등분으로 조정
                prob_bar = f"""
                <div class='prob-text'><span>홈 승 {data['p_h']}%</span><span>원정 승 {data['p_a']}%</span></div>
                <div class='prob-container'>
                    <div class='prob-home' style='width: {data['p_h']}%;'></div>
                    <div class='prob-away' style='width: {data['p_a']}%;'></div>
                </div>
                """
                
                html_str = f"<div style='height: 100%;'><div class='card-box'><div><div class='league-txt'>{data['league']}</div><div class='match-txt'>{data['match_display']}</div><div class='referee-txt'>🏟️ {data['venue']}</div>{prob_bar}<div class='stat-bg'>{data['stat_box']}</div></div><div class='predict-txt'><div style='color: {data['pick_color']}; margin-bottom: 3px;'>🎯 {data['win_pick']}</div><div class='over-under'>{data['over_under']}</div><div class='ai-advice'>⚔️ 요약: {data['control_pick']}</div></div></div></div>"
                st.markdown(html_str, unsafe_allow_html=True)
                
                with st.expander("🔍 투타 상세 지표 & 선발 라인업"):
                    st.markdown(data['detail_html'], unsafe_allow_html=True)
                    st.markdown(data['lineup_html'], unsafe_allow_html=True)
                st.write("")
    elif st.session_state.get('analyzed_data_list') == []: st.markdown("")

# ==========================================
# 🏀 농구 / 🏐 배구 로직 (축구처럼 동일하게 준비중 탭 띄우기)
# ==========================================
elif selected_sport == "농구":
    st.sidebar.button("🚀 농구 데이터 딥-스캔 시작", use_container_width=True, disabled=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏀 농구 리그 선택 (준비중)")
elif selected_sport == "배구":
    st.sidebar.button("🚀 배구 데이터 딥-스캔 시작", use_container_width=True, disabled=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏐 배구 리그 선택 (준비중)")
