import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import random

st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

# 🎨 UI CSS: 카드 높이 고정 및 검색 엔진 복구
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.stApp { background-color: #0e1117; }

/* 💡 핵심: 모든 카드 박스 높이를 강제 고정하여 정렬 유지 */
.card-box {
    background-color: #1e1e1e; padding: 20px; border-radius: 12px;
    border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); 
    margin-bottom: 25px;
    height: 520px; /* 모든 카드의 높이를 520px로 고정 */
    display: flex; flex-direction: column; justify-content: space-between;
}
.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; }
.match-txt { color: #ffffff; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 8px; }
.referee-txt { font-size: 11px; color: #888; text-align: center; margin-bottom: 15px; }
.stat-bg { background-color: #262730; padding: 12px; border-radius: 8px; color: #eeeeee; font-size: 13px; text-align: center; margin-bottom: 10px; border: 1px solid #444;}
.predict-txt { font-size: 14px; font-weight: bold; text-align: center; border-top: 1px dashed #555; padding-top: 10px; }

.ai-advice { font-size: 11px; color: #aaa; margin-top: 5px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.prob-container { display: flex; width: 100%; height: 6px; border-radius: 3px; overflow: hidden; margin: 8px 0; background-color: #333; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }
.prob-text { display: flex; justify-content: space-between; font-size: 10px; color: #aaa; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# (이하 기존 함수 로직 유지)
FOOTBALL_API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
HEADERS = {'x-apisports-key': FOOTBALL_API_KEY}

# [기존 함수들: translate_to_ko, safe_num, fetch_custom_team_stats, get_detailed_html 등 유지]
# (코드 공간 절약을 위해 생략하였으나 실제 app.py에는 그대로 두세요)

# ... (기존과 동일한 함수 생략) ...

# ==========================================
# 📺 메인 UI 렌더링
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 AI 통합 분석실 V27.2</h1>", unsafe_allow_html=True)

selected_sport = st.sidebar.radio("종목 선택", ["축구", "야구", "농구", "배구"], horizontal=True, label_visibility="collapsed")
selected_date = st.sidebar.date_input("날짜 선택", datetime.today())

if selected_sport == "축구":
    analyze_button = st.sidebar.button("⚽ 축구 분석 시작", use_container_width=True)
    # [리그 선택 체크박스들 동일]
    if analyze_button:
        # 💡 [핵심] new_data_list를 매번 새로 정의하고 session_state를 명확히 갱신
        st.session_state['analyzed_data_list'] = [] # 초기화
        # ... (축구 수집 로직 수행) ...
        # [데이터 수집 후 st.session_state['analyzed_data_list']에 append]
        st.rerun()

elif selected_sport == "야구":
    analyze_button = st.sidebar.button("⚾ 야구 분석 시작", use_container_width=True)
    # [야구 시뮬레이션 로직 동일]
    if analyze_button:
        # [데이터 수집 후 st.session_state['analyzed_data_list']에 append]
        st.rerun()

# [결과 출력 로직]
if st.session_state.get('analyzed_data_list'):
    cols = st.columns(3)
    for idx, data in enumerate(st.session_state['analyzed_data_list']):
        with cols[idx % 3]:
            # [카드 출력 로직 유지]
            st.markdown(html_str, unsafe_allow_html=True)
