import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 기본 디자인 세팅 및 다크모드 전술판 크기 고정 CSS
st.markdown("""
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 10px;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 14px; line-height: 1.6; }
.predict-txt { color: #00E676; font-size: 16px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; margin-top: 15px; line-height: 1.6; }

/* 💡 다크모드 전술판 강제 크기 고정 클래스 */
.dark-tactical-board {
    border: 2px solid #333; 
    border-radius: 8px; 
    background: #0a0a0a; /* 아주 어두운 검정 바탕 */
    padding: 10px; 
    margin-bottom: 10px;
    height: 380px; /* 💡 높이 강제 고정 */
    display: flex;
    flex-direction: column;
    justify-content: space-around; /* 포메이션 간격 균등 분배 */
}
</style>
""", unsafe_allow_html=True)

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

# 💡 개선된 함수: 다크모드 전술판 그리기 (크기 고정 + 흰/검 블록)
def draw_dark_tactical_board(team_name, lineup_info):
    if not lineup_info or 'startXI' not in lineup_info:
        return f"<div style='text-align:center; color:#888; padding:10px; height: 380px; display:flex; align-items:center; justify-content:center;'>{team_name} 명단 미발표</div>"
    
    formation = lineup_info.get('formation', '포메이션 미정')
    startXI = lineup_info['startXI']
    
    rows = {}
    for p in startXI:
        grid = p.get('player', {}).get('grid')
        name = p.get('player', {}).get('name', 'Unknown')
        short_name = name.split()[-1][:8] 
        
        row_idx = int(grid.split(':')[0]) if grid else 0
        if row_idx not in rows: rows[row_idx] = []
        rows[row_idx].append(short_name)
        
    board_html = f"<div style='text-align:center; color: #aaa; font-weight: bold; margin-bottom: 10px; font-size:13px;'>{team_name} <span style='color:#fff;'>({formation})</span></div>"
    board_html += f"<div class='dark-tactical-board'>"
    
    for row_idx in sorted(rows.keys(), reverse=True):
        players = rows[row_idx]
        board_html += "<div style='display: flex; justify-content: space-evenly; width: 100%;'>"
        for player in players:
            # 💡 다크모드 맞춤형 선수 블록 (흰색 바탕, 검정 글씨, 둥근 디자인)
            board_html += f"<div style='background: #ffffff; color: #000000; padding: 6px 10px; border-radius: 15px; font-size: 11px; font-weight:bold; white-space: nowrap; box-shadow: 0 0 5px rgba(255,255,255,0.3);'>{player}</div>"
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

# 세션 초기화
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
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 데이터 분석 중... ({idx+1}/{total_leagues})")
        progress_bar.progress((idx) / total_leagues)
        
        querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            fixtures = res.get('response', [])
            
            for match in fixtures:
                fix_id = str(match['fixture']['id'])
                home_en = match['teams']['home']['name']
                away_en = match['teams']['away']['name']
                
                # 팀 이름 캐시 번역
                home_kr = translate_to_ko(home_en)
                away_kr = translate_to_ko(away_en)
                
                status = match['fixture']['status']['short']
                is_finished = status in ['FT', 'AET', 'PEN']
                
                if is_finished:
                    h_goal = match['goals']['home']
                    a_goal = match['goals']['away']
                    score_html = f"<span style='font-size:26px; color:#00E676; margin: 0 15px;'>{h_goal} : {a_goal}</span>"
                    match_display = f"{home_kr} <br> {score_html} <br> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[종료됨]</div>"
                else:
                    match_display = f"{home_kr} <br> <span style='font-size:16px; color:#888;'>vs</span> <br> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[{status}]</div>"

                stats_data = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not stats_data or len(stats_data) < 2:
                    continue 
                
                # 💡 감독님이 가장 선호하시는 실시간 스탯(점유율+슈팅) 알고리즘
                h_stats = stats_data[0]['statistics']
                a_stats = stats_data[1]['statistics']

                h_poss = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Ball Possession'), 0))
                h_shot = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Shots on Goal'), 0))
                a_poss = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Ball Possession'), 0))
                a_shot = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Shots on Goal'), 0))

                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                
                if h_score > a_score + 2.5:
                    pred_winner = "home"
                    win_pick = f"🟢 {home_kr} 승리 유력"
                elif a_score > h_score + 2.5:
                    pred_winner = "away"
                    win_pick = f"🔵 {away_kr} 승리 유력"
                else:
                    pred_winner = "draw"
                    win_pick = "🟡 무승부 접전"
                
                # 적중 채점
                if is_finished:
                    if h_goal > a_goal: actual_winner = "home"
                    elif a_goal > h_goal: actual_winner = "away"
                    else: actual_winner = "draw"
                    
                    if actual_winner == pred_winner:
                        win_pick += " <span style='color:#ff9800; font-size:15px;'>(적중)</span>"
                    else:
                        win_pick += " <span style='color:#ff9800; font-size:15px;'>(미적중)</span>"

                control_pick = f"{home_kr} 주도" if h_poss > a_poss + 15 else (f"{away_kr} 주도" if a_poss > h_poss + 15 else "팽팽한 중원 싸움")
                total_shots = h_shot + a_shot
                over_under = "🔥 오버 (다득점 페이스)" if total_shots >= 9 else ("❄️ 언더 (저득점 늪축구)" if total_shots <= 5 else "⚖️ 언오버 팽팽")

                # 💡 다크모드 전술판 렌더링 호출
                h_pitch = draw_dark_tactical_board(home_kr, lineup_data[0] if lineup_data else None)
                a_pitch = draw_dark_tactical_board(away_kr, lineup_data[1] if lineup_data and len(lineup_data)>1 else None)

                # 데이터를 딕셔너리로 저장 (HTML 구조 꼬임 방지)
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
    status_text.text("✅ 모든 데이터 분석이 완료되었습니다!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

# 💡 화면 출력 로직 (HTML 들여쓰기 에러 원천 차단)
if st.session_state['analyzed_html_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_html_list']):
        
        # 1. 윗부분 카드 생성
        html_str = "<div class='card-box'>"
        html_str += f"<div class='league-txt'>{data['league']}</div>"
        html_str += f"<div class='match-txt'>{data['match_display']}</div>"
        html_str += f"<div class='stat-bg'><b style='color:#fff;'>{data['h_kr']}</b> : 점유율 {data['h_poss']}% / 슈팅 {data['h_shot']}개<br>"
        html_str += f"<b style='color:#fff;'>{data['a_kr']}</b> : 점유율 {data['a_poss']}% / 슈팅 {data['a_shot']}개</div>"
        html_str += f"<div class='predict-txt'>🎯 {data['win_pick']}<br>"
        html_str += f"<span style='font-size: 15px; font-weight: bold; color: #00E676;'>"
        html_str += f"⚔️ {data['control_pick']}<br>📊 {data['over_under']}</span></div></div>"
        
        with cols[idx % 3]:
            st.markdown(html_str, unsafe_allow_html=True)
            
            # 2. 전술판 메뉴 (안전하게 스트림릿 네이티브 기능 사용)
            with st.expander("▶ 다크모드 전술판 및 라인업"):
                st.markdown(data['h_pitch'], unsafe_allow_html=True)
                st.markdown(data['a_pitch'], unsafe_allow_html=True)
elif st.session_state['analyzed_html_list'] == []:
    st.markdown("")
