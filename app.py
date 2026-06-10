import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import math

# ==========================================
# 1. 페이지 및 API 초기 설정
# ==========================================
st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

FOOTBALL_API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
HEADERS = {'x-apisports-key': FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}

# ==========================================
# 2. 🎨 UI CSS (아이콘 라디오 버튼 원상복구 및 카드 디자인)
# ==========================================
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.stApp { background-color: #0e1117; }

/* 스포츠 종목 선택 아이콘 라디오 버튼 디자인 */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] { display: flex !important; flex-direction: row !important; justify-content: space-between !important; gap: 5px !important; width: 100% !important; margin-bottom: 10px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { flex: 1 !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; background: transparent !important; border: none !important; padding: 5px 0 !important; cursor: pointer !important; margin: 0 !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label::before { font-family: "Font Awesome 6 Free"; font-weight: 900; font-size: 22px; color: #ffffff; background-color: #151515; width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; transition: all 0.3s ease; border: 2px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }

/* 각 종목별 폰트어썸 아이콘 매핑 */
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1)::before { content: "\\f1e3"; } /* 축구 */
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2)::before { content: "\\f433"; } /* 야구 */
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3)::before { content: "\\f434"; } /* 농구 */
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4)::before { content: "\\f45f"; } /* 배구 */

