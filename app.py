import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🔑 API 세팅
API_KEY = st.secrets["FOOTBALL_API_KEY"]
HEADERS = {'x-apisports-key': API_KEY}

# 번역 캐시
@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    try: return GoogleTranslator(source='en', target='ko').translate(text)
    except: return text

# 💡 뇌(Session State) 초기화
if 'analysis_data' not in st.session_state: st.session_state['analysis_data'] = None

st.title("🏆 라이브 AI 축구 승부 예측 PRO")

# 1. 사이드바 설정
st.sidebar.header("🔍 검색 설정")
selected_date = st.sidebar.date_input("📅 날짜 선택", datetime.today())
LEAGUE_MAP = {"1": "월드컵", "10": "A매치 친선전", "39": "프리미어리그", "140": "라리가", "135": "세리에A", "78": "분데스리가", "61": "리그1", "292": "K리그1"}
selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["39", "140", "292"])

# 2. 데이터 불러오기 로직 (뇌에 저장)
if st.sidebar.button("🚀 데이터 불러오기"):
    all_results = []
    url = "https://v3.football.api-sports.io/fixtures"
    for league_id in selected_leagues:
        res = requests.get(url, headers=HEADERS, params={"league": league_id, "season": str(selected_date.year), "date": selected_date.strftime('%Y-%m-%d')}).json()
        fixtures = res.get('response', [])
        for match in fixtures:
            all_results.append((league_id, match))
    st.session_state['analysis_data'] = all_results

# 3. 화면 그리기 (저장된 데이터를 기반으로 반복 출력)
if st.session_state['analysis_data']:
    cols = st.columns(3)
    col_idx = 0
    for league_id, match in st.session_state['analysis_data']:
        fix_id = str(match['fixture']['id'])
        home_kr = translate_to_ko(match['teams']['home']['name'])
        away_kr = translate_to_ko(match['teams']['away']['name'])
        
        with cols[col_idx % 3]:
            # 카드 디자인
            st.markdown(f"""
            <div style='background:#1e1e1e; padding:15px; border-radius:10px; border:1px solid #444; margin-bottom:15px;'>
                <div style='color:#ff9800; font-weight:bold;'>{LEAGUE_MAP[league_id]}</div>
                <div style='text-align:center; font-weight:bold; font-size:18px;'>{home_kr} vs {away_kr}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 여기서 분석 실행 버튼 (개별)
            if st.button(f"📊 분석 실행", key=fix_id):
                stats = requests.get("https://v3.football.api-sports.io/fixtures/statistics", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
                if stats:
                    # 간단 예측 로직 및 결과 출력
                    st.success("✅ 분석 완료!")
                    # 결과 카드 부분은 여기에 추가
            col_idx += 1
