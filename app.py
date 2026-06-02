import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 기본 디자인 세팅
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

# 💡 핵심 무기: 라인업 데이터를 받아서 초록색 전술판(미니 축구장)을 그리는 함수
def draw_tactical_board(team_name, lineup_info, shirt_color):
    if not lineup_info or 'startXI' not in lineup_info:
        return f"<div style='text-align:center; color:#888; padding:10px;'>{team_name} 명단 미발표</div>"
    
    formation = lineup_info.get('formation', '포메이션 미정')
    startXI = lineup_info['startXI']
    
    # 선수들의 포지션 좌표(Grid)를 층별로 묶기
    rows = {}
    for p in startXI:
        grid = p.get('player', {}).get('grid')
        name = p.get('player', {}).get('name', 'Unknown')
        short_name = name.split()[-1][:8] # 이름이 길면 카드 밖으로 나가므로 자르기
        
        row_idx = int(grid.split(':')[0]) if grid else 0
        if row_idx not in rows: rows[row_idx] = []
        rows[row_idx].append(short_name)
        
    # 축구장(초록 잔디) HTML 그리기
    board_html = f"<div style='border: 2px solid rgba(255,255,255,0.2); border-radius: 8px; background: #1b4d24; padding: 10px; margin-bottom: 10px;'>"
    board_html += f"<div style='text-align:center; color: #a5d6a7; font-weight: bold; margin-bottom: 15px; font-size:13px;'>{team_name} <span style='color:#fff;'>({formation})</span></div>"
    
    # 공격수(맨 앞)부터 골키퍼(맨 뒤) 순서로 출력하기 위해 역순 정렬
    for row_idx in sorted(rows.keys(), reverse=True):
        players = rows[row_idx]
        board_html += "<div style='display: flex; justify-content: space-evenly; margin-bottom: 10px;'>"
        for player in players:
            # 유니폼을 입은 선수 블록
            board_html += f"<div style='background: {shirt_color}; color: #fff; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight:bold; white-space: nowrap; box-shadow: 1px 1px 3px rgba(0,0,0,0.6);'>{player}</div>"
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

if st.sidebar.button("🚀 데이터 불러오기 및 AI 분석"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    matches_found = False
    total_leagues = len(selected_leagues)
    
    cols = st.columns(3)
    col_idx = 0
    
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
                is_finished = status in ['FT', 'AET', 'PEN']
                
                # 💡 스코어 결과 연동 로직
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
                
                h_stats = stats_data[0]['statistics']
                a_stats = stats_data[1]['statistics']

                h_poss = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Ball Possession'), 0))
                h_shot = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Shots on Goal'), 0))
                a_poss = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Ball Possession'), 0))
                a_shot = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Shots on Goal'), 0))

                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                
                win_pick = f"🟢 {home_kr} 승리 유력" if h_score > a_score + 2.5 else (f"🔵 {away_kr} 승리 유력" if a_score > h_score + 2.5 else "🟡 무승부 접전")
                control_pick = f"{home_kr} 주도" if h_poss > a_poss + 15 else (f"{away_kr} 주도" if a_poss > h_poss + 15 else "팽팽한 중원 싸움")
                total_shots = h_shot + a_shot
                over_under = "🔥 오버 (다득점 페이스)" if total_shots >= 9 else ("❄️ 언더 (저득점 늪축구)" if total_shots <= 5 else "⚖️ 언오버 팽팽")

                # 💡 전술판 렌더링 (홈팀: 파란색 유니폼 / 원정팀: 빨간색 유니폼 세팅)
                h_pitch_html = draw_tactical_board(home_kr, lineup_data[0] if lineup_data else None, "#1565c0")
                a_pitch_html = draw_tactical_board(away_kr, lineup_data[1] if lineup_data and len(lineup_data)>1 else None, "#c62828")

                with cols[col_idx % 3]:
                    card_html = f"""
                    <div class="card-box">
                        <div class="league-txt">{LEAGUE_MAP[league_id]}</div>
                        <div class="match-txt">{match_display}</div>
                        <div class="stat-bg">
                            <b style="color:#fff;">{home_kr}</b> : 점유율 {h_poss}% / 슈팅 {h_shot}개<br>
                            <b style="color:#fff;">{away_kr}</b> : 점유율 {a_poss}% / 슈팅 {a_shot}개
                        </div>
                        <div class="predict-txt">
                            🎯 {win_pick}<br>
                            ⚔️ {control_pick}<br>
                            📊 {over_under}
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # 스트림릿 순정 아코디언 안에 전술판 HTML 꽂아넣기
                    with st.expander("▶ 전술판 및 선발 라인업 보기"):
                        st.markdown(h_pitch_html, unsafe_allow_html=True)
                        st.markdown(a_pitch_html, unsafe_allow_html=True)
                    
                    st.write("") 
                col_idx += 1

        except Exception as e:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 모든 데이터 분석이 완료되었습니다!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    if not matches_found:
        st.error("해당 날짜에 분석 가능한 데이터가 없습니다.")
