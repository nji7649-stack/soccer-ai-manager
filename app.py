import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 카드 크기 고정 및 다크모드 전술판 CSS
st.markdown("""
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
    min-height: 380px; display: flex; flex-direction: column; justify-content: space-between;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; text-align: center;}
.match-txt { color: #ffffff; font-size: 19px; font-weight: bold; text-align: center; margin-bottom: 10px; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 13px; line-height: 1.6; text-align: center; margin-bottom: 10px;}
.predict-txt { color: #00E676; font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; line-height: 1.6; }

/* 다크모드 전술판 강제 크기 고정 */
.dark-tactical-board {
    border: 2px solid #333; border-radius: 8px; background: #0a0a0a; padding: 10px; 
    margin-bottom: 10px; height: 350px; display: flex; flex-direction: column; justify-content: space-around;
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

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 AI 승부 예측 PRO (스쿼드 가치 기반)</h1>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())

LEAGUE_MAP = {
    "1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", 
    "140": "라리가", "135": "세리에A", "78": "분데스리가", 
    "61": "리그1", "292": "K리그1"
}

selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["10", "39"])

if 'analyzed_html_list' not in st.session_state:
    st.session_state['analyzed_html_list'] = []

if st.sidebar.button("🚀 정밀 데이터 분석 시작"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_leagues = len(selected_leagues)
    new_html_list = []
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 스쿼드 지표 분석 중... ({idx+1}/{total_leagues})")
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

                # 💡 핵심: 멍청한 단순 스탯을 버리고 Predictions(스쿼드 전력 예측) API 호출
                pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not pred_res: continue
                
                pred_data = pred_res[0]
                preds = pred_data.get('predictions', {})
                comparison = pred_data.get('comparison', {})
                
                # 빅데이터 전력 수치 (폼, 공격력, 수비력)
                form_h = safe_text(comparison.get('form', {}).get('home'))
                form_a = safe_text(comparison.get('form', {}).get('away'))
                att_h = safe_text(comparison.get('att', {}).get('home'))
                att_a = safe_text(comparison.get('att', {}).get('away'))
                
                h_pct = safe_num(preds.get('percent', {}).get('home'))
                a_pct = safe_num(preds.get('percent', {}).get('away'))
                d_pct = safe_num(preds.get('percent', {}).get('draw'))
                
                # 💡 타이브레이커: 50 vs 50 동률일 경우 폼(Form) 지표로 승패 강제 결정
                form_h_val = safe_num(form_h)
                form_a_val = safe_num(form_a)
                if h_pct == a_pct and h_pct > 0:
                    if form_h_val > form_a_val: h_pct += 1
                    elif form_a_val > form_h_val: a_pct += 1

                # 픽 결정 로직
                if h_pct == 0 and a_pct == 0:
                    pred_winner, win_pick = "none", "⚠️ 데이터 수집 불가 (분석 패스)"
                elif h_pct > a_pct:
                    pred_winner, win_pick = "home", f"🟢 {home_kr} 우세 ({h_pct}%)"
                elif a_pct > h_pct:
                    pred_winner, win_pick = "away", f"🔵 {away_kr} 우세 ({a_pct}%)"
                else:
                    pred_winner, win_pick = "draw", f"🟡 팽팽한 무승부 ({d_pct}%)"

                # 종료 경기 채점
                if is_finished and pred_winner != "none":
                    if h_goal > a_goal: actual = "home"
                    elif a_goal > h_goal: actual = "away"
                    else: actual = "draw"
                    win_pick += " <span style='color:#ff9800;'>(적중)</span>" if actual == pred_winner else " <span style='color:#ff5252;'>(미적중)</span>"
                        
                # 전문가 코멘트 번역
                advice = translate_to_ko(preds.get('advice', '데이터 분석 중'))
                control_pick = f"🧠 AI: {advice}"
                
                # 언더/오버
                under_over_val = preds.get('under_over', '')
                if under_over_val:
                    uo_text = "언더 (저득점)" if "-" in under_over_val else "오버 (다득점)"
                    clean_val = under_over_val.replace('-', '').replace('+', '')
                    over_under = f"🔥 기준점 {clean_val} {uo_text}"
                else:
                    over_under = "🔥 기준점 산정 중"

                stat_box = f"<span style='color:#aaa;'>스쿼드 폼(Form):</span> {home_kr} <b>{form_h}</b> vs <b>{form_a}</b> {away_kr}<br>"
                stat_box += f"<span style='color:#aaa;'>공격진 파괴력:</span> <b>{att_h}</b> vs <b>{att_a}</b>"

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
    status_text.text("✅ 스쿼드 기반 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

# 💡 화면 출력 (들여쓰기 에러 완벽 차단)
if st.session_state['analyzed_html_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_html_list']):
        
        # 1. 윗부분 카드 생성
        html_str = "<div class='card-box'>"
        html_str += f"<div class='league-txt'>{data['league']}</div>"
        html_str += f"<div class='match-txt'>{data['match_display']}</div>"
        html_str += f"<div class='stat-bg'>{data['stat_box']}</div>"
        html_str += f"<div class='predict-txt'>🎯 {data['win_pick']}<br>"
        html_str += f"<span style='font-size: 14px; font-weight: normal; color: #00E676;'>"
        html_str += f"⚔️ {data['control_pick']}<br>{data['over_under']}</span></div></div>"
        
        with cols[idx % 3]:
            st.markdown(html_str, unsafe_allow_html=True)
            
            # 2. 다크모드 전술판 아코디언 메뉴
            with st.expander("▶ 다크모드 전술판 및 라인업"):
                st.markdown(data['h_pitch'], unsafe_allow_html=True)
                st.markdown(data['a_pitch'], unsafe_allow_html=True)
            
            st.write("")
elif st.session_state['analyzed_html_list'] == []:
    st.markdown("")
