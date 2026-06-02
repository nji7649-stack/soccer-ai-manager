import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 감독님이 원하시던 시그니처 다크모드 및 초록색 텍스트 UI 고정 CSS
custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
}
/* 리그 정보 및 경기 시간 텍스트 (오렌지색) */
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 14px; line-height: 1.6; }

/* 💡 핵심 요구사항: 승부예측, 해설, 언오버 세 줄 모두 동일한 초록색 볼드체 적용 */
.predict-txt { 
    color: #00E676; 
    font-size: 16px; 
    font-weight: bold; 
    text-align: center; 
    border-top: 1px dashed #555; 
    padding-top: 15px; 
    margin-top: 15px; 
    line-height: 1.6; 
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

API_KEY = st.secrets["FOOTBALL_API_KEY"]
HEADERS = {'x-apisports-key': API_KEY}

# 팀 이름만 번역 (캐시 적용)
@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    try: return GoogleTranslator(source='en', target='ko').translate(text)
    except: return text

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 라이브 AI 축구 승부 예측 PRO</h1>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())

LEAGUE_MAP = {
    "1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", 
    "140": "라리가", "135": "세리에A", "78": "분데스리가", 
    "61": "리그1", "292": "K리그1"
}

selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["39", "140", "292"])

if 'analyzed_html_list' not in st.session_state:
    st.session_state['analyzed_html_list'] = []

if st.sidebar.button("🚀 데이터 불러오기 및 AI 분석"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_leagues = len(selected_leagues)
    new_html_list = []
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 분석 중...")
        progress_bar.progress((idx) / total_leagues)
        
        # 💡 유료 버전이므로 timezone을 Asia/Seoul로 설정하여 정확한 한국 시각 수신
        querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            fixtures = res.get('response', [])
            
            for match in fixtures:
                fix_id = str(match['fixture']['id'])
                home_kr = translate_to_ko(match['teams']['home']['name'])
                away_kr = translate_to_ko(match['teams']['away']['name'])
                
                status = match['fixture']['status']['short']
                is_finished = status in ['FT', 'AET', 'PEN']
                
                # 💡 한국 시간 경기 시작 시간 추출 (예: "2026-06-03T21:00:00+09:00" -> "21:00")
                match_date_raw = match['fixture']['date']
                try:
                    match_time_obj = datetime.strptime(match_date_raw[:16], "%Y-%m-%dT%H:%M")
                    time_str = match_time_obj.strftime("%H:%M")
                except:
                    time_str = "시간 미정"
                
                # 💡 상단 리그 텍스트를 "A매치 친선경기(경기시간)" 형태로 조합
                top_league_display = f"{LEAGUE_MAP[league_id]} ({time_str})"
                
                stats_data = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not stats_data or len(stats_data) < 2: continue
                
                h_stats = stats_data[0]['statistics']
                a_stats = stats_data[1]['statistics']

                h_poss = safe_num(next((i['value'] for i in h_stats if i['type'] == 'Ball Possession'), 0))
                h_shot = safe_num(next((i['value'] for i in h_stats if i['type'] == 'Shots on Goal'), 0))
                a_poss = safe_num(next((i['value'] for i in a_stats if i['type'] == 'Ball Possession'), 0))
                a_shot = safe_num(next((i['value'] for i in a_stats if i['type'] == 'Shots on Goal'), 0))

                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                
                if h_score > a_score + 2.5:
                    pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력"
                elif a_score > h_score + 2.5:
                    pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력"
                else:
                    pred_winner, win_pick = "draw", "🟡 무승부 접전"

                # 💡 적중 마크는 줄바꿈 없이 승리 유력 바로 옆에 붙이고 색상을 오렌지색(#ff9800)으로 강제 매핑
                if is_finished:
                    h_goal = match['goals']['home']
                    a_goal = match['goals']['away']
                    match_display = f"{home_kr} <span style='color:#00E676; margin:0 15px; font-size:26px;'>{h_goal} : {a_goal}</span> {away_kr}"
                    
                    if h_goal > a_goal: actual_winner = "home"
                    elif a_goal > h_goal: actual_winner = "away"
                    else: actual_winner = "draw"
                    
                    if actual_winner == pred_winner:
                        win_pick += " <span style='color:#ff9800; font-size:16px;'>(적중)</span>"
                    else:
                        win_pick += " <span style='color:#ff9800; font-size:16px;'>(미적중)</span>"
                else:
                    match_display = f"{home_kr} <br> <span style='color:#888; font-size:16px;'>vs</span> <br> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[{status}]</div>"

                control_pick = f"{home_kr} 주도" if h_poss > a_poss + 15 else (f"{away_kr} 주도" if a_poss > h_poss + 15 else "팽팽한 중원 싸움")
                total_shots = h_shot + a_shot
                over_under = "🔥 오버 (다득점 페이스)" if total_shots >= 9 else ("❄️ 언더 (저득점 늪축구)" if total_shots <= 5 else "⚖️ 언오버 팽팽")

                new_html_list.append({
                    "league": top_league_display,
                    "match_display": match_display,
                    "h_kr": home_kr, "a_kr": away_kr,
                    "h_poss": h_poss, "h_shot": h_shot, "a_poss": a_poss, "a_shot": a_shot,
                    "win_pick": win_pick, "control_pick": control_pick, "over_under": over_under
                })
        except:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

# 💡 화면 출력 (불필요한 expander/전술판 전면 제거)
if st.session_state['analyzed_html_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_html_list']):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card-box">
                <div class="league-txt">{data['league']}</div>
                <div class="match-txt">{data['match_display']}</div>
                <div class="stat-bg">
                    <b style="color:#fff;">{data['h_kr']}</b> : 점유율 {data['h_poss']}% / 슈팅 {data['h_shot']}개<br>
                    <b style="color:#fff;">{data['a_kr']}</b> : 점유율 {data['a_poss']}% / 슈팅 {data['a_shot']}개
                </div>
                <div class="predict-txt">
                    🎯 {data['win_pick']}<br>
                    ⚔️ {data['control_pick']}<br>
                    📊 {data['over_under']}
                </div>
            </div>
            """, unsafe_allow_html=True)
elif st.session_state['analyzed_html_list'] == []:
    st.markdown("")
