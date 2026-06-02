import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

# 🎨 1. 웹사이트 기본 설정
st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 2. 다크모드 카드 UI 디자인 
custom_css = """
<style>
    .stApp { background-color: #121212; }
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    .match-card {
        background: #1e1e1e; border: 1px solid #333; border-radius: 12px; 
        padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); 
        color: #ffffff; transition: 0.3s;
    }
    .match-card:hover { border-color: #00E676; transform: translateY(-5px); }
    .league-title { font-size: 0.85em; color: #ff9800; font-weight: bold; margin-bottom: 10px; }
    .teams-title { font-size: 1.2em; font-weight: bold; margin-bottom: 15px; text-align: center; }
    .stat-box { background: #2a2a2a; padding: 12px; border-radius: 8px; font-size: 0.9em; margin-bottom: 15px; color: #ccc; line-height: 1.6; }
    .ai-result { font-size: 1em; font-weight: bold; color: #00E676; border-top: 1px dashed #444; padding-top: 15px; text-align: center; line-height: 1.6; }
    details { margin-top: 15px; font-size: 0.85em; color: #aaa; cursor: pointer; }
    summary { outline: none; color: #00bcd4; font-weight: bold; margin-bottom: 10px; }
    .lineup-box { background: #222; padding: 10px; border-radius: 5px; line-height: 1.5; border-left: 3px solid #00bcd4; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 🔑 API 세팅
API_KEY = st.secrets["FOOTBALL_API_KEY"]
HEADERS = {'x-apisports-key': API_KEY}

@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    try: return GoogleTranslator(source='en', target='ko').translate(text)
    except: return text

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 라이브 AI 축구 승부 예측 PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>선택한 날짜와 리그의 모든 경기를 딥 다이브 분석합니다.</p>", unsafe_allow_html=True)

# 🔍 사이드바 설정
st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())

LEAGUE_MAP = {
    "1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", 
    "140": "라리가", "135": "세리에A", "78": "분데스리가", 
    "61": "리그1", "292": "K리그1"
}

selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["39", "140", "292"])

# 💡 스트림릿이 멍청하게 리셋되지 않게, 버튼이 눌리면 아예 함수 전체를 통째로 실행시켜버립니다.
if st.sidebar.button("🚀 데이터 불러오기 및 AI 분석"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    html_cards = ""
    total_leagues = len(selected_leagues)
    matches_found = False
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 데이터 분석 중... ({idx+1}/{total_leagues})")
        progress_bar.progress((idx) / total_leagues)
        
        querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            fixtures = res.get('response', [])
            
            for match in fixtures:
                matches_found = True
                fix_id = str(match['fixture']['id'])
                home_en = match['teams']['home']['name']
                away_en = match['teams']['away']['name']
                
                home_kr = translate_to_ko(home_en)
                away_kr = translate_to_ko(away_en)
                status = match['fixture']['status']['short']
                
                # 스탯 & 라인업 찌르기
                stats_data = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not stats_data or len(stats_data) < 2:
                    # 스탯이 없으면 회색빛 카드로 "데이터 없음"만 출력
                    html_cards += f"""
                    <div class="match-card" style="opacity: 0.6;">
                        <div class="league-title">{LEAGUE_MAP[league_id]}</div>
                        <div class="teams-title">{home_kr} vs {away_kr} <span style="font-size:0.7em; color:#888;">[{status}]</span></div>
                        <div style="text-align:center; color:#ff5252; padding: 20px 0;">⚠️ 이 경기는 아직 상세 스탯이 제공되지 않습니다.</div>
                    </div>
                    """
                    continue
                
                h_stats = stats_data[0]['statistics']
                a_stats = stats_data[1]['statistics']

                h_poss = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Ball Possession'), 0))
                h_shot = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Shots on Goal'), 0))
                a_poss = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Ball Possession'), 0))
                a_shot = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Shots on Goal'), 0))

                # AI 알고리즘
                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                
                win_pick = f"🟢 {home_kr} 승리 유력" if h_score > a_score + 2.5 else (f"🔵 {away_kr} 승리 유력" if a_score > h_score + 2.5 else "🟡 무승부 접전")
                control_pick = f"{home_kr} 주도" if h_poss > a_poss + 15 else (f"{away_kr} 주도" if a_poss > h_poss + 15 else "팽팽한 중원 싸움")
                total_shots = h_shot + a_shot
                over_under = "🔥 오버 (다득점 페이스)" if total_shots >= 9 else ("❄️ 언더 (저득점 늪축구)" if total_shots <= 5 else "⚖️ 언오버 팽팽")

                h_lineup = ", ".join([p['player']['name'] for p in lineup_data[0]['startXI']]) if lineup_data else "명단 미발표"
                a_lineup = ", ".join([p['player']['name'] for p in lineup_data[1]['startXI']]) if lineup_data and len(lineup_data) > 1 else "명단 미발표"

                # 🎨 예쁜 카드 HTML 조립
                html_cards += f"""
                <div class="match-card">
                    <div class="league-title">{LEAGUE_MAP[league_id]}</div>
                    <div class="teams-title">{home_kr} vs {away_kr} <span style="font-size:0.7em; color:#888;">[{status}]</span></div>
                    
                    <div class="stat-box">
                        <span style="color:#fff; font-weight:bold;">{home_kr}</span> : 점유율 {h_poss}% / 슈팅 {h_shot}개<br>
                        <span style="color:#fff; font-weight:bold;">{away_kr}</span> : 점유율 {a_poss}% / 슈팅 {a_shot}개
                    </div>
                    
                    <div class="ai-result">
                        🎯 {win_pick}<br>
                        ⚔️ {control_pick}<br>
                        📊 {over_under}
                    </div>
                    
                    <details>
                        <summary>▶ 선발 라인업 보기</summary>
                        <div class="lineup-box">
                            <strong>🏠 {home_kr}:</strong> {h_lineup}<br><br>
                            <strong>✈️ {away_kr}:</strong> {a_lineup}
                        </div>
                    </details>
                </div>
                """
        except Exception as e:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 모든 데이터 분석이 완료되었습니다!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    # 🎨 완성된 카드를 화면에 즉시 렌더링!
    if matches_found and html_cards:
        st.markdown(f'<div class="grid-container">{html_cards}</div>', unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align:center; color:#ff5252;'>해당 날짜에 선택한 리그의 경기가 없습니다.</h3>", unsafe_allow_html=True)
