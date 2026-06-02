import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

custom_css = """
<style>
.stApp { background-color: #121212; }
.card-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px; }
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
.match-txt { color: #ffffff; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px; line-height: 1.4; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 14px; line-height: 1.6; text-align: center; margin-bottom: 15px;}
.predict-txt { color: #00E676; font-size: 16px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; line-height: 1.6; }
.wc-mode { color: #00d4ff; font-weight: bold; font-size: 13px; margin-top: 10px; border: 1px solid #00d4ff; padding: 5px; border-radius: 5px; display: inline-block; }
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

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 사전 승부 예측 AI (국대 스쿼드 분석 탑재)</h1>", unsafe_allow_html=True)
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
        
        is_national_match = (league_id in ["1", "10"]) # 국가대표 매치 확인
        
        querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
        
        try:
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            fixtures = res.get('response', [])
            
            for match in fixtures:
                fix_id = str(match['fixture']['id'])
                home_en = match['teams']['home']['name']
                away_en = match['teams']['away']['name']
                home_kr = translate_to_ko(home_en)
                away_kr = translate_to_ko(away_en)
                
                status_short = match['fixture']['status']['short']
                is_finished = status_short in ['FT', 'AET', 'PEN']
                is_live = status_short in ['1H', 'HT', '2H', 'ET', 'P']
                
                try: time_str = datetime.strptime(match['fixture']['date'][:16], "%Y-%m-%dT%H:%M").strftime("%H:%M")
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

                pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                if not pred_res: continue
                
                pred_data = pred_res[0]
                preds = pred_data.get('predictions', {})
                comparison = pred_data.get('comparison', {})
                
                form_h_val = safe_num(comparison.get('form', {}).get('home'))
                form_a_val = safe_num(comparison.get('form', {}).get('away'))
                att_h = str(comparison.get('att', {}).get('home', 'N/A'))
                att_a = str(comparison.get('att', {}).get('away', 'N/A'))

                h_pct = safe_num(preds.get('percent', {}).get('home'))
                a_pct = safe_num(preds.get('percent', {}).get('away'))
                d_pct = safe_num(preds.get('percent', {}).get('draw'))
                
                # 💡 타이브레이커 탑재: API가 50 vs 50을 줄 경우 '최근 폼' 수치로 강제 승부 결정
                if h_pct == a_pct and h_pct > 0:
                    if form_h_val > form_a_val: h_pct += 1.0
                    elif form_a_val > form_h_val: a_pct += 1.0

                if h_pct == 0 and a_pct == 0:
                    pred_winner, win_pick = "none", "⚠️ 데이터 분석 불가 (베팅 패스)"
                elif h_pct > a_pct:
                    pred_winner, win_pick = "home", f"🟢 {home_kr} 승리 유력"
                elif a_pct > h_pct:
                    pred_winner, win_pick = "away", f"🔵 {away_kr} 승리 유력"
                else:
                    pred_winner, win_pick = "draw", "🟡 팽팽한 무승부"

                if is_finished and pred_winner != "none":
                    if h_goal > a_goal: actual = "home"
                    elif a_goal > h_goal: actual = "away"
                    else: actual = "draw"
                    win_pick += " <span style='color:#ff9800;'>(적중)</span>" if actual == pred_winner else " <span style='color:#ff9800;'>(미적중)</span>"
                        
                # 💡 감독님 기획: A매치/월드컵 스쿼드 가치 변환 로직
                if is_national_match:
                    # 국가대표 매치 시, 공격력 지표를 '빅리그 출신 공격진 파괴력'으로 치환하여 해석
                    stat_box = f"<span style='color:#aaa;'>해외파 스쿼드 전력차:</span> {home_kr} <b>{form_h_val}%</b> vs <b>{form_a_val}%</b> {away_kr}<br>"
                    stat_box += f"<span style='color:#aaa;'>빅리그 핵심자원 공격력:</span> <b>{att_h}</b> vs <b>{att_a}</b>"
                    control_pick = f"🌍 국가대표 스쿼드 가치 기반 산출: {home_kr} {h_pct}% / {away_kr} {a_pct}%"
                else:
                    stat_box = f"<span style='color:#aaa;'>최근 폼:</span> {home_kr} <b>{form_h_val}%</b> vs <b>{form_a_val}%</b> {away_kr}<br>"
                    stat_box += f"<span style='color:#aaa;'>공격력:</span> <b>{att_h}</b> vs <b>{att_a}</b>"
                    advice = translate_to_ko(preds.get('advice', '데이터 분석 중'))
                    control_pick = f"💡 코멘트: {advice}"

                under_over_val = preds.get('under_over', '')
                if under_over_val and str(under_over_val).strip() != "":
                    uo_text = "언더 (저득점)" if "-" in under_over_val else "오버 (다득점)"
                    clean_val = under_over_val.replace('-', '').replace('+', '')
                    over_under = f"📊 기준점 {clean_val} {uo_text}"
                else:
                    over_under = "📊 언더/오버 기준점 미제공"

                new_html_list.append({
                    "league": top_league_display,
                    "match_display": match_display,
                    "stat_box": stat_box,
                    "win_pick": win_pick, 
                    "control_pick": control_pick, 
                    "over_under": over_under
                })
        except:
            pass

    progress_bar.progress(1.0)
    status_text.text("✅ 빅데이터 분석 완료!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

    st.session_state['analyzed_html_list'] = new_html_list

# 💡 버그 원천 차단: st.markdown 내부 문자열 들여쓰기 100% 제거
if st.session_state['analyzed_html_list']:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_html_list']):
        html_str = "<div class='card-box'>"
        html_str += f"<div class='league-txt'>{data['league']}</div>"
        html_str += f"<div class='match-txt'>{data['match_display']}</div>"
        html_str += f"<div class='stat-bg'>{data['stat_box']}</div>"
        html_str += f"<div class='predict-txt'>"
        html_str += f"🎯 {data['win_pick']}<br>"
        html_str += f"<span style='font-size: 14px; font-weight: normal; color: #00E676;'>"
        html_str += f"⚔️ {data['control_pick']}<br>"
        html_str += f"{data['over_under']}"
        html_str += f"</span></div></div>"
        
        with cols[idx % 3]:
            st.markdown(html_str, unsafe_allow_html=True)
elif st.session_state['analyzed_html_list'] == []:
    st.markdown("")
