import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time
import math

st.set_page_config(page_title="AI 축구 분석실 PRO MAX", page_icon="⚽", layout="wide")

# 🎨 UI CSS
custom_css = """
<style>
.stApp { background-color: #0e1117; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 12px;
    border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 25px;
    display: flex; flex-direction: column; justify-content: space-between; height: 100%;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; letter-spacing: 1px; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 8px; line-height: 1.3; }
.referee-txt { font-size: 11px; color: #888; text-align: center; margin-bottom: 15px; }
.stat-bg { background-color: #262730; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 13.5px; line-height: 1.7; text-align: center; margin-bottom: 10px; border: 1px solid #444;}
.predict-txt { font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; line-height: 1.6; }

.ai-advice { font-size: 11.5px; color: #aaa; font-weight: normal; margin-top: 5px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; white-space: normal; }
.over-under { font-size: 13px; color: #ddd; font-weight: normal; margin-top: 4px; }

.prob-container { display: flex; width: 100%; height: 8px; border-radius: 4px; overflow: hidden; margin-top: 5px; margin-bottom: 15px; background-color: #333; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }
.prob-text { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 3px; }

.table-wrapper { overflow-x: auto; margin-top: 10px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 12px; color: #ccc; text-align: center; }
.detail-table th { background-color: #111; padding: 8px; border-bottom: 2px solid #555; color: #fff; white-space: nowrap; }
.detail-table td { padding: 6px 8px; border-bottom: 1px solid #2a2a2a; white-space: nowrap; }
.injury-tag { color: #ff5252; font-size: 11px; background: #331111; padding: 2px 6px; border-radius: 4px; display: inline-block; margin: 2px; }

@media (max-width: 768px) {
    .card-box { padding: 15px; margin-bottom: 15px; }
    .match-txt { font-size: 17px; }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

API_KEY = st.secrets["FOOTBALL_API_KEY"]
HEADERS = {'x-apisports-key': API_KEY}

@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or str(text).strip() in ['', 'N/A']: return '데이터 분석 중'
    try: 
        safe_txt = str(text).replace('<', '').replace('>', '')
        return GoogleTranslator(source='en', target='ko').translate(safe_txt)
    except:
        try:
            time.sleep(0.5)
            return GoogleTranslator(source='en', target='ko').translate(str(text))
        except: return str(text)

def safe_num(value):
    if not value or str(value).strip() in ['', 'N/A']: return 0.0
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except: return 0.0

def fetch_custom_team_stats(team_id, season_year):
    try:
        url = "https://v3.football.api-sports.io/fixtures"
        res = requests.get(url, headers=HEADERS, params={"team": team_id, "last": 5, "season": season_year}).json()
        fixtures = res.get('response', [])
        if not fixtures: return 10, 10, 10 
        
        wins, goals_for, goals_against = 0, 0, 0
        for match in fixtures:
            is_home = match['teams']['home']['id'] == team_id
            h_g = match['goals']['home'] if match['goals']['home'] is not None else 0
            a_g = match['goals']['away'] if match['goals']['away'] is not None else 0
            if is_home:
                goals_for += h_g; goals_against += a_g
                if h_g > a_g: wins += 1
            else:
                goals_for += a_g; goals_against += h_g
                if a_g > h_g: wins += 1
        return (wins / 5) * 100, min((goals_for / 15) * 100, 100), max(100 - (goals_against / 10) * 100, 0)
    except: return 20, 20, 20

def get_detailed_html(home_kr, away_kr, h_rank, a_rank, h_goals, a_goals, h_goals_against, a_goals_against, h_injuries, a_injuries):
    h_inj_html = "".join([f"<span class='injury-tag'>🚑 {inj}</span>" for inj in h_injuries]) or "<span style='color:#888;'>결장자 없음</span>"
    a_inj_html = "".join([f"<span class='injury-tag'>🚑 {inj}</span>" for inj in a_injuries]) or "<span style='color:#888;'>결장자 없음</span>"
    
    html = f"""
    <div class='table-wrapper'>
        <table class='detail-table'>
            <tr><th style='color:#4FC3F7; width:40%;'>{home_kr}</th><th style='width:20%; color:#aaa;'>비교 지표</th><th style='color:#EF5350; width:40%;'>{away_kr}</th></tr>
            <tr><td><b>{h_rank}</b>위</td><td style='font-size:11px;'>리그 순위</td><td><b>{a_rank}</b>위</td></tr>
            <tr><td>{h_goals}골</td><td style='font-size:11px;'>평균 득점</td><td>{a_goals}골</td></tr>
            <tr><td>{h_goals_against}골</td><td style='font-size:11px;'>평균 실점</td><td>{a_goals_against}골</td></tr>
            <tr>
                <td style='white-space:normal;'>{h_inj_html}</td>
                <td style='font-size:11px;'>결장/부상</td>
                <td style='white-space:normal;'>{a_inj_html}</td>
            </tr>
        </table>
    </div>
    """
    return html

def get_lineup_table(home_kr, away_kr, lineup_data):
    if not lineup_data or len(lineup_data) < 2: return "<div style='text-align:center; padding:15px; color:#888;'>명단 미발표</div>"
    h_p = [p['player']['name'].split()[-1] for p in lineup_data[0].get('startXI', [])]
    a_p = [p['player']['name'].split()[-1] for p in lineup_data[1].get('startXI', [])]
    m_len = max(len(h_p), len(a_p))
    h_p += [""] * (m_len - len(h_p)); a_p += [""] * (m_len - len(a_p))

    html = "<div class='table-wrapper'><table class='detail-table'>"
    html += f"<tr><th style='color:#4FC3F7;'>{home_kr} (선발)</th><th style='color:#EF5350;'>{away_kr} (선발)</th></tr>"
    for h, a in zip(h_p, a_p): html += f"<tr><td>{h}</td><td>{a}</td></tr>"
    html += "</table></div>"
    return html

def create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom=False):
    labels = ['공격력', '수비력', '최근폼', '상대전적', '득점력', '종합전력']
    size = 220; center = size / 2; max_val = 100
    
    def get_poly(vals, bc, fc):
        pts = []
        for i, val in enumerate(vals):
            ang = (math.pi * 2 / 6) * i - (math.pi / 2)
            r = (val / max_val) * (size * 0.35)
            pts.append(f"{center + r * math.cos(ang)},{center + r * math.sin(ang)}")
        return f"<polygon points='{' '.join(pts)}' style='fill:{fc}; stroke:{bc}; stroke-width:2; opacity:0.6;' />"

    svg = ""
    for i in range(6):
        ang = (math.pi * 2 / 6) * i - (math.pi / 2)
        x = center + (size * 0.35) * math.cos(ang); y = center + (size * 0.35) * math.sin(ang)
        svg += f"<line x1='{center}' y1='{center}' x2='{x}' y2='{y}' style='stroke:#444; stroke-width:1;' />"
        lx = center + (size * 0.44) * math.cos(ang); ly = center + (size * 0.44) * math.sin(ang)
        anchor = "start" if lx > center + 10 else ("end" if lx < center - 10 else "middle")
        svg += f"<text x='{lx}' y='{ly+4}' fill='#ddd' font-size='10' font-weight='bold' text-anchor='{anchor}'>{labels[i]}</text>"

    for ratio in [0.33, 0.66, 1.0]:
        r = (size * 0.35) * ratio
        pts = [f"{center + r * math.cos((math.pi*2/6)*i - math.pi/2)},{center + r * math.sin((math.pi*2/6)*i - math.pi/2)}" for i in range(6)]
        svg += f"<polygon points='{' '.join(pts)}' style='fill:none; stroke:#333; stroke-width:1;' />"

    h_poly = get_poly(h_vals, "#4FC3F7", "rgba(79, 195, 247, 0.3)") 
    a_poly = get_poly(a_vals, "#EF5350", "rgba(239, 83, 80, 0.3)") 
    
    badge = "<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>⚙️ AI 자체 데이터 수집 가동</div>" if is_custom else ""
    return f"<div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:10px;'>{badge}<div style='font-size:11px; color:#fff; margin-bottom:10px; font-weight:bold; text-align:center;'><span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}</div><svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>{svg}{h_poly}{a_poly}</svg></div>"

st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px;'>🏆 AI 궁극의 디테일 분석실 (V25 PRO MAX)</h1>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### 📅 검색 날짜 설정")
selected_date = st.sidebar.date_input("날짜를 선택하세요", datetime.today())

st.sidebar.markdown("<br>", unsafe_allow_html=True)
analyze_button = st.sidebar.button("🚀 전체 데이터 딥-스캔 시작", use_container_width=True)
st.sidebar.markdown("---")

st.sidebar.markdown("### 🏆 분석 리그 선택")

with st.sidebar.expander("🌟 국제 대회 (UEFA/FIFA)", expanded=True):
    l_2 = st.checkbox("챔피언스리그 (UCL)", value=False)
    l_3 = st.checkbox("유로파리그 (UEL)", value=False)
    l_1 = st.checkbox("월드컵 (World Cup)", value=False)
    l_10 = st.checkbox("A매치 친선전", value=True)

with st.sidebar.expander("⚽ 유럽 주요 1부 리그", expanded=True):
    l_39 = st.checkbox("프리미어리그 (ENG)", value=True)
    l_140 = st.checkbox("라리가 (ESP)", value=True)
    l_135 = st.checkbox("세리에 A (ITA)", value=False)
    l_78 = st.checkbox("분데스리가 (GER)", value=False)
    l_61 = st.checkbox("리그 1 (FRA)", value=False)
    l_88 = st.checkbox("에레디비시 (NED)", value=False)
    l_119 = st.checkbox("스코티시 프리미어십 (SCO)", value=False)

with st.sidebar.expander("📈 유럽 2부 리그", expanded=False):
    l_40 = st.checkbox("챔피언십 (ENG 2부)", value=False)
    l_141 = st.checkbox("세군다 디비시온 (ESP 2부)", value=False)

with st.sidebar.expander("🌏 아시아 및 기타", expanded=True):
    l_292 = st.checkbox("K리그1 (KOR 1부)", value=False)
    l_293 = st.checkbox("K리그2 (KOR 2부)", value=False)
    l_98 = st.checkbox("J1리그 (JPN)", value=False)

selected_leagues = []
if l_2: selected_leagues.append("2")
if l_3: selected_leagues.append("3")
if l_1: selected_leagues.append("1")
if l_10: selected_leagues.append("10")
if l_39: selected_leagues.append("39")
if l_140: selected_leagues.append("140")
if l_135: selected_leagues.append("135")
if l_78: selected_leagues.append("78")
if l_61: selected_leagues.append("61")
if l_88: selected_leagues.append("88")
if l_119: selected_leagues.append("119")
if l_40: selected_leagues.append("40")
if l_141: selected_leagues.append("141")
if l_292: selected_leagues.append("292")
if l_293: selected_leagues.append("293")
if l_98: selected_leagues.append("98")

LEAGUE_MAP = {
    "2": "챔피언스리그", "3": "유로파리그", "1": "월드컵", "10": "A매치 친선전", 
    "39": "프리미어리그", "140": "라리가", "135": "세리에A", "78": "분데스리가", "61": "리그1", 
    "88": "에레디비시", "119": "스코티시 프리미어십", "40": "챔피언십", "141": "세군다 디비시온",
    "292": "K리그1", "293": "K리그2", "98": "J1리그"
}

AUTUMN_TO_SPRING_LEAGUES = ["2", "3", "39", "140", "135", "78", "61", "88", "119", "40", "141"]

if 'analyzed_data_list' not in st.session_state: st.session_state['analyzed_data_list'] = []

if analyze_button:
    if not selected_leagues: st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요."); st.stop()
        
    progress_bar = st.progress(0); status_text = st.empty()
    total_leagues = len(selected_leagues); new_data_list = []
    
    for idx, league_id in enumerate(selected_leagues):
        status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 정밀 데이터 스캔 중... ({idx+1}/{total_leagues})")
        progress_bar.progress((idx) / total_leagues)
        
        calc_season_year = str(selected_date.year - 1) if league_id in AUTUMN_TO_SPRING_LEAGUES and selected_date.month < 7 else str(selected_date.year)
        querystring = {"league": league_id, "season": calc_season_year, "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get("https://v3.football.api-sports.io/fixtures", headers=HEADERS, params=querystring, timeout=10).json()
            fixtures = res.get('response', [])
            
            for match in fixtures:
                fix_id = str(match['fixture']['id'])
                home_id = match['teams']['home']['id']; away_id = match['teams']['away']['id']
                home_kr = translate_to_ko(match['teams']['home']['name'])
                away_kr = translate_to_ko(match['teams']['away']['name'])
                
                referee = str(match['fixture']['referee']).split(',')[0] if match['fixture']['referee'] else "배정 전"
                venue = match['fixture']['venue']['name'] or "미정"
                
                status_short = match['fixture']['status']['short']
                is_finished = status_short in ['FT', 'AET', 'PEN']
                is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P']
                
                elapsed_time = match['fixture']['status'].get('elapsed', '')
                
                try: match_time = datetime.strptime(match['fixture']['date'][:16], "%Y-%m-%dT%H:%M").strftime("%H:%M")
                except: match_time = "시간미정"
                
                # 💡 핵심: 기호 빼고 깔끔하게 텍스트로만 상태 표시
                if is_live and elapsed_time:
                    top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#ff5252; font-size:12px;'>[진행중: {elapsed_time}분]</span>"
                elif is_finished:
                    top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#aaa; font-size:12px;'>[경기 종료]</span>"
                else:
                    top_league_display = f"{LEAGUE_MAP[league_id]} ({match_time})"
                
                h_goal = match['goals']['home'] if match['goals']['home'] is not None else 0
                a_goal = match['goals']['away'] if match['goals']['away'] is not None else 0
                
                if is_finished: match_display = f"{home_kr} <span style='color:#00E676; margin:0 10px; font-size:24px;'>{h_goal} : {a_goal}</span> {away_kr}"
                elif is_live: match_display = f"{home_kr} <span style='color:#ff5252; margin:0 10px; font-size:24px;'>{h_goal} : {a_goal}</span> {away_kr}"
                else: match_display = f"{home_kr} <span style='color:#888; font-size:16px; margin:0 10px;'>VS</span> {away_kr}"

                pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                odds_res = requests.get("https://v3.football.api-sports.io/odds", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                lineup_data = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                injuries_res = requests.get("https://v3.football.api-sports.io/injuries", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                
                h_inj = [translate_to_ko(inj['player']['name']) for inj in injuries_res if inj['team']['id'] == home_id]
                a_inj = [translate_to_ko(inj['player']['name']) for inj in injuries_res if inj['team']['id'] == away_id]

                if not pred_res: continue
                pred_data = pred_res[0]; comparison = pred_data.get('comparison', {})
                
                h_rank = pred_data.get('teams',{}).get('home',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                a_rank = pred_data.get('teams',{}).get('away',{}).get('league',{}).get('standings', [{}])[0].get('rank', 'N/A')
                h_goals_avg = pred_data.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                a_goals_avg = pred_data.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('for',{}).get('average',{}).get('total', '0')
                h_goals_against_avg = pred_data.get('teams',{}).get('home',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')
                a_goals_against_avg = pred_data.get('teams',{}).get('away',{}).get('league',{}).get('goals',{}).get('against',{}).get('average',{}).get('total', '0')

                win_prob = pred_data.get('predictions', {}).get('percent', {})
                p_h = win_prob.get('home', '33%').replace('%','')
                p_d = win_prob.get('draw', '33%').replace('%','')
                p_a = win_prob.get('away', '33%').replace('%','')

                h_vals = [safe_num(comparison.get('att', {}).get('home')), safe_num(comparison.get('def', {}).get('home')), safe_num(comparison.get('form', {}).get('home')), safe_num(comparison.get('h2h', {}).get('home')), safe_num(comparison.get('goals', {}).get('home')), safe_num(comparison.get('total', {}).get('home'))]
                a_vals = [safe_num(comparison.get('att', {}).get('away')), safe_num(comparison.get('def', {}).get('away')), safe_num(comparison.get('form', {}).get('away')), safe_num(comparison.get('h2h', {}).get('away')), safe_num(comparison.get('goals', {}).get('away')), safe_num(comparison.get('total', {}).get('away'))]
                
                is_custom = False
                if sum(h_vals) < 10 or sum(a_vals) < 10:
                    c_h_form, c_h_att, c_h_def = fetch_custom_team_stats(home_id, calc_season_year)
                    c_a_form, c_a_att, c_a_def = fetch_custom_team_stats(away_id, calc_season_year)
                    c_h_total = (c_h_att + c_h_def + c_h_form) / 3
                    c_a_total = (c_a_att + c_a_def + c_a_form) / 3
                    h_vals = [c_h_att, c_h_def, c_h_form, 50, c_h_att, c_h_total]
                    a_vals = [c_a_att, c_a_def, c_a_form, 50, c_a_att, c_a_total]
                    is_custom = True

                radar_html = create_html_radar(h_vals, a_vals, home_kr, away_kr, is_custom)
                lineup_html = get_lineup_table(home_kr, away_kr, lineup_data)
                detail_html = get_detailed_html(home_kr, away_kr, h_rank, a_rank, h_goals_avg, a_goals_avg, h_goals_against_avg, a_goals_against_avg, h_inj, a_inj)

                odds_h, odds_d, odds_a = 0.0, 0.0, 0.0
                if odds_res:
                    for bet in odds_res[0].get('bookmakers', [])[0].get('bets', []):
                        if bet['name'] == 'Match Winner':
                            for val in bet['values']:
                                if str(val['value']) == 'Home': odds_h = float(val['odd'])
                                elif str(val['value']) == 'Draw': odds_d = float(val['odd'])
                                elif str(val['value']) == 'Away': odds_a = float(val['odd'])
                            break
                
                h_power = (h_vals[0] + h_vals[2] + h_vals[3]) - (len(h_inj) * 3)
                a_power = (a_vals[0] + a_vals[2] + a_vals[3]) - (len(a_inj) * 3)

                pred_winner = "none"
                if h_power < 5 or a_power < 5:
                    if odds_h > 0 and odds_a > 0:
                        pred_winner, win_pick, pick_color = ("home", f"🟢 {home_kr} 승 (데이터 부족/배당 기준)", "#00E676") if odds_h < odds_a else ("away", f"🔵 {away_kr} 승 (데이터 부족/배당 기준)", "#4FC3F7")
                    else: pred_winner, win_pick, pick_color = "none", "⚠️ 데이터/배당 모두 누락 (패스)", "#888888"
                else:
                    if odds_h > 0 and odds_a > 0:
                        if odds_h < odds_a - 0.3:
                            pred_winner, win_pick, pick_color = ("away", f"🚨 정밀 데이터 역배픽: {away_kr} 승", "#ff5252") if a_power > h_power + 35 else ("home", f"🟢 {home_kr} 승 (정배당)", "#00E676")
                        elif odds_a < odds_h - 0.3:
                            pred_winner, win_pick, pick_color = ("home", f"🚨 정밀 데이터 역배픽: {home_kr} 승", "#ff5252") if h_power > a_power + 35 else ("away", f"🔵 {away_kr} 승 (정배당)", "#4FC3F7")
                        else:
                            if h_power > a_power + 15: pred_winner, win_pick, pick_color = "home", f"🟢 {home_kr} 전력 우세", "#00E676"
                            elif a_power > h_power + 15: pred_winner, win_pick, pick_color = "away", f"🔵 {away_kr} 전력 우세", "#4FC3F7"
                            else: pred_winner, win_pick, pick_color = "draw", "🟡 팽팽한 무승부", "#ff9800"
                    else:
                        if h_power > a_power + 15: pred_winner, win_pick, pick_color = "home", f"🟢 {home_kr} 전력 우세", "#00E676"
                        elif a_power > h_power + 15: pred_winner, win_pick, pick_color = "away", f"🔵 {away_kr} 전력 우세", "#4FC3F7"
                        else: pred_winner, win_pick, pick_color = "none", "⚠️ 데이터 박빙 (패스)", "#888888"

                if is_finished and pred_winner != "none":
                    actual = "home" if h_goal > a_goal else ("away" if a_goal > h_goal else "draw")
                    win_pick += " (적중)" if actual == pred_winner else " (미적중)"
                        
                odds_text = f"<b style='color:#ff9800;'>{odds_h}</b> | 무 <b>{odds_d}</b> | 원정 <b style='color:#ff9800;'>{odds_a}</b>" if odds_h > 0 else "해외 배당 미발매"
                stat_box = f"<span style='color:#aaa;'>해외 배당:</span> 홈 {odds_text}<br><span style='color:#aaa;'>최종 산출 파워:</span> {home_kr} <b>{int(h_power)}점</b> vs <b>{int(a_power)}점</b> {away_kr}"

                advice = "API 누락으로 자체 전력 계산을 수행했습니다." if is_custom else translate_to_ko(pred_data['predictions'].get('advice', '데이터 분석 완료'))
                
                under_over_val = pred_data['predictions'].get('under_over', '')
                if under_over_val and not is_custom:
                    over_under = f"🔥 예상 기준점: {under_over_val.replace('-', '').replace('+', '')} {'언더' if '-' in under_over_val else '오버'}"
                else:
                    goal_expect = h_vals[4] + a_vals[4]
                    over_under = "🔥 2.5 기준 오버 (자체예측)" if goal_expect >= 120 else "❄️ 2.5 기준 언더 (자체예측)"

                new_data_list.append({
                    "league": top_league_display, "match_display": match_display, "stat_box": stat_box,
                    "referee": referee, "venue": venue, "p_h": p_h, "p_d": p_d, "p_a": p_a,
                    "win_pick": win_pick, "pick_color": pick_color, "control_pick": advice, 
                    "over_under": over_under, "radar_html": radar_html, "lineup_html": lineup_html, "detail_html": detail_html
                })
        except: pass

    progress_bar.progress(1.0); status_text.text("✅ 궁극의 데이터 스캔 완료!"); time.sleep(1); status_text.empty(); progress_bar.empty()
    st.session_state['analyzed_data_list'] = new_data_list

if st.session_state.get('analyzed_data_list'):
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_data_list']):
        with cols[idx % 3]:
            prob_bar = f"""
            <div class='prob-text'><span>승 {data['p_h']}%</span><span>무 {data['p_d']}%</span><span>패 {data['p_a']}%</span></div>
            <div class='prob-container'>
                <div class='prob-home' style='width: {data['p_h']}%;'></div>
                <div class='prob-draw' style='width: {data['p_d']}%;'></div>
                <div class='prob-away' style='width: {data['p_a']}%;'></div>
            </div>
            """
            
            html_str = f"<div style='height: 100%;'><div class='card-box'><div><div class='league-txt'>{data['league']}</div><div class='match-txt'>{data['match_display']}</div><div class='referee-txt'>🏟️ {data['venue']} | 👨‍⚖️ 주심: {data['referee']}</div>{prob_bar}<div class='stat-bg'>{data['stat_box']}</div></div><div class='predict-txt'><div style='color: {data['pick_color']}; margin-bottom: 3px;'>🎯 {data['win_pick']}</div><div class='over-under'>{data['over_under']}</div><div class='ai-advice'>⚔️ 요약: {data['control_pick']}</div></div></div></div>"
            st.markdown(html_str, unsafe_allow_html=True)
            
            with st.expander("🔍 상세 분석 (부상/순위) & 선발 명단"):
                st.markdown(data['detail_html'], unsafe_allow_html=True)
                st.markdown(data['radar_html'], unsafe_allow_html=True)
                st.markdown(data['lineup_html'], unsafe_allow_html=True)
            st.write("")
elif st.session_state.get('analyzed_data_list') == []: st.markdown("")
