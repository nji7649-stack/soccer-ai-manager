import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator

# 🎨 웹사이트 기본 설정
st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🔑 스트림릿 금고에서 열쇠 꺼내기
API_KEY = st.secrets["FOOTBALL_API_KEY"]
HEADERS = {'x-apisports-key': API_KEY}

# 🌐 한글 번역기능 (속도 향상을 위해 캐시 사용)
@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    try:
        return GoogleTranslator(source='en', target='ko').translate(text)
    except:
        return text

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

st.title("🏆 라이브 AI 축구 승부 예측 PRO")
st.markdown("전 세계 모든 축구 경기를 클릭 한 번으로 정밀 분석합니다.")
st.markdown("---")

# 🔍 왼쪽 사이드바 (검색 메뉴)
st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())

LEAGUE_MAP = {
    "1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", 
    "140": "라리가", "135": "세리에A", "78": "분데스리가", 
    "61": "리그1", "292": "K리그1"
}

selected_leagues = st.sidebar.multiselect(
    "⚽ 리그 선택", 
    options=list(LEAGUE_MAP.keys()), 
    format_func=lambda x: LEAGUE_MAP[x],
    default=["39", "140", "292"]
)

# 💡 1. 버튼을 누르면 데이터를 불러와서 '로봇의 뇌(session_state)'에 영구 저장합니다.
if st.sidebar.button("🚀 데이터 불러오기"):
    if not selected_leagues:
        st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요.")
        st.stop()
        
    url = "https://v3.football.api-sports.io/fixtures"
    
    with st.spinner("전 세계 경기 일정을 불러오는 중입니다..."):
        all_fixtures = {}
        for league_id in selected_leagues:
            querystring = {"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d'), "timezone": "Asia/Seoul"}
            res = requests.get(url, headers=HEADERS, params=querystring, timeout=10).json()
            
            if 'errors' in res and res['errors']:
                st.error(f"🚨 API 에러 발생: {res['errors']}")
                continue

            fixtures = res.get('response', [])
            if fixtures:
                all_fixtures[league_id] = fixtures
        
        # 불러온 경기 목록을 메모리에 저장!
        st.session_state['saved_fixtures'] = all_fixtures

# 💡 2. 메모리에 데이터가 있다면 화면이 깜빡여도 날아가지 않고 계속 보여줍니다.
if 'saved_fixtures' in st.session_state:
    for league_id, fixtures in st.session_state['saved_fixtures'].items():
        st.subheader(f"🏟️ {LEAGUE_MAP[league_id]} ({len(fixtures)}경기)")
        
        for match in fixtures:
            fix_id = str(match['fixture']['id'])
            home_kr = translate_to_ko(match['teams']['home']['name'])
            away_kr = translate_to_ko(match['teams']['away']['name'])
            status = match['fixture']['status']['short']
            
            with st.expander(f"⚽ {home_kr} vs {away_kr} [{status}]"):
                # 내부 버튼을 눌러도 화면이 날아가지 않습니다!
                if st.button(f"📊 '{home_kr} vs {away_kr}' 정밀 분석 실행", key=fix_id):
                    with st.spinner("라인업 및 세부 스탯 추출 중..."):
                        stats_res = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json()
                        lineup_res = requests.get("https://v3.football.api-sports.io/fixtures/lineups", headers=HEADERS, params={"fixture": fix_id}).json()

                        if 'errors' in stats_res and stats_res['errors']:
                            st.error(f"🚨 스탯 API 권한 에러: {stats_res['errors']}")
                        else:
                            stats_data = stats_res.get('response', [])
                            lineup_data = lineup_res.get('response', [])

                            if not stats_data or len(stats_data) < 2:
                                st.info("아직 이 경기의 세부 스탯이 서버에 등록되지 않았습니다. (경기 전이거나 데이터 제공이 안 되는 경기)")
                            else:
                                h_stats = stats_data[0]['statistics']
                                a_stats = stats_data[1]['statistics']

                                h_poss = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Ball Possession'), 0))
                                h_shot = safe_num(next((item['value'] for item in h_stats if item['type'] == 'Shots on Goal'), 0))
                                a_poss = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Ball Possession'), 0))
                                a_shot = safe_num(next((item['value'] for item in a_stats if item['type'] == 'Shots on Goal'), 0))

                                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                                
                                win_pick = f"🟢 {home_kr} 우세" if h_score > a_score + 2.5 else (f"🔵 {away_kr} 우세" if a_score > h_score + 2.5 else "🟡 무승부 접전")
                                control_pick = f"{home_kr} 주도" if h_poss > a_poss + 15 else (f"{away_kr} 주도" if a_poss > h_poss + 15 else "팽팽한 중원 싸움")
                                total_shots = h_shot + a_shot
                                over_under = "🔥 오버 (다득점)" if total_shots >= 9 else ("❄️ 언더 (저득점)" if total_shots <= 5 else "⚖️ 언오버 팽팽")

                                h_lineup = ", ".join([p['player']['name'] for p in lineup_data[0]['startXI']]) if lineup_data else "명단 미발표"
                                a_lineup = ", ".join([p['player']['name'] for p in lineup_data[1]['startXI']]) if lineup_data and len(lineup_data) > 1 else "명단 미발표"

                                st.success(f"🎯 **AI 최종 예측:** {win_pick} | {control_pick} | {over_under}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"### 🏠 {home_kr}")
                                    st.metric("점유율", f"{h_poss}%")
                                    st.metric("유효슈팅", f"{h_shot}개")
                                    st.caption(f"🏃 선발 명단:\n{h_lineup}")
                                with col2:
                                    st.markdown(f"### ✈️ {away_kr}")
                                    st.metric("점유율", f"{a_poss}%")
                                    st.metric("유효슈팅", f"{a_shot}개")
                                    st.caption(f"🏃 선발 명단:\n{a_lineup}")
