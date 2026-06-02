import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 1. 완벽한 CSS (세 줄 모두 초록색 폰트 강제 적용)
custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 14px; line-height: 1.6; }
/* 💡 여기서부터 예측 텍스트 영역: 모든 글씨를 초록색(#00E676)으로 통일! */
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

/* 다크모드 전술판 디자인 */
.tactical-board {
    background-color: #0a0a0a; border: 2px solid #333; border-radius: 8px;
    width: 100%; max-width: 320px; height: 350px; margin: 0 auto 10px auto;
    display: flex; flex-direction: column; justify-content: space-around; padding: 10px 0;
}
.player-wrapper { display: flex; flex-direction: column; align-items: center; }
.player-dot {
    background-color: #ffffff; color: #000000; width: 28px; height: 28px;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: bold; box-shadow: 0 0 5px rgba(255,255,255,0.3);
}
.player-name-label { color: #ffffff; font-size: 11px; text-align: center; margin-top: 4px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

API_KEY = st.secrets["FOOTBALL_API_KEY"]
HEADERS = {'x-apisports-key': API_KEY}

# 팀 이름만 번역
@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    try: return GoogleTranslator(source='en', target='ko').translate(text)
    except: return text

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

# 💡 고속 렌더링 작전판 (영문 이름 추출 로직 수정)
def draw_dark_tactical_board(team_name, lineup_info):
    if not lineup_info or 'startXI' not in lineup_info:
        return f"<div style='text-align:center; color:#888; padding:10px;'>{team_name} 명단 미발표</div>"
    
    formation = lineup_info.get('formation', '포메이션 미정')
    startXI = lineup_info['startXI']
    
    rows = {}
    for p in startXI:
        grid = p.get('player', {}).get('grid')
        if not grid: grid = '1:1' # 좌표가 없는 경우 예외 처리
            
        name = p.get('player', {}).get('name', 'Unknown')
        short_name = name.split()[-1][:8] # 성씨만 추출
        initial = short_name[0] if short_name else "X"
        
        row_idx = int(grid.split(':')[0])
        if row_idx not in rows: rows[row_idx] = []
        rows[row_idx].append((initial, short_name))
        
    board_html = f"<div style='text-align:center; color: #aaa; font-weight: bold; margin-bottom: 5px; font-size:13px;'>{team_name} <span style='color:#fff;'>({formation})</span></div>"
    board_html += "<div class='tactical-board'>"
    
    for row_idx in sorted(rows.keys(), reverse=True):
        players = rows[row_idx]
        board_html += "<div style='display: flex; justify-content: space-evenly; width: 100%;'>"
        for initial, full_name in players:
            board_html += f"""
            <div class='player-wrapper'>
                <div class='player-dot'>{initial}</div>
                <div class='player-name-label'>{full_name}</div>
            </div>
            """
        board_html += "</div>"
    board_html += "</div>"
    return board_html

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
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 분석 중... ({idx+1}/{total_leagues})")
        progress_bar.progress((idx) / total_leagues)
        
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
                
                stats_data = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
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

                # 💡 종료된 경기일 경우, 예측 결과 바로 옆에 괄호로 적중 여부 표시
                if is_finished:
                    h_goal = match['goals']['home']
                    a_goal = match['goals']['away']
                    match_display = f"{home_kr} <span style='color:#00E676; margin:0 15px; font-size:26px;'>{h_goal} : {a_goal}</span> {away_kr}"
                    
                    if h_goal > a_goal: actual_winner = "home"
                    elif a_goal > h_goal: actual_winner = "away"
                    else: actual_winner = "draw"
                    
                    if actual_winner == pred_winner:
                        win_pick += " (적중)"
                    else:
                        win_pick += " (미적중)"
                else:
                    match_display = f"{home_kr} <br> <span style='color:#888; font-size:16px;'>vs</span> <br> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[{status}]</div>"

                control_pick = f"{home_kr} 주도" if h_poss > a_poss + 15 else (f"{away_kr} 주도" if a_poss > h_poss + 15 else "팽팽한 중원 싸움")
                total_shots = h_shot + a_shot
                over_under = "🔥 오버 (다득점 페이스)" if total_shots >= 9 else ("❄️ 언더 (저득점 늪축구)" if total_shots <= 5 else "⚖️ 언오버 팽팽")

                # 작전판 생성
                h_pitch = draw_dark_tactical_board(home_kr, lineup_data[0] if lineup_data else None)
                a_pitch = draw_dark_tactical_board(away_kr, lineup_data[1] if lineup_data and len(lineup_data)>1 else None)

                new_html_list.append({
                    "league": LEAGUE_MAP[league_id],
                    "match_display": match_display,
                    "h_kr": home_kr, "a_kr": away_kr,
                    "h_poss": h_poss, "h_shot": h_shot, "a_poss": a_poss, "a_shot": a_shot,
                    "win_pick": win_pick, "control_pick": control_pick, "over_under": over_under,
                    "h_pitch": h_pitch, "a_pitch": a_pitch
                })
        except:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 초고속 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

# 💡 화면 출력 (모든 예측 텍스트가 CSS에 의해 초록색으로 나옵니다)
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
            
            with st.expander("▶ 다크모드 전술판 및 라인업 보기"):
                st.markdown(data['h_pitch'], unsafe_allow_html=True)
                st.markdown(data['a_pitch'], unsafe_allow_html=True)
elif st.session_state['analyzed_html_list'] == []:
    st.markdown("")
