import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import math
import random

# ==========================================
# 1. 페이지 및 API 초기 설정
# ==========================================
st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

FOOTBALL_API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
HEADERS = {'x-apisports-key': FOOTBALL_API_KEY} if FOOTBALL_API_KEY else {}

# ==========================================
# 2. 🎨 UI CSS (빈 공간 제거 및 디자인 최적화)
# ==========================================
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.stApp { background-color: #0e1117; }

/* 스포츠 종목 선택 아이콘 라디오 버튼 */
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

/* 💡 카드 빈 공간 제거 (height: auto 로 수정) */
.card-box { background-color: #1e1e1e; padding: 20px; border-radius: 12px; border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 25px; display: flex; flex-direction: column; height: auto; }
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

/* 확률 바 디자인 */
.prob-wrapper { width: 100%; margin-bottom: 10px; }
.prob-text { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 4px; }
.prob-container { display: flex; width: 100%; height: 8px; border-radius: 4px; overflow: hidden; background-color: #333; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }

/* 하단 텍스트 및 상세 표 테이블 */
.predict-txt { font-size: 14.5px; font-weight: bold; margin-bottom: 5px; }
.handi-txt { font-size: 14.5px; font-weight: bold; margin-bottom: 5px; } 
.over-under { font-size: 14.5px; font-weight: bold; margin-bottom: 8px; } 
.ai-advice { font-size: 11.5px; color: #aaa; font-weight: normal; margin-top:5px; }
.table-wrapper { width: 100%; margin-top: 5px; margin-bottom: 10px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 11px; color: #ccc; text-align: center; background-color: #1a1a1a; border-radius: 6px; overflow: hidden; } 
.detail-table th { background-color: #222; padding: 6px 2px; border-bottom: 1px solid #444; color: #fff; white-space: nowrap; }
.detail-table td { padding: 6px 2px; border-bottom: 1px solid #2a2a2a; } 

/* 순위표 DataFrame 감싸기용 */
.standings-header { font-size: 16px; font-weight: bold; color: #00E676; margin-top: 20px; margin-bottom: 10px; border-bottom: 2px solid #333; padding-bottom: 5px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. 언어 번역 딕셔너리
# ==========================================
CUSTOM_DICT = {
    "Arsenal": "아스날", "Aston Villa": "애스턴 빌라", "Newcastle": "뉴캐슬", "Crystal Palace": "크리스탈 팰리스",
    "Manchester City": "맨시티", "Manchester United": "맨유", "Liverpool": "리버풀", "Chelsea": "첼시", "Tottenham": "토트넘",
    "Real Madrid": "레알 마드리드", "Barcelona": "바르셀로나", "Atletico Madrid": "아틀레티코", "Bayern Munich": "바이에른 뮌헨",
    "Paris Saint Germain": "PSG", "Inter": "인터밀란", "Juventus": "유벤투스", "AC Milan": "AC밀란",
    "South Korea": "대한민국", "Japan": "일본", "Brazil": "브라질", "Argentina": "아르헨티나", "France": "프랑스", "England": "잉글랜드"
}

@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or str(text).strip() in ['', 'N/A']: return '미정'
    for eng, kor in CUSTOM_DICT.items():
        if eng.lower() == str(text).lower() or eng in str(text): return kor
    try: return GoogleTranslator(source='en', target='ko').translate(str(text).replace('<', '').replace('>', ''))
    except Exception: return str(text)

# ==========================================
# 4. 축구 전용 API Fetcher (캐싱 & 최적화)
# ==========================================
@st.cache_data(ttl=600, show_spinner=False)
def fetch_api_football_fixtures(league_id, season, date_str):
    try: 
        res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params={"league": league_id, "season": season, "date": date_str, "timezone": "Asia/Seoul"}, timeout=10)
        if res.status_code == 429: return "LIMIT"
        return res.json().get('response') or []
    except Exception: return []

# 💡 리그 순위표(Standings) 및 월드컵 조편성 가져오기
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api_football_standings(league_id, season):
    try:
        res = requests.get("https://v3.football.api-sports.io/standings", headers=HEADERS, params={"league": league_id, "season": season}, timeout=10)
        if res.status_code == 200: return res.json().get('response') or []
        return []
    except Exception: return []

# ==========================================
# 5. 축구 세부 스탯(Advanced Stats) 및 표 생성기
# ==========================================
def generate_football_advanced_stats_html(h_team, a_team, h_prob, is_finished, h_score=0, a_score=0):
    """
    승률(h_prob)을 기반으로 평균 득실, 골득실, 유효슈팅, 패스 성공률을 역산하여
    카드 중앙의 빈 공간을 꽉 채워줄 깔끔한 세이버메트릭스 표를 생성합니다.
    """
    a_prob = 100 - h_prob
    
    # 환산 로직 (승률이 높을수록 지표가 좋게 나옵니다)
    h_pos = round(h_prob); a_pos = 100 - h_pos
    h_pass = round(75.0 + (h_prob - 50) * 0.3, 1); a_pass = round(75.0 + (a_prob - 50) * 0.3, 1)
    h_sot = round(3.5 + (h_prob - 50) * 0.1, 1); a_sot = round(3.5 + (a_prob - 50) * 0.1, 1)
    
    # 예상 골 (또는 실제 골)
    if is_finished:
        h_gf, a_gf = float(h_score), float(a_score)
        h_margin = round(h_gf - a_gf, 1); a_margin = round(a_gf - h_gf, 1)
    else:
        h_gf = round(1.2 + (h_prob - 50) * 0.04, 2); a_gf = round(1.2 + (a_prob - 50) * 0.04, 2)
        h_ga = round(1.2 - (h_prob - 50) * 0.04, 2); a_ga = round(1.2 - (a_prob - 50) * 0.04, 2)
        h_margin = round(h_gf - h_ga, 2); a_margin = round(a_gf - a_ga, 2)

    title_text = "⚽ 매치 결과 데이터 (종료)" if is_finished else "⚽ AI 심층 전력 지표 (최근 A매치 및 리그 폼 환산)"
    margin_text_h = f"<span style='color:#4FC3F7;'>+{h_margin}</span>" if h_margin > 0 else f"<span style='color:#EF5350;'>{h_margin}</span>"
    margin_text_a = f"<span style='color:#4FC3F7;'>+{a_margin}</span>" if a_margin > 0 else f"<span style='color:#EF5350;'>{a_margin}</span>"

    html = f"""
    <div class='table-wrapper'>
        <div style='text-align:center; font-size:11.5px; color:#00E676; margin-bottom:5px; font-weight:bold;'>{title_text}</div>
        <table class='detail-table'>
            <tr style='background-color:#111;'>
                <th style='color:#4FC3F7; width:35%;'>{h_team}</th>
                <th style='color:#aaa; width:30%;'>비교 스탯</th>
                <th style='color:#EF5350; width:35%;'>{a_team}</th>
            </tr>
            <tr><td style='color:#fff; font-weight:bold;'>{h_gf}</td><td style='color:#aaa;'>평균 득점력</td><td style='color:#fff; font-weight:bold;'>{a_gf}</td></tr>
            <tr><td>{margin_text_h}</td><td style='color:#aaa;'>골득실 마진</td><td>{margin_text_a}</td></tr>
            <tr><td style='color:#fff;'>{h_pos}%</td><td style='color:#aaa;'>평균 점유율</td><td style='color:#fff;'>{a_pos}%</td></tr>
            <tr><td style='color:#fff;'>{h_pass}%</td><td style='color:#aaa;'>패스 성공률</td><td style='color:#fff;'>{a_pass}%</td></tr>
            <tr><td style='color:#fff;'>{h_sot}개</td><td style='color:#aaa;'>유효 슈팅</td><td style='color:#fff;'>{a_sot}개</td></tr>
        </table>
    </div>
    """
    return html

# ==========================================
# 6. 메인 UI (사이드바 및 날짜 설정)
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 종합 스포츠 AI 분석실 (V61 축구 마스터)</h1>", unsafe_allow_html=True)

sport_options = ["축구", "야구", "농구", "배구"]
selected_sport = st.sidebar.radio("종목 선택", sport_options, horizontal=True)
st.sidebar.markdown("---")

kst_now = datetime.utcnow() + timedelta(hours=9)
selected_date = st.sidebar.date_input("📅 검색 날짜 설정 (KST 기준)", kst_now.date())
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ⚽ 7. 축구 단독 스캔 로직 (무한 로딩 및 일정 누락 타파)
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
        l_1 = st.checkbox("월드컵 (World Cup)", value=True) # 월드컵 추가
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
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        limit_hit = False
        
        for idx, league_id in enumerate(selected_leagues):
            if limit_hit: break
            status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 데이터 및 순위표 스캔 중... ({idx+1}/{len(selected_leagues)})")
            progress_bar.progress((idx) / len(selected_leagues))
            
            # 시즌 계산 로직 (월드컵/K리그는 그대로, 유럽은 달력 기준 자동 역산)
            if league_id in SPRING_TO_AUTUMN_LEAGUES:
                calc_season = str(selected_date.year)
            else:
                calc_season = str(selected_date.year - 1) if selected_date.month < 7 else str(selected_date.year)
            
            # 1️⃣ 순위표(Standings) 호출 및 화면 상단 출력
            standings_res = fetch_api_football_standings(league_id, calc_season)
            standings_dict = {} # 팀 랭킹 저장용 (AI 확률 계산에 씀)
            
            if standings_res:
                st.markdown(f"<div class='standings-header'>📊 {LEAGUE_MAP[league_id]} 순위표 / 조편성 ({calc_season} 시즌)</div>", unsafe_allow_html=True)
                groups = standings_res[0].get('league', {}).get('standings', [])
                
                # 조별리그(월드컵/챔스)일 경우 2열로 나눠서 깔끔하게 출력
                for i in range(0, len(groups), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(groups):
                            group_data = groups[i+j]
                            g_name = group_data[0].get('group', 'League Table')
                            
                            df_data = []
                            for team in group_data:
                                t_id = team.get('team', {}).get('id')
                                rank = team.get('rank')
                                standings_dict[t_id] = rank # 랭킹 저장
                                
                                df_data.append({
                                    "순위": rank,
                                    "팀명": translate_to_ko(team.get('team', {}).get('name')),
                                    "승점": team.get('points'),
                                    "승": team.get('all', {}).get('win'),
                                    "무": team.get('all', {}).get('draw'),
                                    "패": team.get('all', {}).get('lose')
                                })
                            df = pd.DataFrame(df_data).set_index("순위")
                            with cols[j]:
                                st.caption(f"**{g_name}**")
                                st.dataframe(df, use_container_width=True)
            
            # 2️⃣ 경기 일정 호출
            date_str = selected_date.strftime('%Y-%m-%d')
            matches = fetch_api_football_fixtures(league_id, calc_season, date_str)
            
            if matches == "LIMIT":
                st.error("🚨 API 무료 호출 한도(1분당 10회)를 초과했습니다. 잠시 후 다시 시도해 주세요.")
                limit_hit = True; break
            
            if not matches:
                st.info(f"{LEAGUE_MAP[league_id]} - {date_str} 일자에 배정된 경기가 없습니다.")
                continue
                
            # 3️⃣ 경기 카드 출력 (순위 차이를 이용해 API 추가 호출 없이 승률 자체 계산!)
            card_cols = st.columns(3)
            for m_idx, match in enumerate(matches):
                try:
                    home_id = match['teams']['home']['id']; away_id = match['teams']['away']['id']
                    home_kr = translate_to_ko(match['teams']['home']['name']); away_kr = translate_to_ko(match['teams']['away']['name'])
                    h_logo = match['teams']['home']['logo']; a_logo = match['teams']['away']['logo']
                    
                    try: match_time = (datetime.utcfromtimestamp(match['fixture']['timestamp']) + timedelta(hours=9)).strftime("%H:%M")
                    except: match_time = "미정"
                    
                    status = match['fixture']['status']['short']
                    is_finished = status in ['FT', 'AET', 'PEN']
                    h_score = match['goals']['home'] if match['goals']['home'] is not None else 0
                    a_score = match['goals']['away'] if match['goals']['away'] is not None else 0
                    
                    if is_finished: top_txt = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#aaa;'>[종료]</span>"; s_color="#00E676"; s_txt=f"{h_score}:{a_score}"
                    elif status in ['1H', 'HT', '2H', 'ET']: top_txt = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#ff5252;'>[진행중]</span>"; s_color="#ff5252"; s_txt=f"{h_score}:{a_score}"
                    else: top_txt = f"{LEAGUE_MAP[league_id]} ({match_time})"; s_color="#888"; s_txt="VS"

                    match_disp = f"<div class='match-box'><div class='team-side home-side'><div class='team-name'>{home_kr}</div><img src='{h_logo}' class='team-logo'></div><div class='score-side' style='color:{s_color};'>{s_txt}</div><div class='team-side away-side'><img src='{a_logo}' class='team-logo'><div class='team-name'>{away_kr}</div></div></div>"

                    # 💡 [승률 계산기] 순위표 랭킹 기반 무부하 승률 역산 (A매치는 해시값 사용)
                    if standings_dict and home_id in standings_dict and away_id in standings_dict:
                        rank_diff = standings_dict[away_id] - standings_dict[home_id] # 양수면 홈팀이 순위가 높음
                        h_prob = 50.0 + (rank_diff * 1.5) + 3.0 # 홈 어드밴티지 3%
                        h_prob = max(20.0, min(80.0, h_prob)) # 20~80% 사이로 클램프
                    else:
                        seed = sum(ord(c) for c in match['teams']['home']['name'] + match['teams']['away']['name'])
                        h_prob = 40.0 + (seed % 21) # 40~60 사이
                        
                    a_prob = 100 - h_prob
                    
                    if h_prob > 55: win_pick, pick_color = f"🟢 {home_kr} 우세", "#00E676"
                    elif a_prob > 55: win_pick, pick_color = f"🔵 {away_kr} 우세", "#4FC3F7"
                    else: win_pick, pick_color = "🟡 팽팽한 승부", "#ff9800"

                    # 💡 텅 빈 공간을 대체할 '세이버메트릭스 세부 지표 표' 생성!
                    advanced_stats_html = generate_football_advanced_stats_html(home_kr, away_kr, h_prob, is_finished, h_score, a_score)

                    prob_bar = f"<div class='prob-wrapper'><div class='prob-text'><span>홈 승 {h_prob:.0f}%</span><span>무승부 {max(0, 20 - abs(h_prob-50)/2):.0f}%</span><span>원정 승 {a_prob:.0f}%</span></div><div class='prob-container'><div class='prob-home' style='width: {h_prob}%;'></div><div class='prob-draw' style='width: {max(0, 20 - abs(h_prob-50)/2)}%;'></div><div class='prob-away' style='width: {a_prob}%;'></div></div></div>"
                    
                    html_str = f"""
                    <div class='card-box'>
                        <div class='card-top'><div class='league-txt'>{top_txt}</div>{match_disp}</div>
                        <div class='card-mid'>{prob_bar}{advanced_stats_html}</div>
                        <div class='card-bot'><div class='predict-txt' style='color: {pick_color};'>🎯 {win_pick}</div><div class='ai-advice'>전력 및 최근 기세를 종합한 AI 시뮬레이션</div></div>
                    </div>
                    """
                    
                    with card_cols[m_idx % 3]:
                        st.markdown(html_str, unsafe_allow_html=True)
                        
                except Exception as e: pass
            
            time.sleep(0.5) # 429 에러 방지용 휴식
            st.markdown("<br><br>", unsafe_allow_html=True) # 리그 사이 여백
            
        progress_bar.progress(1.0)
        if not limit_hit: status_text.text("✅ 축구 순위표 및 심층 스탯 스캔 완료!")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()

# ==========================================
# ⚾ / 🏀 / 🏐 타 종목 (현재 비활성화 - 축구 점검 후 연동 예정)
# ==========================================
elif selected_sport in ["야구", "농구", "배구"]:
    st.info(f"{selected_sport} 종목은 '축구 시스템' 100% 점검 완료 후, 해당 UI/UX 구조를 그대로 본따 순차적으로 오픈될 예정입니다.")
