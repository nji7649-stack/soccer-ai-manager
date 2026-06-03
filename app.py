import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time
import plotly.graph_objects as go

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 UI 고정 CSS (다크모드 통일)
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
.lineup-box { font-size: 12px; color: #bbb; line-height: 1.5; background: #0a0a0a; padding: 10px; border-radius: 8px; border: 1px solid #333; margin-top: 10px;}
.lineup-title { color: #fff; font-weight: bold; margin-bottom: 5px; border-bottom: 1px solid #444; padding-bottom: 3px;}
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

# 💡 1. 텍스트 라인업 추출 함수
def get_lineup_html(home_kr, away_kr, lineup_data):
    if not lineup_data or len(lineup_data) < 2:
        return "<div class='lineup-box' style='text-align:center;'>선발 명단 미발표</div>"
    
    h_start = ", ".join([p['player']['name'].split()[-1] for p in lineup_data[0].get('startXI', [])])
    h_sub = ", ".join([p['player']['name'].split()[-1] for p in lineup_data[0].get('substitutes', [])])
    a_start = ", ".join([p['player']['name'].split()[-1] for p in lineup_data[1].get('startXI', [])])
    a_sub = ", ".join([p['player']['name'].split()[-1] for p in lineup_data[1].get('substitutes', [])])
    
    html = f"""
    <div style='display:flex; justify-content:space-between; gap:10px;'>
        <div class='lineup-box' style='width:50%;'>
            <div class='lineup-title'>🔵 {home_kr}</div>
            <b>선발:</b> {h_start}<br><br><b>후보:</b> {h_sub}
        </div>
        <div class='lineup-box' style='width:50%;'>
            <div class='lineup-title'>🔴 {away_kr}</div>
            <b>선발:</b> {a_start}<br><br><b>후보:</b> {a_sub}
        </div>
    </div>
    """
    return html

# 💡 2. Plotly 육각형 레이더 차트 생성 함수
def create_radar_chart(home_kr, away_kr, comparison):
    categories = ['공격력(Att)', '수비력(Def)', '최근 폼(Form)', '상대전적(H2H)', '득점력(Goals)', '전술완성도(Poisson)']
    
    h_vals = [
        safe_num(comparison.get('att', {}).get('home')), safe_num(comparison.get('def', {}).get('home')),
        safe_num(comparison.get('form', {}).get('home')), safe_num(comparison.get('h2h', {}).get('home')),
        safe_num(comparison.get('goals', {}).get('home')), safe_num(comparison.get('poisson', {}).get('home'))
    ]
    
    a_vals = [
        safe_num(comparison.get('att', {}).get('away')), safe_num(comparison.get('def', {}).get('away')),
        safe_num(comparison.get('form', {}).get('away')), safe_num(comparison.get('h2h', {}).get('away')),
        safe_num(comparison.get('goals', {}).get('away')), safe_num(comparison.get('poisson', {}).get('away'))
    ]
    
    # 데이터가 모두 0이면 차트를 그리지 않음
    if sum(h_vals) == 0 and sum(a_vals) == 0: return None

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=h_vals, theta=categories, fill='toself', name=home_kr, line_color='#2196F3', fillcolor='rgba(33, 150, 243, 0.4)'))
    fig.add_trace(go.Scatterpolar(r=a_vals, theta=categories, fill='toself', name=away_kr, line_color='#F44336', fillcolor='rgba(244, 67, 54, 0.4)'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#444', tickfont=dict(color='#888')), bgcolor='#0a0a0a'),
        showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white', size=11),
        margin=dict(l=30, r=30, t=30, b=30), height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 육각형 딥러닝 예측 분석실</h1>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())

LEAGUE_MAP = {
    "1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", 
    "140": "라리가", "135": "세리에A", "78": "분데스리가", 
    "61": "리그1", "292": "K리그1"
}

selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["39", "140", "292"])

if 'analyzed_data_list' not in st.session_state:
    st.session_state['analyzed_data_list'] = []

