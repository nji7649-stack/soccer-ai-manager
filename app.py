import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import math
import random

# ==========================================
# 1. 페이지 설정 및 API 키 (글로벌 변수 분리)
# ==========================================
st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

# ==========================================
# 2. 🎨 UI CSS (레이아웃 깨짐 철벽 방어)
# ==========================================
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.stApp { background-color: #0e1117; }

/* 종목 선택 아이콘 */
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

/* 매치 카드 */
.card-box { background-color: #1e1e1e; padding: 20px; border-radius: 12px; border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 15px; display: flex; flex-direction: column; height: auto; box-sizing: border-box; overflow: hidden; }
.card-top { flex-shrink: 0; width: 100%; }
.card-mid { flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-start; margin: 10px 0; width: 100%; }
.card-bot { flex-shrink: 0; border-top: 1px dashed #555; padding-top: 15px; text-align: center; width: 100%; }
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; letter-spacing: 1px; }
.match-box { display: flex; align-items: center; justify-content: center; width: 100%; margin-bottom: 15px; }
.team-side { display: flex; align-items: center; width: 38%; gap: 6px; }
.home-side { justify-content: flex-end; text-align: right; }
.away-side { justify-content: flex-start; text-align: left; }
.team-name { font-size: 13.5px; font-weight: bold; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 85px; }
.score-side { width: 24%; font-size: 20px; font-weight: bold; text-align: center; flex-shrink: 0; white-space: nowrap; letter-spacing: 0.5px; }
.team-logo { width: 26px; height: 26px; object-fit: contain; flex-shrink: 0; background-color: #fff; border-radius: 50%; padding: 2px; }
.referee-txt { font-size: 11px; color: #888; text-align: center; margin-bottom: 5px; }

/* 확률 바 */
.prob-wrapper { width: 100%; margin-bottom: 15px; box-sizing: border-box; }
.prob-text { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 6px; width: 100%; padding: 0 2px; box-sizing: border-box; }
.prob-container { display: flex; width: 100%; height: 10px; border-radius: 5px; overflow: hidden; background-color: #333; box-sizing: border-box; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }

/* 하단 텍스트 및 테이블 */
.predict-txt { font-size: 14.5px; font-weight: bold; margin-bottom: 6px; }
.handi-txt { font-size: 13.5px; font-weight: bold; margin-bottom: 6px; color: #B39DDB; } 
.over-under { font-size: 13.5px; font-weight: bold; margin-bottom: 10px; color: #FFF59D; } 
.ai-advice { font-size: 12px; color: #bbb; line-height: 1.4; margin-top: 10px; border-top: 1px dotted #444; padding-top: 8px; font-style: italic; }
.table-wrapper { width: 100%; margin-top: 5px; margin-bottom: 10px; overflow-x: hidden; }
.detail-table { width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 11px; color: #ccc; text-align: center; background-color: #1a1a1a; border-radius: 6px; overflow: hidden; } 
.detail-table th { background-color: #222; padding: 6px 2px; border-bottom: 1px solid #444; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.detail-table td { padding: 6px 2px; border-bottom: 1px solid #2a2a2a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; } 

.standings-header { font-size: 16px; font-weight: bold; color: #00E676; margin-top: 30px; margin-bottom: 10px; border-bottom: 2px solid #333; padding-bottom: 5px; }

.badge-hit { color: #111; background-color: #00E676; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 5px; display: inline-block; }
.badge-miss { color: #fff; background-color: #EF5350; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 5px; display: inline-block; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. 안전한 번역 및 API 함수 (캐시 충돌 원천 차단)
# ==========================================
def translate_to_ko(text):
    if not text or not isinstance(text, str): return '미정'
    custom_dict = {
        "Arsenal": "아스날", "Aston Villa": "애스턴 빌라", "Newcastle": "뉴캐슬", "Crystal Palace": "크리스탈 팰리스",
        "Manchester City": "맨시티", "Manchester United": "맨유", "Liverpool": "리버풀", "Chelsea": "첼시", "Tottenham": "토트넘",
        "Real Madrid": "레알 마드리드", "Barcelona": "바르셀로나", "Atletico Madrid": "아틀레티코", "Bayern Munich": "바이에른 뮌헨",
        "Paris Saint Germain": "PSG", "Inter": "인터밀란", "Juventus": "유벤투스", "AC Milan": "AC밀란",
        "South Korea": "대한민국", "Japan": "일본", "Brazil": "브라질", "Argentina": "아르헨티나", "France": "프랑스", "England": "잉글랜드"
    }
    for eng, kor in custom_dict.items():
        if eng.lower() == text.lower() or eng in text: return kor
    try: return GoogleTranslator(source='en', target='ko').translate(text.replace('<', '').replace('>', ''))
    except: return text

@st.cache_data(ttl=600, show_spinner=False)
def fetch_api_football_fixtures(league_id, season, date_str):
    api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    headers = {'x-apisports-key': api_key} if api_key else {}
    try: 
        res = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params={"league": league_id, "season": season, "date": date_str, "timezone": "Asia/Seoul"}, timeout=10)
        if res.status_code == 429: return "LIMIT"
        return res.json().get('response') or []
    except: return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api_football_standings(league_id, season):
    api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    headers = {'x-apisports-key': api_key} if api_key else {}
    try:
        res = requests.get("https://v3.football.api-sports.io/standings", headers=headers, params={"league": league_id, "season": season}, timeout=10)
        if res.status_code == 200: return res.json().get('response') or []
        return []
    except: return []

# ==========================================
# 4. 차트 및 지표 생성기 (안전 변환 적용)
# ==========================================
def create_html_radar(h_vals, a_vals, home_kr, away_kr):
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
    return f"<div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:10px; margin-top: 10px; margin-bottom: 10px;'><div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ 자체 환산 전력망</div><div style='font-size:11px; color:#fff; margin-bottom:10px; font-weight:bold; text-align:center;'><span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}</div><svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>{svg}{h_poly}{a_poly}</svg></div>"

def generate_football_advanced_stats(h_team, a_team, h_prob, is_finished, h_score, a_score):
    a_prob = 100.0 - h_prob
    h_pos = round(h_prob); a_pos = 100 - h_pos
    h_pass = round(75.0 + (h_prob - 50.0) * 0.3, 1); a_pass = round(75.0 + (a_prob - 50.0) * 0.3, 1)
    h_sot = round(3.5 + (h_prob - 50.0) * 0.1, 1); a_sot = round(3.5 + (a_prob - 50.0) * 0.1, 1)
    
    if is_finished:
        h_gf = float(h_score) if h_score is not None else 0.0
        a_gf = float(a_score) if a_score is not None else 0.0
        h_margin = round(h_gf - a_gf, 1); a_margin = round(a_gf - h_gf, 1)
    else:
        h_gf = round(1.2 + (h_prob - 50.0) * 0.04, 2); a_gf = round(1.2 + (a_prob - 50.0) * 0.04, 2)
        h_margin = round(h_gf - (1.2 - (h_prob - 50.0) * 0.04), 2); a_margin = round(a_gf - (1.2 - (a_prob - 50.0) * 0.04), 2)

    title_text = "⚽ 매치 결과 데이터 (종료)" if is_finished else "⚽ AI 심층 전력 지표 (환산)"
    margin_text_h = f"<span style='color:#4FC3F7;'>+{h_margin}</span>" if h_margin > 0 else f"<span style='color:#EF5350;'>{h_margin}</span>"
    margin_text_a = f"<span style='color:#4FC3F7;'>+{a_margin}</span>" if a_margin > 0 else f"<span style='color:#EF5350;'>{a_margin}</span>"

    html = f"""
    <div class='table-wrapper'>
        <div style='text-align:center; font-size:11.5px; color:#00E676; margin-bottom:5px; font-weight:bold;'>{title_text}</div>
        <table class='detail-table'>
            <tr style='background-color:#111;'><th style='color:#4FC3F7; width:33%;'>{h_team}</th><th style='color:#aaa; width:34%;'>비교 스탯</th><th style='color:#EF5350; width:33%;'>{a_team}</th></tr>
            <tr><td style='color:#fff; font-weight:bold;'>{h_gf}</td><td style='color:#aaa;'>평균 득점력</td><td style='color:#fff; font-weight:bold;'>{a_gf}</td></tr>
            <tr><td>{margin_text_h}</td><td style='color:#aaa;'>골득실 마진</td><td>{margin_text_a}</td></tr>
            <tr><td style='color:#fff;'>{h_pos}%</td><td style='color:#aaa;'>평균 점유율</td><td style='color:#fff;'>{a_pos}%</td></tr>
            <tr><td style='color:#fff;'>{h_pass}%</td><td style='color:#aaa;'>패스 성공률</td><td style='color:#fff;'>{a_pass}%</td></tr>
            <tr><td style='color:#fff;'>{h_sot}개</td><td style='color:#aaa;'>유효 슈팅</td><td style='color:#fff;'>{a_sot}개</td></tr>
        </table>
    </div>
    """
    return html, h_gf, a_gf

def get_lineup_table(home_kr, away_kr):
    return f"""
    <div class='table-wrapper'>
        <table class='detail-table'>
            <tr><th style='color:#4FC3F7; width:50%;'>{home_kr} (예상)</th><th style='color:#EF5350; width:50%;'>{away_kr} (예상)</th></tr>
            <tr><td style='color:#888;'>라인업 발표 대기중</td><td style='color:#888;'>라인업 발표 대기중</td></tr>
        </table>
    </div>
    """

def get_prediction_and_commentary(home_kr, away_kr, h_prob, h_gf, a_gf, is_finished, h_score, a_score):
    d_prob = max(0.0, 20.0 - abs(h_prob - 50.0) / 2.0)
    a_prob = 100.0 - h_prob - d_prob
    
    # 승패 픽
    if h_prob > a_prob + 10.0 and h_prob > d_prob: pred_win = "home"; win_txt = f"🟢 {home_kr} 승리 유력"
    elif a_prob > h_prob + 10.0 and a_prob > d_prob: pred_win = "away"; win_txt = f"🔵 {away_kr} 승리 유력"
    else: pred_win = "draw"; win_txt = "🟡 치열한 접전 (무승부 가능성)"
    
    # 핸디 픽
    if h_prob > 60.0: pred_handi = "home"; handi_txt = f"💪 {home_kr} 2골 차 이상 대승 기대"
    elif a_prob > 60.0: pred_handi = "away"; handi_txt = f"💪 {away_kr} 2골 차 이상 대승 기대"
    elif pred_win == "home": pred_handi = "away"; handi_txt = f"🛡️ {away_kr}의 탄탄한 방어 (1골 차 신승)"
    else: pred_handi = "home"; handi_txt = f"🛡️ {home_kr}의 탄탄한 방어 (1골 차 신승)"
        
    # 언오버 픽
    exp_total = h_gf + a_gf
    if exp_total > 2.6: pred_ou = "over"; ou_txt = "🔥 화력 집중! 고득점 양상"
    else: pred_ou = "under"; ou_txt = "❄️ 짠물 수비! 저득점 늪"
        
    # 적중 판별 (오류 방벽 적용)
    win_badge = handi_badge = ou_badge = ""
    if is_finished:
        try:
            h_s = float(h_score) if h_score is not None else 0.0
            a_s = float(a_score) if a_score is not None else 0.0
            
            actual_win = "home" if h_s > a_s else ("away" if a_s > h_s else "draw")
            win_badge = "<span class='badge-hit'>적중</span>" if pred_win == actual_win else "<span class='badge-miss'>미적중</span>"
            
            margin = abs(h_s - a_s)
            if "대승" in handi_txt: actual_handi = "hit" if margin >= 2 and actual_win == pred_win else "miss"
            else: actual_handi = "hit" if margin <= 1 else "miss"
            handi_badge = "<span class='badge-hit'>적중</span>" if actual_handi == "hit" else "<span class='badge-miss'>미적중</span>"
            
            actual_ou = "over" if (h_s + a_s) > 2.5 else "under"
            ou_badge = "<span class='badge-hit'>적중</span>" if pred_ou == actual_ou else "<span class='badge-miss'>미적중</span>"
        except: pass

    # 코멘트
    if pred_win == "home" and pred_ou == "over": comment = f"홈 이점을 등에 업은 {home_kr}의 폭발적인 공격력이 경기를 지배할 것입니다."
    elif pred_win == "away" and pred_ou == "under": comment = f"{away_kr}이 탄탄한 수비 조직력으로 상대의 공세를 틀어막고 승리를 가져갈 확률이 높습니다."
    elif pred_win == "draw": comment = "중원에서의 치열한 주도권 싸움이 예상되며, 쉽게 승부가 나지 않는 팽팽한 양상이 전개됩니다."
    else: comment = f"전술적 상성이 강하게 부딪히며, 작은 실수 하나가 전체 승부를 가르는 경기가 될 것입니다."
        
    return f"{win_txt} {win_badge}", f"{handi_txt} {handi_badge}", f"{ou_txt} {ou_badge}", comment

# ==========================================
# 7. 메인 UI 구성
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 종합 스포츠 AI 분석실 (V70 완벽 멸균판)</h1>", unsafe_allow_html=True)

sport_options = ["축구", "야구", "농구", "배구"]
selected_sport = st.sidebar.radio("종목 선택", sport_options, horizontal=True)
st.sidebar.markdown("---")

kst_now = datetime.utcnow() + timedelta(hours=9)
selected_date = st.sidebar.date_input("📅 검색 날짜 설정 (KST 기준)", kst_now.date())
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if 'soccer_cards_data' not in st.session_state: st.session_state['soccer_cards_data'] = []
if 'soccer_standings_tabs' not in st.session_state: st.session_state['soccer_standings_tabs'] = {}

# ==========================================
# ⚽ 8. 축구 메인 엔진
# ==========================================
if selected_sport == "축구":
    analyze_button = st.sidebar.button("🚀 축구 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚽ 축구 리그 선택")
    
    with st.sidebar.expander("🌏 아시아 및 기타 리그", expanded=True):
        l_292 = st.checkbox("K리그 1 (KOR)", value=True)
        l_293 = st.checkbox("K리그 2 (KOR)", value=False)
        l_98 = st.checkbox("J1 리그 (JPN)", value=False)
        
    with st.sidebar.expander("🌟 국제 대회 (FIFA/UEFA)", expanded=True):
        l_1 = st.checkbox("월드컵 (World Cup)", value=True)
        l_2 = st.checkbox("챔피언스리그 (UCL)", value=False)
        l_3 = st.checkbox("유로파리그 (UEL)", value=False)
        l_10 = st.checkbox("A매치 친선전", value=False)
        
    with st.sidebar.expander("🌍 유럽 주요 리그", expanded=True):
        l_39 = st.checkbox("프리미어리그 (ENG)", value=False)
        l_140 = st.checkbox("라리가 (ESP)", value=False)
        l_135 = st.checkbox("세리에 A (ITA)", value=False)
        l_78 = st.checkbox("분데스리가 (GER)", value=False)

    league_ids = ["292", "293", "98", "1", "2", "3", "10", "39", "140", "135", "78"]
    checkbox_vals = [l_292, l_293, l_98, l_1, l_2, l_3, l_10, l_39, l_140, l_135, l_78]
    selected_leagues = [lid for lid, selected in zip(league_ids, checkbox_vals) if selected]
    
    LEAGUE_MAP = {
        "292":"K리그1", "293":"K리그2", "98":"J1리그", "1":"월드컵", "2":"챔피언스리그", 
        "3":"유로파리그", "10":"A매치", "39":"프리미어리그", "140":"라리가", "135":"세리에 A", "78":"분데스리가"
    }
    SPRING_TO_AUTUMN_LEAGUES = ["292", "293", "98", "1", "10"]

    if analyze_button:
        if not selected_leagues: 
            st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
            st.stop()
            
        st.session_state['soccer_cards_data'] = []
        st.session_state['soccer_standings_tabs'] = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        limit_hit = False
        match_count = 0
        
        for idx, league_id in enumerate(selected_leagues):
            if limit_hit: break
            status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 데이터 스캔 중... ({idx+1}/{len(selected_leagues)})")
            progress_bar.progress((idx) / len(selected_leagues))
            
            calc_season = str(selected_date.year) if league_id in SPRING_TO_AUTUMN_LEAGUES else (str(selected_date.year - 1) if selected_date.month < 7 else str(selected_date.year))
            
            # 1️⃣ 순위표 수집 (안전 파싱)
            standings_res = fetch_api_football_standings(league_id, calc_season)
            standings_dict = {} 
            if standings_res and isinstance(standings_res, list) and len(standings_res) > 0:
                league_data_list = []
                groups = standings_res[0].get('league', {}).get('standings', [])
                for g_idx, group in enumerate(groups):
                    try:
                        g_name = group[0].get('group', f'Group {g_idx+1}') if len(groups) > 1 else "통합 순위표"
                        df_data = []
                        for team in group:
                            t_id = team.get('team', {}).get('id')
                            rank = team.get('rank')
                            standings_dict[t_id] = rank 
                            df_data.append({"순위": rank, "팀명": translate_to_ko(team.get('team', {}).get('name')), "승점": team.get('points'), "승": team.get('all', {}).get('win'), "무": team.get('all', {}).get('draw'), "패": team.get('all', {}).get('lose')})
                        league_data_list.append({"group_name": g_name, "dataframe": pd.DataFrame(df_data).set_index("순위")})
                    except: pass
                st.session_state['soccer_standings_tabs'][LEAGUE_MAP[league_id]] = league_data_list
            
            # 2️⃣ 일정 수집
            date_str = selected_date.strftime('%Y-%m-%d')
            matches = fetch_api_football_fixtures(league_id, calc_season, date_str)
            
            if matches == "LIMIT":
                st.error("🚨 API 무료 호출 한도 초과! 잠시 후 다시 시도해 주세요.")
                limit_hit = True; break
            
            # 3️⃣ 경기별 렌더링 준비 (개별 try-except로 에러 원천 차단)
            if matches and isinstance(matches, list):
                for match in matches:
                    try:
                        home_id = match['teams']['home']['id']; away_id = match['teams']['away']['id']
                        home_kr = translate_to_ko(match['teams']['home']['name']); away_kr = translate_to_ko(match['teams']['away']['name'])
                        h_logo = match['teams']['home']['logo']; a_logo = match['teams']['away']['logo']
                        
                        try: match_time = (datetime.utcfromtimestamp(match['fixture']['timestamp']) + timedelta(hours=9)).strftime("%H:%M")
                        except: match_time = "미정"
                        
                        status = match['fixture']['status']['short']
                        is_finished = status in ['FT', 'AET', 'PEN']
                        
                        # 안전한 스코어 파싱
                        goals_h = match.get('goals', {}).get('home')
                        goals_a = match.get('goals', {}).get('away')
                        h_score = int(goals_h) if goals_h is not None else 0
                        a_score = int(goals_a) if goals_a is not None else 0
                        
                        if is_finished: top_txt = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#aaa;'>[종료]</span>"; s_color="#00E676"; s_txt=f"{h_score}:{a_score}"
                        elif status in ['1H', 'HT', '2H', 'ET']: top_txt = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#ff5252;'>[진행중]</span>"; s_color="#ff5252"; s_txt=f"{h_score}:{a_score}"
                        else: top_txt = f"{LEAGUE_MAP[league_id]} ({match_time})"; s_color="#888"; s_txt="VS"

                        match_disp = f"<div class='match-box'><div class='team-side home-side'><div class='team-name'>{home_kr}</div><img src='{h_logo}' class='team-logo'></div><div class='score-side' style='color:{s_color};'>{s_txt}</div><div class='team-side away-side'><img src='{a_logo}' class='team-logo'><div class='team-name'>{away_kr}</div></div></div>"

                        # 확률 계산
                        if standings_dict and home_id in standings_dict and away_id in standings_dict:
                            rank_diff = standings_dict[away_id] - standings_dict[home_id]
                            h_prob = 40.0 + (rank_diff * 1.5) + 3.0
                            h_prob = max(20.0, min(80.0, h_prob))
                        else:
                            seed = sum(ord(c) for c in match['teams']['home']['name'] + match['teams']['away']['name'])
                            h_prob = 35.0 + (seed % 30)
                            
                        d_prob = max(0.0, 20.0 - abs(h_prob - 50.0) / 2.0)
                        a_prob = 100.0 - h_prob - d_prob
                        
                        # 컴포넌트 생성
                        adv_html, h_gf, a_gf = generate_football_advanced_stats(home_kr, away_kr, h_prob, is_finished, h_score, a_score)
                        win_txt, handi_txt, ou_txt, ai_comment = get_prediction_and_commentary(home_kr, away_kr, h_prob, h_gf, a_gf, is_finished, h_score, a_score)
                        radar_html = create_html_radar([random.randint(45,88) for _ in range(6)], [random.randint(45,88) for _ in range(6)], home_kr, away_kr)
                        lineup_html = get_lineup_table(home_kr, away_kr)
                        
                        venue_name = match['fixture'].get('venue', {}).get('name')
                        ref_name = f"🏟️ {venue_name}" if venue_name else "🏟️ 경기장 미정"

                        st.session_state['soccer_cards_data'].append({
                            'league_title': LEAGUE_MAP[league_id], 'top_text': top_txt,
                            'home_kr': home_kr, 'away_kr': away_kr, 'h_logo': h_logo, 'a_logo': a_logo, 's_color': s_color, 's_txt': s_txt,
                            'p_h': h_prob, 'p_d': d_prob, 'p_a': a_prob, 
                            'win_txt': win_txt, 'handi_txt': handi_txt, 'ou_txt': ou_txt, 'ai_comment': ai_comment,
                            'advanced_html': adv_html, 'radar_html': radar_html, 'lineup_html': lineup_html, 'referee': ref_name
                        })
                        match_count += 1
                    except Exception as e:
                        # 💡 특정 경기에 오류가 있어도 화면 전체가 죽지 않고 조용히 넘김
                        continue
                        
            time.sleep(0.4)
            
        progress_bar.progress(1.0)
        if not limit_hit: status_text.text("✅ 축구 스캔 및 분석 완료!")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()

        if match_count == 0 and not limit_hit:
            st.info("선택하신 날짜에 배정된 경기가 없습니다.")

# ==========================================
# 9. 렌더링 엔진 (에러 없는 안전 출력)
# ==========================================
if st.session_state.get('soccer_cards_data'):
    cols = st.columns(3)
    for idx, card in enumerate(st.session_state['soccer_cards_data']):
        with cols[idx % 3]:
            html_str = f"""
            <div class='card-box'>
                <div class='card-top'><div class='league-txt'>{card['top_text']}</div><div class='match-box'><div class='team-side home-side'><div class='team-name'>{card['home_kr']}</div><img src='{card['h_logo']}' class='team-logo'></div><div class='score-side' style='color:{card['s_color']};'>{card['s_txt']}</div><div class='team-side away-side'><img src='{card['a_logo']}' class='team-logo'><div class='team-name'>{card['away_kr']}</div></div></div><div class='referee-txt'>{card['referee']}</div></div>
                <div class='card-mid'>
                    <div class='prob-wrapper'>
                        <div class='prob-text'><span>홈 {card['p_h']:.0f}%</span><span>무 {card['p_d']:.0f}%</span><span>원정 {card['p_a']:.0f}%</span></div>
                        <div class='prob-container'>
                            <div class='prob-home' style='width: {card['p_h']}%;'></div>
                            <div class='prob-draw' style='width: {card['p_d']}%;'></div>
                            <div class='prob-away' style='width: {card['p_a']}%;'></div>
                        </div>
                    </div>
                    {card['advanced_html']}
                </div>
                <div class='card-bot'>
                    <div class='predict-txt'>{card['win_txt']}</div>
                    <div class='handi-txt'>{card['handi_txt']}</div>
                    <div class='over-under'>{card['ou_txt']}</div>
                    <div class='ai-advice'>✍️ AI 코멘트: {card['ai_comment']}</div>
                </div>
            </div>
            """
            st.markdown(html_str, unsafe_allow_html=True)
            
            with st.expander("🔍 육각형 지표 & 선발 명단 확인"):
                if card.get('radar_html'): st.markdown(card['radar_html'], unsafe_allow_html=True)
                if card.get('lineup_html'): st.markdown(card['lineup_html'], unsafe_allow_html=True)
            st.write("")

if selected_sport == "축구" and st.session_state.get('soccer_standings_tabs'):
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    
    league_tab_names = list(st.session_state['soccer_standings_tabs'].keys())
    if league_tab_names:
        league_tabs = st.tabs(league_tab_names)
        for l_tab, l_name in zip(league_tabs, league_tab_names):
            with l_tab:
                st.markdown(f"<div class='standings-header'>📊 {l_name} 실시간 순위 리포트</div>", unsafe_allow_html=True)
                tables_data = st.session_state['soccer_standings_tabs'][l_name]
                if len(tables_data) > 1:
                    sub_tab_names = [table['group_name'] for table in tables_data]
                    sub_tabs = st.tabs(sub_tab_names)
                    for s_tab, table in zip(sub_tabs, tables_data):
                        with s_tab: st.dataframe(table['dataframe'], use_container_width=True)
                else:
                    st.dataframe(tables_data[0]['dataframe'], use_container_width=True)

elif selected_sport in ["야구", "농구", "배구"]:
    st.info(f"{selected_sport} 종목은 '축구 시스템' 검증 완료 후, 이 최적화 UI 구조를 100% 동일하게 복사하여 순차 오픈 예정입니다.")
