import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time
import math

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 UI CSS: 모바일 반응형(@media) 쿼리 및 유연한 레이아웃 적용
custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
    display: flex; flex-direction: column; justify-content: space-between; height: 100%;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; }
.match-txt { color: #ffffff; font-size: 19px; font-weight: bold; text-align: center; margin-bottom: 12px; line-height: 1.3; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 13.5px; line-height: 1.7; text-align: center; margin-bottom: 10px; }
.predict-txt { color: #00E676; font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; line-height: 1.6; }

/* 라인업 테이블 디자인 */
.table-wrapper { overflow-x: auto; margin-top: 10px; }
.lineup-table { width: 100%; border-collapse: collapse; font-size: 12px; color: #ccc; }
.lineup-table th { background-color: #333; padding: 8px; text-align: center; border-bottom: 2px solid #555; color: #fff; white-space: nowrap; }
.lineup-table td { padding: 6px 8px; border-bottom: 1px solid #2a2a2a; vertical-align: top; text-align: center; white-space: nowrap; }

/* 📱 스마트폰 모바일 화면 최적화 */
@media (max-width: 768px) {
    .card-box { padding: 15px; margin-bottom: 15px; }
    .match-txt { font-size: 17px; }
    .stat-bg { font-size: 12.5px; padding: 10px; }
    .predict-txt { font-size: 14px; }
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

# 💡 모바일 최적화 라인업 테이블 (가로 스크롤 래퍼 포함)
def get_lineup_table(home_kr, away_kr, lineup_data):
    if not lineup_data or len(lineup_data) < 2:
        return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표</div>"
    
    h_players = [p['player']['name'].split()[-1] for p in lineup_data[0].get('startXI', [])]
    a_players = [p['player']['name'].split()[-1] for p in lineup_data[1].get('startXI', [])]
    
    max_len = max(len(h_players), len(a_players))
    h_players += [""] * (max_len - len(h_players))
    a_players += [""] * (max_len - len(a_players))

    # table-wrapper 클래스로 모바일 화면 이탈 방지
    table_html = "<div class='table-wrapper'><table class='lineup-table'>"
    table_html += f"<tr><th style='color:#4FC3F7;'>{home_kr}</th><th style='color:#EF5350;'>{away_kr}</th></tr>"
    for h_player, a_player in zip(h_players, a_players):
        table_html += f"<tr><td>{h_player}</td><td>{a_player}</td></tr>"
    table_html += "</table></div>"
    
    return table_html

# 💡 모바일 반응형 HTML 레이더 차트 (viewBox 적용)
def create_html_radar(h_vals, a_vals, home_kr, away_kr):
    if sum(h_vals) < 10 and sum(a_vals) < 10:
        return "<div style='text-align:center; padding:30px; color:#ff5252; background:#111; border-radius:8px;'>⚠️ 전력 데이터 부족</div>"

    labels = ['공격력', '수비력', '최근폼', '상대전적', '득점력', '전술도']
    size = 240
    center = size / 2
    max_val = 100
    
    def get_polygon(vals, border_color, fill_color):
        points = []
        for i, val in enumerate(vals):
            angle = (math.pi * 2 / 6) * i - (math.pi / 2)
            r = (val / max_val) * (size * 0.35)
            x = center + r * math.cos(angle)
            y = center + r * math.sin(angle)
            points.append(f"{x},{y}")
        return f"<polygon points='{' '.join(points)}' style='fill:{fill_color}; stroke:{border_color}; stroke-width:2; opacity:0.6;' />"

    svg_lines = ""
    for i in range(6):
        angle = (math.pi * 2 / 6) * i - (math.pi / 2)
        x = center + (size * 0.35) * math.cos(angle)
        y = center + (size * 0.35) * math.sin(angle)
        svg_lines += f"<line x1='{center}' y1='{center}' x2='{x}' y2='{y}' style='stroke:#444; stroke-width:1;' />"
        
        lx = center + (size * 0.44) * math.cos(angle)
        ly = center + (size * 0.44) * math.sin(angle)
        anchor = "middle"
        if lx > center + 10: anchor = "start"
        elif lx < center - 10: anchor = "end"
        svg_lines += f"<text x='{lx}' y='{ly+4}' fill='#ddd' font-size='12' font-weight='bold' text-anchor='{anchor}'>{labels[i]}</text>"

    for r_ratio in [0.33, 0.66, 1.0]:
        r = (size * 0.35) * r_ratio
        pts = []
        for i in range(6):
            angle = (math.pi * 2 / 6) * i - (math.pi / 2)
            pts.append(f"{center + r * math.cos(angle)},{center + r * math.sin(angle)}")
        svg_lines += f"<polygon points='{' '.join(pts)}' style='fill:none; stroke:#333; stroke-width:1;' />"

    h_poly = get_polygon(h_vals, "#4FC3F7", "rgba(79, 195, 247, 0.3)") 
    a_poly = get_polygon(a_vals, "#EF5350", "rgba(239, 83, 80, 0.3)") 

    # width:100%, max-width 처리로 폰 화면에서도 유연하게 줄어듦
    html = f"""
    <div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:15px;'>
        <div style='font-size:12px; color:#fff; margin-bottom:15px; font-weight:bold; text-align:center;'>
            <span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}
        </div>
        <svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>
            {svg_lines}
            {h_poly}
            {a_poly}
        </svg>
    </div>
    """
    return html

st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px;'>🏆 실시간 AI 승부 예측실</h1>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())

LEAGUE_MAP = {
    "1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", 
    "140": "라리가", "135": "세리에A", "78": "분데스리가", 
    "61": "리그1", "292": "K리그1"
}

selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["39", "140", "135"])

if 'analyzed_data_list' not in st.session_state:
    st.session_state['analyzed_data_list'] = []

if st.sidebar.button("🚀 정밀 분석 시작 (모바일 지원)"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_leagues = len(selected_leagues)
    new_data_list = []
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 스탯 수집 중... ({idx+1}/{total_leagues})")
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
                    match_display = f"{home_kr} <span style='color:#00E676; margin:0 10px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr}"
                elif is_live:
                    match_display = f"{home_kr} <span style='color:#ff9800; margin:0 10px; font-size:22px;'>{h_goal} : {a_goal}</span> {away_kr}"
                else:
                    match_display = f"{home_kr} <span style='color:#888; font-size:16px; margin:0 10px;'>VS</span> {away_kr}"

                pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                odds_res = requests.get("https://v3.football.api-sports.io/odds", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                if not pred_res: continue
                
                pred_data = pred_res[0]
                comparison = pred_data.get('comparison', {})
                
                h_vals = [safe_num(comparison.get('att', {}).get('home')), safe_num(comparison.get('def', {}).get('home')), safe_num(comparison.get('form', {}).get('home')), safe_num(comparison.get('h2h', {}).get('home')), safe_num(comparison.get('goals', {}).get('home')), safe_num(comparison.get('poisson', {}).get('home'))]
                a_vals = [safe_num(comparison.get('att', {}).get('away')), safe_num(comparison.get('def', {}).get('away')), safe_num(comparison.get('form', {}).get('away')), safe_num(comparison.get('h2h', {}).get('away')), safe_num(comparison.get('goals', {}).get('away')), safe_num(comparison.get('poisson', {}).get('away'))]
                
                radar_html = create_html_radar(h_vals, a_vals, home_kr, away_kr)
                lineup_html = get_lineup_table(home_kr, away_kr, lineup_data)

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
                
                pred_winner = "none"
                if odds_h > 0 and odds_a > 0:
                    if odds_h < odds_a - 0.3: pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력 (정배당)"
                    elif odds_a < odds_h - 0.3: pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력 (정배당)"
                    else:
                        if h_vals[2] > a_vals[2] or h_vals[3] > a_vals[3]: pred_winner, win_pick = "home", f"🟢 {home_kr} 약우세 (전적/폼 반영)"
                        elif a_vals[2] > h_vals[2] or a_vals[3] > h_vals[3]: pred_winner, win_pick = "away", f"🔵 {away_kr} 약우세 (전적/폼 반영)"
                        else: pred_winner, win_pick = "draw", "🟡 초박빙 무승부 배당"
                else:
                    if h_vals[3] > a_vals[3]: pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 우세"
                    elif a_vals[3] > h_vals[3]: pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 우세"
                    else: pred_winner, win_pick = "none", "⚠️ 데이터 수집 불가 (패스)"

                if is_finished and pred_winner != "none":
                    if h_goal > a_goal: actual = "home"
                    elif a_goal > h_goal: actual = "away"
                    else: actual = "draw"
                    win_pick += " <span style='color:#ff9800;'>(적중)</span>" if actual == pred_winner else " <span style='color:#ff5252;'>(미적중)</span>"
                        
                odds_text = f"<b style='color:#ff9800;'>{odds_h}</b> | 무 <b>{odds_d}</b> | 원정 <b style='color:#ff9800;'>{odds_a}</b>" if odds_h > 0 else "해외 배당 미발매"
                stat_box = f"<span style='color:#aaa;'>해외 배당:</span> 홈 {odds_text}<br>"
                stat_box += f"<span style='color:#aaa;'>최근 폼:</span> {home_kr} <b>{h_vals[2]}%</b> vs <b>{a_vals[2]}%</b> {away_kr}"

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
                    "radar_html": radar_html,
                    "lineup_html": lineup_html
                })
        except:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_data_list'] = new_data_list

# 화면 출력 (모바일 자동 스태킹 최적화)
if st.session_state.get('analyzed_data_list'):
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_data_list']):
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="height: 100%;">
                <div class='card-box'>
                    <div>
                        <div class='league-txt'>{data['league']}</div>
                        <div class='match-txt'>{data['match_display']}</div>
                        <div class='stat-bg'>{data['stat_box']}</div>
                    </div>
                    <div class='predict-txt'>
                        🎯 {data['win_pick']}<br>
                        <span style='font-size: 14px; font-weight: normal; color: #00E676;'>
                        ⚔️ {data['control_pick']}<br>{data['over_under']}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("▶ 전력 차트 & 선발 명단"):
                st.markdown(data['radar_html'], unsafe_allow_html=True)
                st.markdown(data['lineup_html'], unsafe_allow_html=True)
            
            st.write("")
elif st.session_state.get('analyzed_data_list') == []:
    st.markdown("")
