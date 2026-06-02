import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 디자인 세팅: 박스 높이 강제 고정(min-height) 및 내부 요소 칼각 정렬
st.markdown("""
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 15px;
    min-height: 400px; /* 💡 박스 크기 고정 */
    display: flex; flex-direction: column; justify-content: space-between;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; text-align: center; }
.match-txt { color: #ffffff; font-size: 19px; font-weight: bold; text-align: center; margin-bottom: 15px; min-height: 50px;}
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 14px; line-height: 1.6; text-align: center; }
.predict-txt { color: #00E676; font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; margin-top: 15px; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets["FOOTBALL_API_KEY"]
HEADERS = {'x-apisports-key': API_KEY}

@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    try: return GoogleTranslator(source='en', target='ko').translate(text)
    except: return text

def safe_num(value):
    if value is None or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except: return 0.0

# 💡 초록 잔디 전술판 (선수 이름은 로딩 속도를 위해 영문 성씨 유지)
def draw_tactical_board(team_name, lineup_info, shirt_color):
    if not lineup_info or 'startXI' not in lineup_info:
        return f"<div style='text-align:center; color:#888; padding:10px;'>{team_name} 명단 미발표</div>"
    
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
        
    board_html = f"<div style='border: 2px solid rgba(255,255,255,0.2); border-radius: 8px; background: #1b4d24; padding: 10px; margin-bottom: 10px;'>"
    board_html += f"<div style='text-align:center; color: #a5d6a7; font-weight: bold; margin-bottom: 15px; font-size:13px;'>{team_name} <span style='color:#fff;'>({formation})</span></div>"
    
    for row_idx in sorted(rows.keys(), reverse=True):
        players = rows[row_idx]
        board_html += "<div style='display: flex; justify-content: space-evenly; margin-bottom: 10px;'>"
        for player in players:
            board_html += f"<div style='background: {shirt_color}; color: #fff; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight:bold; white-space: nowrap; box-shadow: 1px 1px 3px rgba(0,0,0,0.6);'>{player}</div>"
        board_html += "</div>"
    board_html += "</div>"
    return board_html

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 딥러닝 AI 축구 승부 예측 PRO</h1>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())

LEAGUE_MAP = {
    "1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", 
    "140": "라리가", "135": "세리에A", "78": "분데스리가", 
    "61": "리그1", "292": "K리그1"
}

selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["10", "39", "140"])

if st.sidebar.button("🚀 딥러닝 데이터 분석 시작"):
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
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 스쿼드 및 전력 지표 분석 중... ({idx+1}/{total_leagues})")
        progress_bar.progress((idx) / total_leagues)
        
        is_national = (league_id in ["1", "10"]) # 국가대표 매치 식별
        
        querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            fixtures = res.get('response', [])
            
            for match in fixtures:
                matches_found = True
                fix_id = str(match['fixture']['id'])
                home_kr = translate_to_ko(match['teams']['home']['name'])
                away_kr = translate_to_ko(match['teams']['away']['name'])
                
                status = match['fixture']['status']['short']
                is_finished = status in ['FT', 'AET', 'PEN']
                
                try: match_time = datetime.strptime(match['fixture']['date'][:16], "%Y-%m-%dT%H:%M").strftime("%H:%M")
                except: match_time = "시간미정"
                
                # 💡 스코어 결과
                h_goal = match['goals']['home'] if match['goals']['home'] is not None else 0
                a_goal = match['goals']['away'] if match['goals']['away'] is not None else 0
                
                if is_finished:
                    match_display = f"{home_kr} <span style='font-size:24px; color:#00E676; margin: 0 10px;'>{h_goal} : {a_goal}</span> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[경기종료]</div>"
                else:
                    match_display = f"{home_kr} <span style='font-size:16px; color:#888; margin: 0 10px;'>VS</span> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[{status}]</div>"

                # 💡 핵심: 단순 슈팅수가 아닌 'Predictions API' 빅데이터 호출
                pred_data = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not pred_data: continue
                
                preds = pred_data[0]['predictions']
                comparison = pred_data[0]['comparison']
                
                # 세이버메트릭스 지표 추출 (최근 폼, 공격력)
                form_h = comparison.get('form', {}).get('home', '50%')
                form_a = comparison.get('form', {}).get('away', '50%')
                att_h = comparison.get('att', {}).get('home', '50%')
                att_a = comparison.get('att', {}).get('away', '50%')
                
                h_pct = safe_num(preds['percent']['home'])
                a_pct = safe_num(preds['percent']['away'])
                d_pct = safe_num(preds['percent']['draw'])

                # 💡 국대(월드컵/A매치) vs 클럽 리그 맞춤형 전력 분석 박스
                if is_national:
                    stat_box = f"🌍 <b>국가대표 스쿼드 밸류 분석</b><br>"
                    stat_box += f"<span style='color:#ccc;'>해외파 포함 파괴력:</span> {home_kr} <b style='color:#ff9800;'>{att_h}</b> vs <b style='color:#ff9800;'>{att_a}</b> {away_kr}<br>"
                    stat_box += f"<span style='color:#ccc;'>국대 조직력(Form):</span> {home_kr} <b>{form_h}</b> vs <b>{form_a}</b> {away_kr}"
                else:
                    stat_box = f"📊 <b>클럽 전력 빅데이터 지표</b><br>"
                    stat_box += f"<span style='color:#ccc;'>공격 파괴력:</span> {home_kr} <b style='color:#ff9800;'>{att_h}</b> vs <b style='color:#ff9800;'>{att_a}</b> {away_kr}<br>"
                    stat_box += f"<span style='color:#ccc;'>최근 5경기 폼:</span> {home_kr} <b>{form_h}</b> vs <b>{form_a}</b> {away_kr}"

                # 💡 승패 예측 로직 (1%라도 우세하면 승리 픽, 데이터 없으면 패스)
                if h_pct == 0 and a_pct == 0:
                    pred_winner = "none"
                    win_pick = "⚠️ 배팅 데이터 부족 (패스 권장)"
                elif h_pct > a_pct:
                    pred_winner = "home"
                    win_pick = f"🟢 {home_kr} 승리 예상 ({h_pct}%)"
                elif a_pct > h_pct:
                    pred_winner = "away"
                    win_pick = f"🔵 {away_kr} 승리 예상 ({a_pct}%)"
                else:
                    pred_winner = "draw"
                    win_pick = f"🟡 초박빙 무승부 배당 ({d_pct}%)"
                
                # 적중 채점
                if is_finished and pred_winner != "none":
                    if h_goal > a_goal: actual = "home"
                    elif a_goal > h_goal: actual = "away"
                    else: actual = "draw"
                    win_pick += " <span style='color:#ff9800;'>(적중)</span>" if actual == pred_winner else " <span style='color:#ff5252;'>(미적중)</span>"

                # 💡 디테일 코멘트 (API 분석가의 진짜 코멘트 번역)
                raw_advice = preds.get('advice', '')
                if raw_advice:
                    ko_advice = translate_to_ko(raw_advice)
                    control_pick = f"🧠 AI 분석: {ko_advice}"
                else:
                    control_pick = f"🧠 AI 분석: 전력 기반 {pred_winner.upper()} 사이드 추천"
                
                under_over_val = preds.get('under_over', '')
                over_under = f"🔥 예상 골 기준점: {under_over_val}" if under_over_val else "⚖️ 배팅 데이터 수집 중"

                h_pitch_html = draw_tactical_board(home_kr, lineup_data[0] if lineup_data else None, "#1565c0")
                a_pitch_html = draw_tactical_board(away_kr, lineup_data[1] if lineup_data and len(lineup_data)>1 else None, "#c62828")

                with cols[col_idx % 3]:
                    # html 문자열 합치기로 에러 원천 차단
                    card_html = f"<div class='card-box'>"
                    card_html += f"<div class='league-txt'>{LEAGUE_MAP[league_id]} ({match_time})</div>"
                    card_html += f"<div class='match-txt'>{match_display}</div>"
                    card_html += f"<div class='stat-bg'>{stat_box}</div>"
                    card_html += f"<div><div class='predict-txt'>🎯 {win_pick}<br>⚔️ {control_pick}<br>📊 {over_under}</div></div>"
                    card_html += f"</div>"
                    
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    with st.expander("▶ 전술판 및 선발 라인업 보기"):
                        st.markdown(h_pitch_html, unsafe_allow_html=True)
                        st.markdown(a_pitch_html, unsafe_allow_html=True)
                    
                    st.write("") 
                col_idx += 1

        except Exception as e:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 딥러닝 스쿼드 분석이 완료되었습니다!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    if not matches_found:
        st.error("해당 날짜에 분석 가능한 데이터가 없습니다.")
