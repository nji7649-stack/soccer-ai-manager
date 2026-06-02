import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 1. 다크 모드 전술판 스타일 (검정 배경 + 흰색 선수 동그라미 + 동일 크기)
custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #444; margin-bottom: 20px; }
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
.match-txt { color: #ffffff; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 10px; }
.stat-box { background-color: #2a2a2a; padding: 10px; border-radius: 8px; font-size: 13px; color: #ccc; }
.predict-txt { color: #00E676; font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 10px; margin-top: 10px; }
/* 전술판 크기 고정 (300px) */
.tactical-board { 
    background: #000000; border: 2px solid #555; border-radius: 8px; 
    padding: 10px; width: 300px; height: 350px; margin: 0 auto; display: flex; flex-direction: column; justify-content: space-between;
}
.player-dot { 
    background: #fff; color: #000; width: 28px; height: 28px; border-radius: 50%; 
    display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold; 
}
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

# 💡 선발 라인업 한글화 + 작전판 그리기
def draw_dark_tactical_board(team_name, lineup_info):
    if not lineup_info or 'startXI' not in lineup_info: return f"<div style='text-align:center; color:#888;'>{team_name} 명단 미발표</div>"
    
    board_html = "<div class='tactical-board'>"
    rows = {}
    for p in lineup_info['startXI']:
        grid = p.get('player', {}).get('grid', '1:1')
        name = translate_to_ko(p.get('player', {}).get('name', 'Unknown'))
        row_idx = int(grid.split(':')[0])
        if row_idx not in rows: rows[row_idx] = []
        rows[row_idx].append(name[:6]) # 이름 길이 제한
        
    for row_idx in sorted(rows.keys(), reverse=True):
        board_html += "<div style='display:flex; justify-content:space-evenly;'>"
        for p_name in rows[row_idx]:
            board_html += f"<div class='player-dot'>{p_name}</div>"
        board_html += "</div>"
    board_html += "</div>"
    return board_html

# 💡 승무패 결과 판정
def check_win(h_goal, a_goal, prediction):
    if h_goal > a_goal: actual = "홈 승"
    elif a_goal > h_goal: actual = "원정 승"
    else: actual = "무승부"
    
    if actual in prediction: return "🎯 적중!"
    else: return "❌ 미적중"

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 AI 축구 승부 예측 PRO</h1>", unsafe_allow_html=True)
st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())
selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", ["39", "140", "292"], default=["39", "140", "292"], format_func=lambda x: {"39":"프리미어리그","140":"라리가","292":"K리그1"}[x])

if st.sidebar.button("🚀 데이터 불러오기 및 AI 분석"):
    cols = st.columns(3)
    col_idx = 0
    url = "https://v3.football.api-sports.io/fixtures"
    
    for league_id in selected_leagues:
        fixtures = requests.get(url, headers=HEADERS, params={"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d')}).json().get('response', [])
        
        for match in fixtures:
            fix_id = str(match['fixture']['id'])
            h_name = translate_to_ko(match['teams']['home']['name'])
            a_name = translate_to_ko(match['teams']['away']['name'])
            status = match['fixture']['status']['short']
            
            # 예측 로직
            stats = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
            if not stats: continue
            
            h_shot = safe_num(next((i['value'] for i in stats[0]['statistics'] if i['type'] == 'Shots on Goal'), 0))
            a_shot = safe_num(next((i['value'] for i in stats[1]['statistics'] if i['type'] == 'Shots on Goal'), 0))
            pred = "홈 승" if h_shot > a_shot else ("원정 승" if a_shot > h_shot else "무승부")
            
            # 종료된 경기는 결과 표시
            result_str = ""
            if status in ['FT', 'AET', 'PEN']:
                h_goal = match['goals']['home']
                a_goal = match['goals']['away']
                hit = check_win(h_goal, a_goal, pred)
                result_str = f"🏁 최종: {h_goal}:{a_goal} ({hit})"
            
            lineup = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
            
            with cols[col_idx % 3]:
                st.markdown(f"""
                <div class='card-box'>
                    <div class='league-txt'>{LEAGUE_MAP[league_id]}</div>
                    <div class='match-txt'>{h_name} vs {a_name}</div>
                    <div class='predict-txt'>{pred} 예측 <br> {result_str}</div>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("▶ 전술판 및 라인업"):
                    st.markdown(draw_dark_tactical_board(h_name, lineup[0] if lineup else None), unsafe_allow_html=True)
                    st.markdown(draw_dark_tactical_board(a_name, lineup[1] if len(lineup)>1 else None), unsafe_allow_html=True)
            col_idx += 1
