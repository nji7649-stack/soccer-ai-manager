import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 UI 고정 CSS (네온 그린 통일 및 오렌지색 채점)
custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px; line-height: 1.4; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 14px; line-height: 1.6; text-align: center;}
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
    if isinstance(value, str): return float(value.replace('%', '').replace('+', '').replace('-', ''))
    return float(value)

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 사전 승부 예측 AI (세이버메트릭스)</h1>", unsafe_allow_html=True)
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

if st.sidebar.button("🚀 베팅 데이터 불러오기"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_leagues = len(selected_leagues)
    new_html_list = []
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 빅데이터 분석 중...")
        progress_bar.progress((idx) / total_leagues)
        
        querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            
            # 유료 API 에러 검출기 (만약 에러가 나면 진짜 에러 원인을 영어로 보여줌)
            if 'errors' in res and res['errors']:
                st.error(f"🚨 API 에러: {res['errors']}")
                st.stop()

            fixtures = res.get('response', [])
            
            for match in fixtures:
                fix_id = str(match['fixture']['id'])
                home_kr = translate_to_ko(match['teams']['home']['name'])
                away_kr = translate_to_ko(match['teams']['away']['name'])
                
                status_short = match['fixture']['status']['short']
                is_finished = status_short in ['FT', 'AET', 'PEN']
                is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P']
                
                match_date_raw = match['fixture']['date']
                try: time_str = datetime.strptime(match_date_raw[:16], "%Y-%m-%dT%H:%M").strftime("%H:%M")
                except: time_str = "시간미정"
                
                top_league_display = f"{LEAGUE_MAP[league_id]} ({time_str})"
                
                h_goal = match['goals']['home'] if match['goals']['home'] is not None else 0
                a_goal = match['goals']['away'] if match['goals']['away'] is not None else 0
                
                if is_finished:
                    match_display = f"{home_kr} <span style='color:#00E676; margin:0 10px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[종료됨]</div>"
                elif is_live:
                    match_display = f"{home_kr} <span style='color:#ff9800; margin:0 10px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr} <div style='font-size:12px; color:#ff9800; margin-top:5px;'>🔊 실시간 진행 중</div>"
                else:
                    match_display = f"{home_kr} <span style='color:#888; font-size:16px; margin:0 10px;'>VS</span> {away_kr} <div style='font-size:12px; color:#aaa; margin-top:5px;'>[경기 시작 전]</div>"

                # 💡 사전 예측 API 연결 (유료 플랜 최적화)
                pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not pred_res:
                    continue
                
                pred_data = pred_res[0]
                preds = pred_data['predictions']
                comparison = pred_data['comparison']
                
                form_h = comparison.get('form', {}).get('home', '50%')
                form_a = comparison.get('form', {}).get('away', '50%')
                att_h = comparison.get('att', {}).get('home', '50%')
                att_a = comparison.get('att', {}).get('away', '50%')
                def_h = comparison.get('def', {}).get('home', '50%')
                def_a = comparison.get('def', {}).get('away', '50%')

                advanced_stats_html = f"""
                <span style="color:#fff;">최근 전력(Form):</span> {home_kr} <b>{form_h}</b> vs <b>{form_a}</b> {away_kr}<br>
                <span style="color:#fff;">공격력 지표:</span> {home_kr} <b>{att_h}</b> vs <b>{att_a}</b> {away_kr}<br>
                <span style="color:#fff;">수비력 지표:</span> {home_kr} <b>{def_h}</b> vs <b>{def_a}</b> {away_kr}
                """
                
                h_pct = safe_num(preds['percent']['home'])
                a_pct = safe_num(preds['percent']['away'])
                d_pct = safe_num(preds['percent']['draw'])
                
                if h_pct > a_pct and h_pct > d_pct:
                    pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력 ({h_pct}%)"
                elif a_pct > h_pct and a_pct > d_pct:
                    pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력 ({a_pct}%)"
                else:
                    pred_winner, win_pick = "draw", f"🟡 팽팽한 무승부 예상 ({d_pct}%)"

                if is_finished:
                    if h_goal > a_goal: actual_winner = "home"
                    elif a_goal > h_goal: actual_winner = "away"
                    else: actual_winner = "draw"
                    
                    if actual_winner == pred_winner: win_pick += " <span style='color:#ff9800;'>(적중)</span>"
                    else: win_pick += " <span style='color:#ff9800;'>(미적중)</span>"
                        
                advice = preds.get('advice', '데이터 분석 중')
                translated_advice = translate_to_ko(advice)
                control_pick = f"💡 AI 분석 코멘트: {translated_advice}"
                
                under_over_val = preds.get('under_over', '')
                if under_over_val:
                    uo_text = "언더 (저득점)" if "-" in under_over_val else "오버 (다득점)"
                    clean_val = under_over_val.replace('-', '').replace('+', '')
                    over_under = f"📊 기준점 {clean_val} {uo_text}"
                else:
                    over_under = "📊 언더/오버 기준점 미제공"

                new_html_list.append({
                    "league": top_league_display,
                    "match_display": match_display,
                    "advanced_stats": advanced_stats_html,
                    "win_pick": win_pick, 
                    "control_pick": control_pick, 
                    "over_under": over_under
                })
        except Exception as e:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 빅데이터 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

if st.session_state['analyzed_html_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_html_list']):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card-box">
                <div class="league-txt">{data['league']}</div>
                <div class="match-txt">{data['match_display']}</div>
                <div class="stat-bg">
                    {data['advanced_stats']}
                </div>
                <div class="predict-txt">
                    🎯 {data['win_pick']}<br>
                    ⚔️ {data['control_pick']}<br>
                    {data['over_under']}
                </div>
            </div>
            """, unsafe_allow_html=True)
elif st.session_state['analyzed_html_list'] == []:
    st.markdown("")
