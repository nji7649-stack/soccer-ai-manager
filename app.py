import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 감독님이 요청하신 오렌지색 채점 타이틀 및 네온 그린 3줄 해설 UI 최적화 CSS
custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px; line-height: 1.4; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 14px; line-height: 1.6; }
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
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 데이터 매치업 수집 중...")
        progress_bar.progress((idx) / total_leagues)
        
        querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            fixtures = res.get('response', [])
            
            for match in fixtures:
                fix_id = str(match['fixture']['id'])
                home_kr = translate_to_ko(match['teams']['home']['name'])
                away_kr = translate_to_ko(match['teams']['away']['name'])
                
                status_short = match['fixture']['status']['short']
                elapsed_time = match['fixture']['status']['elapsed']
                
                is_finished = status_short in ['FT', 'AET', 'PEN']
                is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P']
                is_pre_match = not is_finished and not is_live
                
                match_date_raw = match['fixture']['date']
                try:
                    time_str = datetime.strptime(match_date_raw[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M")
                except:
                    time_str = "시간미정"
                
                top_league_display = f"{LEAGUE_MAP[league_id]} ({time_str})"
                
                h_goal = match['goals']['home'] if match['goals']['home'] is not None else 0
                a_goal = match['goals']['away'] if match['goals']['away'] is not None else 0
                
                if is_finished:
                    match_display = f"{home_kr} <span style='color:#00E676; margin:0 10px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[종료됨]</div>"
                elif is_live:
                    live_label = "하프타임" if status_short == 'HT' else f"{elapsed_time}분 진행 중"
                    match_display = f"{home_kr} <span style='color:#ff9800; margin:0 10px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr} <div style='font-size:12px; color:#ff9800; margin-top:5px;'>🔊 LIVE ({live_label})</div>"
                else:
                    match_display = f"{home_kr} <span style='color:#888; font-size:16px; margin:0 10px;'>VS</span> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[경기 시작 전]</div>"

                pred_winner = "none"

                # 💡 경기 전 로직: 사전 예측 API 활용
                if is_pre_match:
                    pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    if pred_res:
                        pred = pred_res[0]['predictions']
                        h_pct = safe_num(pred['percent']['home'])
                        a_pct = safe_num(pred['percent']['away'])
                        
                        h_stat_str = f"예상 승률: {h_pct}%"
                        a_stat_str = f"예상 승률: {a_pct}%"
                        
                        if h_pct > a_pct + 10:
                            pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력 (사전예측)"
                        elif a_pct > h_pct + 10:
                            pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력 (사전예측)"
                        else:
                            pred_winner, win_pick = "draw", "🟡 무승부 접전 (사전예측)"
                            
                        control_pick = f"데이터 분석 승률: 홈 {h_pct}% / 원정 {a_pct}%"
                        under_over_val = pred.get('under_over', '')
                        over_under = f"🔥 예상 골 기준점: {under_over_val}" if under_over_val else "전술 및 라인업 분석 중"
                    else:
                        h_stat_str, a_stat_str = "데이터 대기 중", "데이터 대기 중"
                        win_pick = "⚖️ 실시간 데이터 수집 대기 중"
                        control_pick = "사전 데이터 확인 불가"
                        over_under = "양 팀 라인업 조율 중"
                
                # 💡 라이브 및 종료 경기 로직: 기존 실시간 스탯 알고리즘 활용
                else:
                    stats_data = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                    if not stats_data or len(stats_data) < 2:
                        h_stat_str, a_stat_str = "실시간 스탯 집계 중", "실시간 스탯 집계 중"
                        win_pick = "⚖️ 초반 탐색전 진행 중"
                        control_pick = "실시간 데이터 수집 중..."
                        over_under = "슈팅 데이터 대기 중"
                    else:
                        h_stats = stats_data[0]['statistics']
                        a_stats = stats_data[1]['statistics']
                        h_poss = safe_num(next((i['value'] for i in h_stats if i['type'] == 'Ball Possession'), 0))
                        h_shot = safe_num(next((i['value'] for i in h_stats if i['type'] == 'Shots on Goal'), 0))
                        a_poss = safe_num(next((i['value'] for i in a_stats if i['type'] == 'Ball Possession'), 0))
                        a_shot = safe_num(next((i['value'] for i in a_stats if i['type'] == 'Shots on Goal'), 0))

                        h_stat_str = f"점유율 {h_poss}% / 유효슈팅 {h_shot}개"
                        a_stat_str = f"점유율 {a_poss}% / 유효슈팅 {a_shot}개"

                        h_score = (h_poss * 0.1) + (h_shot * 1.5)
                        a_score = (a_poss * 0.1) + (a_shot * 1.5)
                        
                        if h_score > a_score + 2.5:
                            pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력"
                        elif a_score > h_score + 2.5:
                            pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력"
                        else:
                            pred_winner, win_pick = "draw", "🟡 무승부 접전"

                        control_pick = f"{home_kr} 주도" if h_poss > a_poss + 15 else (f"{away_kr} 주도" if a_poss > h_poss + 15 else "팽팽한 중원 싸움")
                        total_shots = h_shot + a_shot
                        over_under = "🔥 오버 (다득점 페이스)" if total_shots >= 9 else ("❄️ 언더 (저득점 늪축구)" if total_shots <= 5 else "⚖️ 언오버 팽팽")

                # 종료된 경기의 채점 마크 오렌지색 통일 연산
                if is_finished and pred_winner != "none":
                    if h_goal > a_goal: actual_winner = "home"
                    elif a_goal > h_goal: actual_winner = "away"
                    else: actual_winner = "draw"
                    
                    if actual_winner == pred_winner:
                        win_pick += " <span style='color:#ff9800;'>(적중)</span>"
                    else:
                        win_pick += " <span style='color:#ff9800;'>(미적중)</span>"

                new_html_list.append({
                    "league": top_league_display,
                    "match_display": match_display,
                    "h_kr": home_kr, "a_kr": away_kr,
                    "h_stat_str": h_stat_str, "a_stat_str": a_stat_str,
                    "win_pick": win_pick, "control_pick": control_pick, "over_under": over_under
                })
        except:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 하이브리드 엔진 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

# 💡 화면 출력 (모든 예측 텍스트가 초록색으로 렌더링 됨)
if st.session_state['analyzed_html_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_html_list']):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card-box">
                <div class="league-txt">{data['league']}</div>
                <div class="match-txt">{data['match_display']}</div>
                <div class="stat-bg">
                    <b style="color:#fff;">{data['h_kr']}</b> : {data['h_stat_str']}<br>
                    <b style="color:#fff;">{data['a_kr']}</b> : {data['a_stat_str']}
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
