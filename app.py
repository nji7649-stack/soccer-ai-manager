import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 UI 고정 CSS (박스 크기 고정 및 다크모드 전술판)
custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
    min-height: 400px; display: flex; flex-direction: column; justify-content: space-between;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; text-align: center; }
.match-txt { color: #ffffff; font-size: 19px; font-weight: bold; text-align: center; margin-bottom: 10px; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 13.5px; line-height: 1.7; text-align: center; margin-bottom: 10px;}
.predict-txt { color: #00E676; font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; line-height: 1.6; }

/* 다크모드 전술판 강제 크기 고정 */
.dark-tactical-board {
    border: 2px solid #333; border-radius: 8px; background: #0a0a0a; padding: 10px; 
    margin-bottom: 10px; height: 350px; display: flex; flex-direction: column; justify-content: space-around;
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
    if not value or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except: return 0.0

def safe_text(value):
    if not value or str(value).strip() == "": return "N/A"
    return str(value)

# 💡 다크모드 전술판 렌더링 함수
def draw_dark_tactical_board(team_name, lineup_info):
    if not lineup_info or 'startXI' not in lineup_info:
        return f"<div style='text-align:center; color:#888; padding:10px; height:350px; display:flex; align-items:center; justify-content:center; background:#0a0a0a; border: 2px solid #333; border-radius: 8px;'>{team_name} 명단 미발표</div>"
    
    formation = lineup_info.get('formation', '포메이션 미정')
    startXI = lineup_info['startXI']
    
    rows = {}
    for p in startXI:
        grid = p.get('player', {}).get('grid')
        if not grid: grid = '1:1'
        name = p.get('player', {}).get('name', 'Unknown')
        short_name = name.split()[-1][:8] 
        
        row_idx = int(grid.split(':')[0])
        if row_idx not in rows: rows[row_idx] = []
        rows[row_idx].append(short_name)
        
    board_html = f"<div style='text-align:center; color: #aaa; font-weight: bold; margin-bottom: 5px; font-size:13px;'>{team_name} <span style='color:#fff;'>({formation})</span></div>"
    board_html += f"<div class='dark-tactical-board'>"
    
    for row_idx in sorted(rows.keys(), reverse=True):
        players = rows[row_idx]
        board_html += "<div style='display: flex; justify-content: space-evenly; width: 100%;'>"
        for player in players:
            board_html += f"<div style='background: #ffffff; color: #000000; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight:bold; white-space: nowrap; box-shadow: 0 0 5px rgba(255,255,255,0.3);'>{player}</div>"
        board_html += "</div>"
    board_html += "</div>"
    return board_html

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 궁극의 하이브리드 예측 (배당+상대전적+폼)</h1>", unsafe_allow_html=True)
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

if st.sidebar.button("🚀 배당 기반 하이브리드 분석 시작"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_leagues = len(selected_leagues)
    new_html_list = []
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 해외 배당 및 전력 데이터 수집 중... ({idx+1}/{total_leagues})")
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
                is_finished = status_short in ['FT', 'AET', 'PEN']
                is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P']
                
                try: match_time = datetime.strptime(match['fixture']['date'][:16], "%Y-%m-%dT%H:%M").strftime("%H:%M")
                except: match_time = "시간미정"
                top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time})"
                
                h_goal = match['goals']['home'] if match['goals']['home'] is not None else 0
                a_goal = match['goals']['away'] if match['goals']['away'] is not None else 0
                
                if is_finished:
                    match_display = f"{home_kr} <span style='color:#00E676; margin:0 15px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr}"
                elif is_live:
                    match_display = f"{home_kr} <span style='color:#ff9800; margin:0 15px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr}"
                else:
                    match_display = f"{home_kr} <span style='color:#888; font-size:16px; margin:0 15px;'>VS</span> {away_kr}"

                # 💡 핵심 1: Predictions API 호출 (상대 전적, 폼)
                pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                # 💡 핵심 2: Odds API 호출 (실제 해외 배당률)
                odds_res = requests.get("https://v3.football.api-sports.io/odds", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not pred_res: continue
                
                pred_data = pred_res[0]
                comparison = pred_data.get('comparison', {})
                
                # 상대전적(H2H) 및 최근 폼(Form)
                form_h = safe_text(comparison.get('form', {}).get('home'))
                form_a = safe_text(comparison.get('form', {}).get('away'))
                h2h_h = safe_text(comparison.get('h2h', {}).get('home'))
                h2h_a = safe_text(comparison.get('h2h', {}).get('away'))

                # 배당률(Odds) 파싱 로직
                odds_h, odds_d, odds_a = 0.0, 0.0, 0.0
                if odds_res:
                    bookmakers = odds_res[0].get('bookmakers', [])
                    if bookmakers:
                        bets = bookmakers[0].get('bets', [])
                        for bet in bets:
                            if bet['name'] == 'Match Winner': # 승무패 배당
                                for val in bet['values']:
                                    if str(val['value']) == 'Home': odds_h = float(val['odd'])
                                    elif str(val['value']) == 'Draw': odds_d = float(val['odd'])
                                    elif str(val['value']) == 'Away': odds_a = float(val['odd'])
                                break
                
                # 💡 딥러닝 + 배당 하이브리드 예측 로직
                # 배당이 있으면 배당 기반 우선 판단, 없으면 API AI 확률 사용
                pred_winner = "none"
                if odds_h > 0 and odds_a > 0:
                    # 배당이 낮을수록 승리 확률이 높음
                    if odds_h < odds_a - 0.3: # 홈이 확실한 정배
                        pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력 (정배당)"
                    elif odds_a < odds_h - 0.3: # 원정이 확실한 정배
                        pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력 (정배당)"
                    else: # 배당 차이가 0.3 이하일 때 -> 상대 전적(H2H)과 폼(Form)으로 타이브레이커
                        if safe_num(h2h_h) > safe_num(h2h_a) or safe_num(form_h) > safe_num(form_a):
                            pred_winner, win_pick = "home", f"🟢 {home_kr} 약우세 (전적/폼 반영)"
                        elif safe_num(h2h_a) > safe_num(h2h_h) or safe_num(form_a) > safe_num(form_h):
                            pred_winner, win_pick = "away", f"🔵 {away_kr} 약우세 (전적/폼 반영)"
                        else:
                            pred_winner, win_pick = "draw", "🟡 초박빙 무승부 (배당/전적 동률)"
                else:
                    # 배당이 아직 안 뜬 경기는 상대 전적(H2H)과 최근 폼(Form)만으로 분석
                    if safe_num(h2h_h) > safe_num(h2h_a): pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 우세 (상대전적 우위)"
                    elif safe_num(h2h_a) > safe_num(h2h_h): pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 우세 (상대전적 우위)"
                    else: pred_winner, win_pick = "none", "⚠️ 데이터 수집 불가 (분석 패스)"

                # 종료 경기 채점
                if is_finished and pred_winner != "none":
                    if h_goal > a_goal: actual = "home"
                    elif a_goal > h_goal: actual = "away"
                    else: actual = "draw"
                    win_pick += " <span style='color:#ff9800;'>(적중)</span>" if actual == pred_winner else " <span style='color:#ff5252;'>(미적중)</span>"
                        
                # UI 데이터 조합
                odds_text = f"<b style='color:#ff9800;'>{odds_h}</b> | 무 <b>{odds_d}</b> | 원정 <b style='color:#ff9800;'>{odds_a}</b>" if odds_h > 0 else "해외 배당 발매 전"
                
                stat_box = f"<span style='color:#aaa;'>해외 배당:</span> 홈 {odds_text}<br>"
                stat_box += f"<span style='color:#aaa;'>상대 전적:</span> {home_kr} <b>{h2h_h}</b> vs <b>{h2h_a}</b> {away_kr}<br>"
                stat_box += f"<span style='color:#aaa;'>최근 폼:</span> {home_kr} <b>{form_h}</b> vs <b>{form_a}</b> {away_kr}"

                # 전문가 코멘트 및 오버/언더
                advice = translate_to_ko(pred_data['predictions'].get('advice', '데이터 분석 중'))
                control_pick = f"🧠 AI: {advice}"
                
                under_over_val = pred_data['predictions'].get('under_over', '')
                if under_over_val:
                    uo_text = "언더 (저득점)" if "-" in under_over_val else "오버 (다득점)"
                    clean_val = under_over_val.replace('-', '').replace('+', '')
                    over_under = f"🔥 기준점 {clean_val} {uo_text}"
                else:
                    over_under = "🔥 기준점 산정 중"

                # 다크모드 전술판 렌더링
                h_pitch_html = draw_dark_tactical_board(home_kr, lineup_data[0] if lineup_data else None)
                a_pitch_html = draw_dark_tactical_board(away_kr, lineup_data[1] if lineup_data and len(lineup_data)>1 else None)

                new_html_list.append({
                    "league": top_league_display,
                    "match_display": match_display,
                    "stat_box": stat_box,
                    "win_pick": win_pick, 
                    "control_pick": control_pick, 
                    "over_under": over_under,
                    "h_pitch": h_pitch_html,
                    "a_pitch": a_pitch_html
                })
        except:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 하이브리드 엔진 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

# 화면 출력 (들여쓰기 에러 완벽 차단)
if st.session_state['analyzed_html_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_html_list']):
        html_str = "<div class='card-box'>"
        html_str += f"<div class='league-txt'>{data['league']}</div>"
        html_str += f"<div class='match-txt'>{data['match_display']}</div>"
        html_str += f"<div class='stat-bg'>{data['stat_box']}</div>"
        html_str += f"<div class='predict-txt'>🎯 {data['win_pick']}<br>"
        html_str += f"<span style='font-size: 14px; font-weight: normal; color: #00E676;'>"
        html_str += f"⚔️ {data['control_pick']}<br>{data['over_under']}</span></div></div>"
        
        with cols[idx % 3]:
            st.markdown(html_str, unsafe_allow_html=True)
            
            with st.expander("▶ 다크모드 전술판 및 라인업"):
                st.markdown(data['h_pitch'], unsafe_allow_html=True)
                st.markdown(data['a_pitch'], unsafe_allow_html=True)
            
            st.write("")
elif st.session_state['analyzed_html_list'] == []:
    st.markdown("")