if st.sidebar.button("🚀 육각형 레이더 분석 시작"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_leagues = len(selected_leagues)
    new_data_list = []
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 스탯 레이더 생성 중... ({idx+1}/{total_leagues})")
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

                pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                odds_res = requests.get("https://v3.football.api-sports.io/odds", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not pred_res: continue
                
                pred_data = pred_res[0]
                comparison = pred_data.get('comparison', {})
                
                # 💡 레이더 차트 피규어 생성
                radar_fig = create_radar_chart(home_kr, away_kr, comparison)
                
                # 💡 라인업 텍스트 HTML 생성
                lineup_html = get_lineup_html(home_kr, away_kr, lineup_data)

                # 배당 파싱
                odds_h, odds_d, odds_a = 0.0, 0.0, 0.0
                if odds_res:
                    bookmakers = odds_res[0].get('bookmakers', [])
                    if bookmakers:
                        bets = bookmakers[0].get('bets', [])
                        for bet in bets:
                            if bet['name'] == 'Match Winner':
                                for val in bet['values']:
                                    if str(val['value']) == 'Home': odds_h = float(val['odd'])
                                    elif str(val['value']) == 'Draw': odds_d = float(val['odd'])
                                    elif str(val['value']) == 'Away': odds_a = float(val['odd'])
                                break
                
                form_h = safe_num(comparison.get('form', {}).get('home'))
                form_a = safe_num(comparison.get('form', {}).get('away'))
                h2h_h = safe_num(comparison.get('h2h', {}).get('home'))
                h2h_a = safe_num(comparison.get('h2h', {}).get('away'))

                pred_winner = "none"
                if odds_h > 0 and odds_a > 0:
                    if odds_h < odds_a - 0.3: pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력 (정배당)"
                    elif odds_a < odds_h - 0.3: pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력 (정배당)"
                    else:
                        if h2h_h > h2h_a or form_h > form_a: pred_winner, win_pick = "home", f"🟢 {home_kr} 약우세 (전적/폼 반영)"
                        elif h2h_a > h2h_h or form_a > form_h: pred_winner, win_pick = "away", f"🔵 {away_kr} 약우세 (전적/폼 반영)"
                        else: pred_winner, win_pick = "draw", "🟡 초박빙 무승부 배당"
                else:
                    if h2h_h > h2h_a: pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 우세"
                    elif h2h_a > h2h_h: pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 우세"
                    else: pred_winner, win_pick = "none", "⚠️ 데이터 수집 불가 (패스)"

                if is_finished and pred_winner != "none":
                    if h_goal > a_goal: actual = "home"
                    elif a_goal > h_goal: actual = "away"
                    else: actual = "draw"
                    win_pick += " <span style='color:#ff9800;'>(적중)</span>" if actual == pred_winner else " <span style='color:#ff5252;'>(미적중)</span>"
                        
                odds_text = f"<b style='color:#ff9800;'>{odds_h}</b> | 무 <b>{odds_d}</b> | 원정 <b style='color:#ff9800;'>{odds_a}</b>" if odds_h > 0 else "해외 배당 발매 전"
                stat_box = f"<span style='color:#aaa;'>해외 배당:</span> 홈 {odds_text}<br>"
                stat_box += f"<span style='color:#aaa;'>최근 폼:</span> {home_kr} <b>{form_h}%</b> vs <b>{form_a}%</b> {away_kr}"

                advice = translate_to_ko(pred_data['predictions'].get('advice', '데이터 분석 중'))
                control_pick = f"🧠 AI: {advice}"
                
                under_over_val = pred_data['predictions'].get('under_over', '')
                if under_over_val:
                    uo_text = "언더" if "-" in under_over_val else "오버"
                    clean_val = under_over_val.replace('-', '').replace('+', '')
                    over_under = f"🔥 기준점 {clean_val} {uo_text}"
                else:
                    over_under = "🔥 기준점 산정 중"

                new_data_list.append({
                    "league": top_league_display,
                    "match_display": match_display,
                    "stat_box": stat_box,
                    "win_pick": win_pick, 
                    "control_pick": control_pick, 
                    "over_under": over_under,
                    "radar_fig": radar_fig,
                    "lineup_html": lineup_html
                })
        except:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 육각형 전력 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_data_list'] = new_data_list

# 화면 출력
if st.session_state['analyzed_data_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_data_list']):
        html_str = "<div class='card-box'>"
        html_str += f"<div class='league-txt'>{data['league']}</div>"
        html_str += f"<div class='match-txt'>{data['match_display']}</div>"
        html_str += f"<div class='stat-bg'>{data['stat_box']}</div>"
        html_str += f"<div class='predict-txt'>🎯 {data['win_pick']}<br>"
        html_str += f"<span style='font-size: 14px; font-weight: normal; color: #00E676;'>"
        html_str += f"⚔️ {data['control_pick']}<br>{data['over_under']}</span></div></div>"
        
        with cols[idx % 3]:
            st.markdown(html_str, unsafe_allow_html=True)
            
            # 💡 아코디언 안에 레이더 차트와 선발 명단 리스트 삽입
            with st.expander("▶ 전력 육각형 차트 & 출전 명단"):
                if data['radar_fig']:
                    st.plotly_chart(data['radar_fig'], use_container_width=True)
                else:
                    st.markdown("<div style='text-align:center; color:#888; padding:10px;'>전력 비교 데이터 부족</div>", unsafe_allow_html=True)
                st.markdown(data['lineup_html'], unsafe_allow_html=True)
            
            st.write("")
elif st.session_state['analyzed_data_list'] == []:
    st.markdown("")
