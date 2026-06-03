import streamlit as st
import requests
from datetime import datetime
from deep_translator import GoogleTranslator
import time
import plotly.graph_objects as go

st.set_page_config(page_title="AI 축구 분석실", page_icon="⚽", layout="wide")

# 🎨 UI CSS: 박스 높이 고정 및 레이더 차트 영역 확보
st.markdown("""
<style>
.stApp { background-color: #121212; }
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 10px;
    border: 1px solid #444; box-shadow: 0 4px 8px rgba(0,0,0,0.5); margin-bottom: 20px;
    min-height: 380px; display: flex; flex-direction: column; justify-content: space-between;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; text-align: center; }
.match-txt { color: #ffffff; font-size: 19px; font-weight: bold; text-align: center; margin-bottom: 10px; }
.stat-bg { background-color: #2a2a2a; padding: 15px; border-radius: 8px; color: #eeeeee; font-size: 13px; line-height: 1.6; text-align: center; margin-bottom: 10px;}
.predict-txt { color: #00E676; font-size: 15px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 15px; line-height: 1.6; }
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

# 💡 고정 크기 레이더 차트 생성 함수
def create_fixed_radar_chart(home_kr, away_kr, comparison):
    categories = ['공격력', '수비력', '최근 폼', '상대전적', '득점기대', '전술']
    h_vals = [safe_num(comparison.get('att', {}).get('home')), safe_num(comparison.get('def', {}).get('home')),
              safe_num(comparison.get('form', {}).get('home')), safe_num(comparison.get('h2h', {}).get('home')),
              safe_num(comparison.get('goals', {}).get('home')), safe_num(comparison.get('poisson', {}).get('home'))]
    a_vals = [safe_num(comparison.get('att', {}).get('away')), safe_num(comparison.get('def', {}).get('away')),
              safe_num(comparison.get('form', {}).get('away')), safe_num(comparison.get('h2h', {}).get('away')),
              safe_num(comparison.get('goals', {}).get('away')), safe_num(comparison.get('poisson', {}).get('away'))]
    
    # 💡 데이터가 너무 없으면(모두 0이면) 차트 생성 중단
    if sum(h_vals) < 50 and sum(a_vals) < 50: return None

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=h_vals, theta=categories, fill='toself', name=home_kr, line_color='#2196F3'))
    fig.add_trace(go.Scatterpolar(r=a_vals, theta=categories, fill='toself', name=away_kr, line_color='#F44336'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]), bgcolor='#111'),
        showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'), margin=dict(l=40, r=40, t=40, b=40), height=300
    )
    return fig

st.markdown("<h1 style='text-align: center; color: #00E676;'>🏆 정밀 전력 분석 대시보드</h1>", unsafe_allow_html=True)
st.markdown("---")

selected_leagues = st.sidebar.multiselect("⚽ 리그 선택", options=list(LEAGUE_MAP.keys()), format_func=lambda x: LEAGUE_MAP[x], default=["39", "140"])

if st.sidebar.button("🚀 정밀 분석 시작"):
    url = "https://v3.football.api-sports.io/fixtures"
    new_data = []
    
    for league_id in selected_leagues:
        res = requests.get(url, headers=HEADERS, params={"league": league_id, "season": "2026", "date": datetime.today().strftime('%Y-%m-%d')}).json()
        for match in res.get('response', []):
            fix_id = str(match['fixture']['id'])
            home_kr = translate_to_ko(match['teams']['home']['name'])
            away_kr = translate_to_ko(match['teams']['away']['name'])
            
            # 예측 데이터
            pred_res = requests.get("https://v3.football.api-sports.io/predictions", headers=HEADERS, params={"fixture": fix_id}).json().get('response', [])
            if not pred_res: continue
            
            fig = create_fixed_radar_chart(home_kr, away_kr, pred_res[0].get('comparison', {}))
            
            # 예측값
            preds = pred_res[0].get('predictions', {})
            h_pct = safe_num(preds.get('percent', {}).get('home'))
            a_pct = safe_num(preds.get('percent', {}).get('away'))
            
            win_pick = f"🟢 {home_kr} 우세 ({h_pct}%)" if h_pct > a_pct + 1 else (f"🔵 {away_kr} 우세 ({a_pct}%)" if a_pct > h_pct + 1 else "🟡 초박빙")
            
            new_data.append({
                "league": LEAGUE_MAP[league_id],
                "match": f"{home_kr} VS {away_kr}",
                "win_pick": win_pick,
                "radar_fig": fig
            })
    st.session_state['data'] = new_data

# 화면 출력
if 'data' in st.session_state:
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['data']):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class='card-box'>
                <div class='league-txt'>{data['league']}</div>
                <div class='match-txt'>{data['match']}</div>
                <div class='predict-txt'>🎯 {data['win_pick']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("▶ 상세 전력 레이더 차트"):
                if data['radar_fig']:
                    st.plotly_chart(data['radar_fig'], use_container_width=True)
                else:
                    st.markdown("<div style='text-align:center; padding:50px; color:#ff5252;'>⚠️ 데이터 부족: 분석 패스</div>", unsafe_allow_html=True)