[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before { border-color: #666; transform: translateY(-2px); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before { border-color: #00E676 !important; color: #00E676 !important; background-color: #151515 !important; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4) !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 13px !important; font-weight: 700 !important; color: #888 !important; margin: 0 !important; text-align: center !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #00E676 !important; }

/* 분석 카드 디자인 */
.card-box { background-color: #1e1e1e; padding: 20px; border-radius: 12px; border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 25px; display: flex; flex-direction: column; height: 100%; min-height: 650px; }
.card-box p { margin: 0 !important; padding: 0 !important; line-height: 1.5 !important; }
.card-top { flex-shrink: 0; }
.card-mid { flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-start; margin: 10px 0; }
.card-bot { flex-shrink: 0; border-top: 1px dashed #555; padding-top: 15px; text-align: center; }
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; letter-spacing: 1px; }
.match-box { display: flex; align-items: center; justify-content: center; width: 100%; margin-bottom: 15px; }
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
.stat-bg { background-color: #262730; padding: 12px; border-radius: 8px; color: #eeeeee; font-size: 12px; line-height: 1.5; text-align: center; border: 1px solid #444; width: 100%; margin-bottom:10px; }
.predict-txt { font-size: 14.5px; font-weight: bold; margin-bottom: 5px; }
.handi-txt { font-size: 14.5px; font-weight: bold; margin-bottom: 5px; } 
.over-under { font-size: 14.5px; font-weight: bold; margin-bottom: 8px; } 
.ai-advice { font-size: 11.5px; color: #aaa; font-weight: normal; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; white-space: normal; }
.table-wrapper { width: 100%; margin-top: 5px; margin-bottom: 10px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 11px; color: #ccc; text-align: center; } 
.detail-table th { background-color: #111; padding: 6px 2px; border-bottom: 2px solid #555; color: #fff; white-space: nowrap; }
.detail-table td { padding: 5px 2px; border-bottom: 1px solid #2a2a2a; } 
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. 언어 번역 딕셔너리
# ==========================================
CUSTOM_DICT = {
    "Arsenal": "아스날", "Aston Villa": "애스턴 빌라", "Newcastle": "뉴캐슬", "Crystal Palace": "크리스탈 팰리스",
    "Manchester City": "맨시티", "Manchester United": "맨유", "Liverpool": "리버풀", "Chelsea": "리버풀", "Tottenham": "토트넘",
    "Real Madrid": "레알 마드리드", "Barcelona": "바르셀로나", "Atletico Madrid": "아틀레티코", "Bayern Munich": "바이에른 뮌헨",
    "Paris Saint Germain": "PSG", "Inter": "인터밀란", "Juventus": "유벤투스", "AC Milan": "AC밀란"
}

@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or str(text).strip() in ['', 'N/A']: return '미정'
    for eng, kor in CUSTOM_DICT.items():
        if eng.lower() == str(text).lower() or eng in str(text): return kor
    try: return GoogleTranslator(source='en', target='ko').translate(str(text).replace('<', '').replace('>', ''))
    except Exception: return str(text)

def safe_num(value):
    if not value or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except Exception: return 0.0

# ==========================================
# 4. 육각형 레이더 차트 (축구 전용)
# ==========================================
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
    badge = "<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ 전력 분석망 데이터</div>" if not is_custom else "<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ 자체 최근 전적 환산 데이터</div>"
    return f"<div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:10px; margin-bottom: 10px;'>{badge}<div style='font-size:11px; color:#fff; margin-bottom:10px; font-weight:bold; text-align:center;'><span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}</div><svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>{svg}{h_poly}{a_poly}</svg></div>"

# ==========================================
# 5. 축구 전용 API Fetcher (캐싱 & 429 방어 로직 강화)
# ==========================================
@st.cache_data(ttl=600, show_spinner=False)
def fetch_api_football_fixtures(league_id, season, date_str):
    try: 
        res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"league": league_id, "season": season, "date": date_str, "timezone": "Asia/Seoul"}, timeout=10)
        if res.status_code == 429: return "LIMIT" # 호출 한도 초과
        return res.json().get('response') or []
    except Exception: return []

@st.cache_data(ttl=1200, show_spinner=False)
def fetch_api_football_by_fixture(endpoint, fix_id):
    try: 
        res = requests.get(f"https://v3.football.api-sports.io/{endpoint}", headers=HEADERS, params={"fixture": fix_id}, timeout=10)
        if res.status_code == 429: return "LIMIT"
        return res.json().get('response') or []
    except Exception: return []

# API 데이터가 없거나 에러 날 때 사용하는 보조 승률 계산기 (최근 전적 활용)
def fetch_custom_team_stats(team_id, season_year):
    try:
        res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"team": team_id, "last": 5, "season": season_year}, timeout=5)
        if res.status_code == 429: return 50, 50, 50
        fixtures = res.json().get('response') or []
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

# UI 테이블 렌더러
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


# ==========================================
# 6. 메인 UI (사이드바 및 날짜 설정)
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 축구 전용 AI 분석실 (V1 도장깨기)</h1>", unsafe_allow_html=True)

# 💡 4개 종목 아이콘 라디오 버튼 (현재는 축구만 기능 활성화)
sport_options = ["축구", "야구", "농구", "배구"]
selected_sport = st.sidebar.radio("종목 선택", sport_options, horizontal=True)
st.sidebar.markdown("---")

kst_now = datetime.utcnow() + timedelta(hours=9)
selected_date = st.sidebar.date_input("📅 검색 날짜 설정 (KST 기준)", kst_now.date())
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if 'analyzed_data_list' not in st.session_state: 
    st.session_state['analyzed_data_list'] = []

# ==========================================
# ⚽ 7. 축구 단독 스캔 로직
# ==========================================
if selected_sport == "축구":
    analyze_button = st.sidebar.button("🚀 축구 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚽ 축구 리그 선택")
    
    # 💡 아시아/기타 탭 복구
    with st.sidebar.expander("🌏 아시아 및 기타 리그", expanded=True):
        l_292 = st.checkbox("K리그 1 (KOR)", value=True)
        l_293 = st.checkbox("K리그 2 (KOR)", value=False)
        l_98 = st.checkbox("J1 리그 (JPN)", value=False)
        
    # 💡 월드컵 항목(1번) 복구 완료
    with st.sidebar.expander("🌟 국제 대회 (UEFA/FIFA)", expanded=True):
        l_1 = st.checkbox("월드컵 (World Cup)", value=True)
        l_2 = st.checkbox("챔피언스리그 (UCL)", value=False)
        l_3 = st.checkbox("유로파리그 (UEL)", value=False)
        l_10 = st.checkbox("A매치 친선전", value=False)
        
    with st.sidebar.expander("🌍 유럽 주요 리그", expanded=True):
        l_39 = st.checkbox("프리미어리그 (ENG)", value=False)
        l_140 = st.checkbox("라리가 (ESP)", value=False)
        l_135 = st.checkbox("세리에 A (ITA)", value=False)
        l_78 = st.checkbox("분데스리가 (GER)", value=False)
        l_61 = st.checkbox("리그 1 (FRA)", value=False)
        l_88 = st.checkbox("에레디비시 (NED)", value=False)

    # 선택된 리그 매핑
    league_ids = ["292", "293", "98", "1", "2", "3", "10", "39", "140", "135", "78", "61", "88"]
    checkbox_vals = [l_292, l_293, l_98, l_1, l_2, l_3, l_10, l_39, l_140, l_135, l_78, l_61, l_88]
    selected_leagues = [lid for lid, selected in zip(league_ids, checkbox_vals) if selected]
    
    LEAGUE_MAP = {
        "292":"K리그1", "293":"K리그2", "98":"J1리그", "1":"월드컵", "2":"챔피언스리그", 
        "3":"유로파리그", "10":"A매치", "39":"프리미어리그", "140":"라리가", "135":"세리에A", 
        "78":"분데스리가", "61":"리그1", "88":"에레디비시"
    }
    
    # 💡 춘추제(봄 개막) 리그 목록 (여기에 포함되면 연도 계산 시 -1을 하지 않음)
    SPRING_TO_AUTUMN_LEAGUES = ["292", "293", "98", "1", "10"]

    if analyze_button:
        if not selected_leagues: 
            st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
            st.stop()
            
        st.session_state['analyzed_data_list'] = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_leagues = len(selected_leagues)
        
        limit_hit = False # 429 에러 발생 여부 체크
        
        for idx, league_id in enumerate(selected_leagues):
            if limit_hit: break
            
            status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 데이터 스캔 중... ({idx+1}/{total_leagues})")
            progress_bar.progress((idx) / total_leagues)
            
            # 💡 완벽한 시즌 계산 로직
            if league_id in SPRING_TO_AUTUMN_LEAGUES:
                calc_season_year = str(selected_date.year) # K리그 등은 무조건 검색 연도
            else:
                # 유럽 리그는 7월 이전에 검색하면 작년 시즌 데이터를, 7월 이후면 올해 시즌 데이터를 불러옵니다.
                calc_season_year = str(selected_date.year - 1) if selected_date.month < 7 else str(selected_date.year)
                
            date_str = selected_date.strftime('%Y-%m-%d')
            
            matches = fetch_api_football_fixtures(league_id, calc_season_year, date_str)
            
            if matches == "LIMIT":
                st.error(f"🚨 API 무료 호출 한도 초과! 1분 뒤에 다시 시도해주세요.")
                limit_hit = True
                break
                
            for match in matches:
                try:
                    fix_id = str(match['fixture']['id'])
                    home_id = match['teams']['home']['id']
                    away_id = match['teams']['away']['id']
                    
                    home_kr = translate_to_ko(match['teams']['home']['name'])
                    away_kr = translate_to_ko(match['teams']['away']['name'])
                    home_logo = match['teams']['home']['logo']
                    away_logo = match['teams']['away']['logo']
                    
                    referee = str(match['fixture']['referee']).split(',')[0] if match['fixture']['referee'] else "배정 전"
                    venue = match['fixture']['venue']['name'] or "미정"
                    status_short = match['fixture']['status']['short']
                    
                    # 경기 시간 KST 변환
                    try:
                        utc_time = datetime.utcfromtimestamp(match['fixture']['timestamp'])
                        match_time = (utc_time + timedelta(hours=9)).strftime("%H:%M")
                        is_past_start_time = datetime.utcnow() >= utc_time 
                    except Exception: 
                        match_time = "시간미정"; is_past_start_time = True
                        
                    is_finished = status_short in ['FT', 'AET', 'PEN']
                    is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P'] and is_past_start_time
                    elapsed_time = match['fixture']['status'].get('elapsed', '')
                    
                    if is_live and elapsed_time: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#ff5252; font-size:12px;'>[진행중: {elapsed_time}분]</span>"
                    elif is_finished: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#aaa; font-size:12px;'>[경기 종료]</span>"
                    else: top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time})"
                    
                    h_g = match['goals']['home'] if match['goals']['home'] is not None else 0
                    a_g = match['goals']['away'] if match['goals']['away'] is not None else 0
                    score_color = "#00E676" if is_finished else ("#ff5252" if is_live else "#888")
                    score_text = f"{h_g}:{a_g}" if is_finished or is_live else "VS"

                    match_display = f"<div class='match-box'><div class='team-side home-side'><div class='team-name' title='{home_kr}'>{home_kr}</div><img src='{home_logo}' class='team-logo'></div><div class='score-side' style='color:{score_color};'>{score_text}</div><div class='team-side away-side'><img src='{away_logo}' class='team-logo'><div class='team-name' title='{away_kr}'>{away_kr}</div></div></div>"

                    # 예측 데이터 스캔
                    pred_data = fetch_api_football_by_fixture("predictions", fix_id)
                    if pred_data == "LIMIT": limit_hit = True; break
                    if not pred_data: continue
                    
                    pred = pred_data[0]; comp = pred.get('comparison') or {}
                    
                    # 라인업/부상자/배당률 스캔 (리미트 방어를 위해 딜레이 추가)
                    odds_res = fetch_api_football_by_fixture("odds", fix_id)
                    lineup_data = fetch_api_football_by_fixture("fixtures/lineups", fix_id)
                    inj_res = fetch_api_football_by_fixture("injuries", fix_id)
                    
                    if odds_res == "LIMIT" or lineup_data == "LIMIT" or inj_res == "LIMIT":
                        limit_hit = True; break
                    
                    h_inj = [translate_to_ko(i['player']['name']) for i in inj_res if i.get('team', {}).get('id') == home_id]
                    a_inj = [translate_to_ko(i['player']['name']) for i in inj_res if i.get('team', {}).get('id') == away_id]
                    
                    h_rank = pred.get('teams',{}).get('home',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                    a_rank = pred.get('teams',{}).get('away',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                    h_avg_f = pred.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                    a_avg_f = pred.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                    h_avg_a = pred.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')
                    a_avg_a = pred.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')

                    wp = pred.get('predictions', {}).get('percent') or {}
                    p_h = wp.get('home', '33%').replace('%',''); p_d = wp.get('draw', '33%').replace('%',''); p_a = wp.get('away', '33%').replace('%','')

                    h_vals = [safe_num(comp.get('att', {}).get('home')), safe_num(comp.get('def', {}).get('home')), safe_num(comp.get('form', {}).get('home')), safe_num(comp.get('h2h', {}).get('home')), safe_num(comp.get('goals', {}).get('home')), safe_num(comp.get('total', {}).get('home'))]
                    a_vals = [safe_num(comp.get('att', {}).get('away')), safe_num(comp.get('def', {}).get('away')), safe_num(comp.get('form', {}).get('away')), safe_num(comp.get('h2h', {}).get('away')), safe_num(comp.get('goals', {}).get('away')), safe_num(comp.get('total', {}).get('away'))]
                    
                    is_custom = False
                    if sum(h_vals) < 10 or sum(a_vals) < 10:
                        cf_h, ca_h, cd_h = fetch_custom_team_stats(home_id, calc_season_year); cf_a, ca_a, cd_a = fetch_custom_team_stats(away_id, calc_season_year)
                        h_vals = [ca_h, cd_h, cf_h, 50, ca_h, (ca_h+cd_h+cf_h)/3]; a_vals = [ca_a, cd_a, cf_a, 50, ca_a, (ca_a+cd_a+cf_a)/3]
                        is_custom = True

                    radar_html = create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom)
                    detail_html = get_football_detailed_html(home_kr, away_kr, h_rank, a_rank, h_avg_f, a_avg_f, h_avg_a, a_avg_a, h_inj, a_inj)

                    odds_h = odds_d = odds_a = 0.0
                    if odds_res and isinstance(odds_res, list) and isinstance(odds_res[0], dict):
                        bookies = odds_res[0].get('bookmakers') or []
                        if bookies and isinstance(bookies, list):
                            bets = bookies[0].get('bets') or []
                            for b in bets:
                                if b.get('name') == 'Match Winner':
                                    for v in (b.get('values') or []):
                                        if str(v.get('value')) == 'Home': odds_h = float(v.get('odd', 0))
                                        elif str(v.get('value')) == 'Draw': odds_d = float(v.get('odd', 0))
                                        elif str(v.get('value')) == 'Away': odds_a = float(v.get('odd', 0))
                                    break
                    
                    h_power = sum(h_vals[:3]); a_power = sum(a_vals[:3])
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
                    ou_line = 2.5; pred_is_over = True
                    if under_over_val:
                        if '-' in under_over_val: 
                            pred_is_over = False
                            try: ou_line = float(under_over_val.replace('-', '').replace('+', '').strip())
                            except Exception: pass
                        elif '+' in under_over_val: 
                            pred_is_over = True
                            try: ou_line = float(under_over_val.replace('+', '').replace('-', '').strip())
                            except Exception: pass
                    else: pred_is_over = (h_vals[4] + a_vals[4]) >= 120

                    ou_text_prefix = f"🔥 기준점 {ou_line} {'오버' if pred_is_over else '언더'}"
                    ou_color = "#ddd"
                    if is_finished:
                        if (h_g + a_g > ou_line) == pred_is_over: over_under = f"{ou_text_prefix} (적중)"; ou_color = "#FFF59D" 
                        else: over_under = f"{ou_text_prefix} (미적중)"; ou_color = "#F48FB1" 
                    else: over_under = ou_text_prefix

                    advice = translate_to_ko(pred.get('predictions', {}).get('advice', '분석 완료'))
                    ref_text = f"👨‍⚖️ 주심: {referee} | 🏟️ {venue}"

                    st.session_state['analyzed_data_list'].append(dict(sport="축구", league=top_league_display, match_display=match_display, stat_box=stat_box, referee=ref_text, p_h=p_h, p_d=p_d, p_a=p_a, win_pick=win_pick, pick_color=pick_color, ou_color=ou_color, handi_color="#ddd", control_pick=advice, over_under=over_under, handi_pick="", radar_html=radar_html, lineup_html=get_lineup_table(home_kr, away_kr, lineup_data), detail_html=detail_html))
                except Exception: pass
                
        if not limit_hit and len(st.session_state['analyzed_data_list']) == 0: 
            st.info(f"선택하신 리그에 {selected_date} 일자로 배정된 축구 경기가 없습니다.")
            
        progress_bar.progress(1.0)
        if not limit_hit: status_text.text("✅ 축구 데이터 스캔 및 분석 완료!")
        time.sleep(1.5)
        status_text.empty()
        progress_bar.empty()

# ==========================================
# ⚾ 야구 로직 (축구 완성 전 임시 비활성화)
# ==========================================
elif selected_sport == "야구":
    st.info("⚾ 야구 종목은 축구 로직 완벽 검증 후 구축 예정입니다. 현재는 껍데기만 존재합니다.")

# ==========================================
# 🏀 농구 로직 (축구 완성 전 임시 비활성화)
# ==========================================
elif selected_sport == "농구":
    st.info("🏀 농구 종목은 축구 로직 완벽 검증 후 구축 예정입니다. 현재는 껍데기만 존재합니다.")

# ==========================================
# 🏐 배구 로직 (축구 완성 전 임시 비활성화)
# ==========================================
elif selected_sport == "배구":
    st.info("🏐 배구 종목은 축구 로직 완벽 검증 후 구축 예정입니다. 현재는 껍데기만 존재합니다.")


# ==========================================
# 📺 8. 공통 렌더링 엔진 (분석 카드 출력부)
# ==========================================
if st.session_state.get('analyzed_data_list'):
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_data_list']):
        with cols[idx % 3]:
            if data['sport'] in ["야구", "농구"]: prob_bar = f"<div class='prob-wrapper'><div class='prob-text'><span>홈 승 {data['p_h']}%</span><span>원정 승 {data['p_a']}%</span></div><div class='prob-container'><div class='prob-home' style='width: {data['p_h']}%;'></div><div class='prob-away' style='width: {data['p_a']}%;'></div></div></div>"
            else: prob_bar = f"<div class='prob-wrapper'><div class='prob-text'><span>승 {data['p_h']}%</span><span>무 {data['p_d']}%</span><span>패 {data['p_a']}%</span></div><div class='prob-container'><div class='prob-home' style='width: {data['p_h']}%;'></div><div class='prob-draw' style='width: {data['p_d']}%;'></div><div class='prob-away' style='width: {data['p_a']}%;'></div></div></div>"
            handi_html = f"<div class='handi-txt' style='color: {data.get('handi_color', '#ddd')}'>{data.get('handi_pick', '')}</div>" if data.get('handi_pick') else ""
            html_str = f"<div style='height: 100%;'><div class='card-box'><div class='card-top'><div class='league-txt'>{data['league']}</div>{data['match_display']}<div class='referee-txt'>{data['referee']}</div></div><div class='card-mid'>{prob_bar}<div class='stat-bg'>{data['stat_box']}</div></div><div class='card-bot'><div class='predict-txt' style='color: {data['pick_color']};'>🎯 {data['win_pick']}</div>{handi_html}<div class='over-under' style='color: {data['ou_color']};'>{data['over_under']}</div><div class='ai-advice'>⚔️ {data['control_pick']}</div></div></div></div>"
            st.markdown(html_str, unsafe_allow_html=True)
            with st.expander("🔍 상세 지표 & 명단 확인"):
                if data.get('detail_html'): st.markdown(data['detail_html'], unsafe_allow_html=True)
                if data.get('radar_html'): st.markdown(data['radar_html'], unsafe_allow_html=True)
                if data.get('lineup_html'): st.markdown(data['lineup_html'], unsafe_allow_html=True)
            st.write("")
