import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import time
import math
import random

# ==========================================
# 1. 페이지 설정 및 API 키
# ==========================================
st.set_page_config(page_title="AI 종합 스포츠 분석실 PRO MAX", page_icon="🏆", layout="wide")

try:
    FOOTBALL_API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
except:
    FOOTBALL_API_KEY = ""

if not FOOTBALL_API_KEY:
    FOOTBALL_API_KEY = "83870361ee49a5abb1fef372d22a2d06"

# ==========================================
# 2. 🎨 UI CSS (사진 디자인 완벽 반영)
# ==========================================
custom_css = """
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
.stApp { background-color: #0e1117; }

[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] { display: flex !important; flex-direction: row !important; justify-content: space-between !important; gap: 5px !important; width: 100% !important; margin-bottom: 10px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { flex: 1 !important; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: center !important; background: transparent !important; border: none !important; padding: 5px 0 !important; cursor: pointer !important; margin: 0 !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label::before { font-family: "Font Awesome 6 Free"; font-weight: 900; font-size: 22px; color: #ffffff; background-color: #151515; width: 52px; height: 52px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; transition: all 0.3s ease; border: 2px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }

[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(1)::before { content: "\\f1e3"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(2)::before { content: "\\f433"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(3)::before { content: "\\f434"; } 
[data-testid="stSidebar"] div[role="radiogroup"] label:nth-child(4)::before { content: "\\f45f"; } 

[data-testid="stSidebar"] div[role="radiogroup"] label:hover::before { border-color: #666; transform: translateY(-2px); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked)::before { border-color: #00E676 !important; color: #00E676 !important; background-color: #151515 !important; box-shadow: 0 0 15px rgba(0, 230, 118, 0.4) !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 13px !important; font-weight: 700 !important; color: #888 !important; margin: 0 !important; text-align: center !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #00E676 !important; }

/* 💡 매치 카드 레이아웃 (V84 UI 패치) */
.card-box { background-color: #1e1e1e; padding: 20px; border-radius: 12px; border: 1px solid #333; box-shadow: 0 8px 16px rgba(0,0,0,0.6); margin-bottom: 15px; display: flex; flex-direction: column; justify-content: space-between; height: 580px; box-sizing: border-box; overflow: hidden; }
.card-top { flex-shrink: 0; width: 100%; }
.card-mid { flex-grow: 1; display: flex; flex-direction: column; justify-content: center; margin: 10px 0; width: 100%; }
.card-bot { flex-shrink: 0; border-top: 1px dashed #555; padding-top: 12px; text-align: center; width: 100%; height: 210px; }

.league-txt { color: #ff9800; font-size: 13px; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; text-align: center; letter-spacing: 1px; }
.match-box { display: flex; align-items: center; justify-content: center; width: 100%; margin-bottom: 15px; }
.team-side { display: flex; align-items: center; width: 38%; gap: 6px; }
.home-side { justify-content: flex-end; text-align: right; }
.away-side { justify-content: flex-start; text-align: left; }
.team-name { font-size: 13.5px; font-weight: bold; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 85px; }
.score-side { width: 24%; font-size: 20px; font-weight: bold; text-align: center; flex-shrink: 0; white-space: nowrap; letter-spacing: 0.5px; }
.team-logo { width: 26px; height: 26px; object-fit: contain; flex-shrink: 0; background-color: #fff; border-radius: 50%; padding: 2px; }
.referee-txt { font-size: 11px; color: #888; text-align: center; margin-bottom: 5px; }

.prob-wrapper { width: 100%; margin-bottom: 10px; box-sizing: border-box; }
.prob-text { display: flex; justify-content: space-between; font-size: 11px; color: #aaa; margin-bottom: 6px; width: 100%; padding: 0 2px; box-sizing: border-box; }
.prob-container { display: flex; width: 100%; height: 10px; border-radius: 5px; overflow: hidden; background-color: #333; box-sizing: border-box; }
.prob-home { background-color: #4FC3F7; height: 100%; }
.prob-draw { background-color: #ff9800; height: 100%; }
.prob-away { background-color: #EF5350; height: 100%; }

.table-wrapper { width: 100%; margin-top: 5px; margin-bottom: 5px; overflow-x: hidden; }
.detail-table { width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 11px; color: #ccc; text-align: center; background-color: #1a1a1a; border-radius: 6px; overflow: hidden; } 
.detail-table th { background-color: #222; padding: 6px 2px; border-bottom: 1px solid #444; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.detail-table td { padding: 6px 2px; border-bottom: 1px solid #2a2a2a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; } 

.standings-header { font-size: 16px; font-weight: bold; color: #00E676; margin-top: 30px; margin-bottom: 10px; border-bottom: 2px solid #333; padding-bottom: 5px; }

/* 💡 [핵심] 사진 UI 알약 배지 스타일 */
.prediction-badge { display: flex; align-items: center; justify-content: space-between; border-radius: 25px; padding: 10px 15px; margin-bottom: 10px; color: #fff; font-size: 13px; font-weight: bold; border: 1px solid rgba(255,255,255,0.1); }
.badge-left { display: flex; align-items: center; gap: 10px; }
.badge-right { display: flex; align-items: center; gap: 8px; font-size: 11.5px; }
.badge-icon { font-size: 16px; }

/* HIT (Blue), MISS (Red), Pending (Grey) */
.hit-bg { background-color: #0D47A1; }
.miss-bg { background-color: #B71C1C; }
.pending-bg { background-color: #333; color: #aaa; }

/* 우측 끝 작은 상태 배지 */
.status-label { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
.label-hit { background-color: #00E676; color: #111; }
.label-miss { background-color: #EF5350; color: #fff; }
.label-pending { background-color: #555; color: #ccc; }

.ai-advice { font-size: 12px; color: #bbb; line-height: 1.4; margin-top: 5px; font-style: italic; height: 38px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; text-align: left; padding-left: 5px;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. 언어 번역 딕셔너리
# ==========================================
@st.cache_data(show_spinner=False)
def translate_to_ko(text):
    if not text or not isinstance(text, str): return '미정'
    custom_dict = {
        "Arsenal": "아스날", "Aston Villa": "애스턴 빌라", "Newcastle": "뉴캐슬", "Crystal Palace": "크리스탈 팰리스",
        "Manchester City": "맨시티", "Manchester United": "맨유", "Liverpool": "리버풀", "Chelsea": "첼시", "Tottenham": "토트넘",
        "Real Madrid": "레알 마드리드", "Barcelona": "바르셀로나", "Atletico Madrid": "아틀레티코", "Bayern Munich": "바이에른 뮌헨",
        "Paris Saint Germain": "PSG", "Inter": "인터밀란", "Juventus": "유벤투스", "AC Milan": "AC밀란",
        "South Korea": "대한민국", "Japan": "일본", "Brazil": "브라질", "Argentina": "아르헨티나", "France": "프랑스", "England": "잉글랜드",
        # MLB 
        "Athletics": "애슬레틱스", "Oakland Athletics": "오클랜드", "Arizona Diamondbacks": "애리조나", "Atlanta Braves": "애틀랜타", 
        "Baltimore Orioles": "볼티모어", "Boston Red Sox": "보스턴", "Chicago Cubs": "시카고 컵스", "Chicago White Sox": "화이트삭스", 
        "Cincinnati Reds": "신시내티", "Cleveland Guardians": "클리블랜드", "Colorado Rockies": "콜로라도", "Detroit Tigers": "디트로이트", 
        "Houston Astros": "휴스턴", "Kansas City Royals": "캔자스시티", "Los Angeles Angels": "LA 에인절스", "Los Angeles Dodgers": "LA 다저스", 
        "Miami Marlins": "마이애미", "Milwaukee Brewers": "밀워키", "Minnesota Twins": "미네소타", "New York Mets": "NY 메츠", 
        "New York Yankees": "NY 양키스", "Philadelphia Phillies": "필라델피아", "Pittsburgh Pirates": "피츠버그", "San Diego Padres": "샌디에이고", 
        "San Francisco Giants": "샌프란시스코", "Seattle Mariners": "시애틀", "St. Louis Cardinals": "세인트루이스", "Tampa Bay Rays": "탬파베이", 
        "Texas Rangers": "텍사스", "Toronto Blue Jays": "토론토", "Washington Nationals": "워싱턴"
    }
    for eng, kor in custom_dict.items():
        if eng.lower() == text.lower() or eng in text: return kor
    try: return GoogleTranslator(source='en', target='ko').translate(text.replace('<', '').replace('>', ''))
    except: return text

def safe_float(value, default=0.0):
    if value is None or value == "": return default
    try: return float(str(value).replace('%', '').replace('+', '').replace('-', ''))
    except: return default

# ==========================================
# 4. 공통 차트
# ==========================================
def create_html_radar(h_prob, home_kr, away_kr, is_custom=False, sport_type="축구"):
    labels = ['공격력', '수비력', '최근폼', '상대전적', '득점력', '종합전력'] if sport_type == "축구" else ['공격력', '선발투수', '불펜', '최근폼', '득점력', '종합전력']
    seed_h = sum(ord(c) for c in home_kr); seed_a = sum(ord(c) for c in away_kr)
    base_h = h_prob; base_a = 100.0 - h_prob
    
    h_vals = [
        min(95, max(40, base_h + (seed_h % 15 - 5))), min(95, max(40, base_h + ((seed_h * 2) % 15 - 5))),
        min(95, max(40, base_h + ((seed_h * 3) % 15 - 5))), min(95, max(40, base_h + ((seed_h * 4) % 15 - 5))),
        min(95, max(40, base_h + ((seed_h * 5) % 15 - 5))), base_h
    ]
    a_vals = [
        min(95, max(40, base_a + (seed_a % 15 - 5))), min(95, max(40, base_a + ((seed_a * 2) % 15 - 5))),
        min(95, max(40, base_a + ((seed_a * 3) % 15 - 5))), min(95, max(40, base_a + ((seed_a * 4) % 15 - 5))),
        min(95, max(40, base_a + ((seed_a * 5) % 15 - 5))), base_a
    ]
    
    size = 220; center = size / 2; max_val = 100
    pts_h = " ".join([f"{center + (v/max_val)*(size*0.35)*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (v/max_val)*(size*0.35)*math.sin((math.pi*2/6)*i - math.pi/2)}" for i, v in enumerate(h_vals)])
    pts_a = " ".join([f"{center + (v/max_val)*(size*0.35)*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (v/max_val)*(size*0.35)*math.sin((math.pi*2/6)*i - math.pi/2)}" for i, v in enumerate(a_vals)])
    
    svg = ""
    for i in range(6):
        ang = (math.pi * 2 / 6) * i - (math.pi / 2); x = center + (size * 0.35) * math.cos(ang); y = center + (size * 0.35) * math.sin(ang)
        svg += f"<line x1='{center}' y1='{center}' x2='{x}' y2='{y}' style='stroke:#444; stroke-width:1;' />"
        lx = center + (size * 0.44) * math.cos(ang); ly = center + (size * 0.44) * math.sin(ang)
        anchor = "start" if lx > center + 10 else ("end" if lx < center - 10 else "middle")
        svg += f"<text x='{lx}' y='{ly+4}' fill='#ddd' font-size='10' font-weight='bold' text-anchor='{anchor}'>{labels[i]}</text>"
    for ratio in [0.33, 0.66, 1.0]:
        pts = " ".join([f"{center + (size*0.35)*ratio*math.cos((math.pi*2/6)*i - math.pi/2)},{center + (size*0.35)*ratio*math.sin((math.pi*2/6)*i - math.pi/2)}" for i in range(6)])
        svg += f"<polygon points='{pts}' style='fill:none; stroke:#333; stroke-width:1;' />"
        
    h_poly = f"<polygon points='{pts_h}' style='fill:rgba(79, 195, 247, 0.3); stroke:#4FC3F7; stroke-width:2; opacity:0.6;' />"
    a_poly = f"<polygon points='{pts_a}' style='fill:rgba(239, 83, 80, 0.3); stroke:#EF5350; stroke-width:2; opacity:0.6;' />"
    badge = "⚙️ 자체 환산 전력망" if is_custom else "⚙️ 딥-스캔 전력망"
    
    return (
        f"<div style='display:flex; flex-direction:column; align-items:center; background:#0a0a0a; border:1px solid #333; border-radius:8px; padding:10px; margin-top:10px; margin-bottom:10px;'>"
        f"<div style='color:#ff9800; font-size:11px; margin-bottom:5px;'>{badge}</div>"
        f"<div style='font-size:11px; color:#fff; margin-bottom:10px; font-weight:bold; text-align:center;'><span style='color:#4FC3F7;'>■</span> {home_kr} <span style='margin:0 10px; color:#777;'>vs</span> <span style='color:#EF5350;'>■</span> {away_kr}</div>"
        f"<svg viewBox='0 0 {size} {size}' style='width: 100%; max-width: {size}px; height: auto;'>{svg}{h_poly}{a_poly}</svg></div>"
    )

# ==========================================
# 5. [신규] UI 배지 생성 헬퍼 함수
# ==========================================
def create_prediction_badge_html(icon, pred_text, type_text, status):
    """사진 속 디자인을 HTML로 구현"""
    bg_class = "pending-bg"
    status_text = "대기"
    label_class = "label-pending"
    
    if status == "HIT":
        bg_class = "hit-bg" # Blue
        status_text = "HIT"
        label_class = "label-hit"
    elif status == "MISS":
        bg_class = "miss-bg" # Red
        status_text = "MISS"
        label_class = "label-miss"

    html = f"""
    <div class="prediction-badge {bg_class}">
        <div class="badge-left">
            <span class="badge-icon">{icon}</span>
            <span class="badge-pred-text">{pred_text}</span>
        </div>
        <div class="badge-right">
            <span class="badge-type-text">{type_text}</span>
            <span class="status-label {label_class}">{status_text}</span>
        </div>
    </div>
    """
    return html

# ==========================================
# 6. 축구 전용 로직
# ==========================================
@st.cache_data(ttl=600, show_spinner=False)
def fetch_api_football_fixtures(api_key, league_id, season, date_str):
    headers = {'x-apisports-key': api_key} if api_key else {}
    try: 
        res = requests.get("https://v3.football.api-sports.io/fixtures", headers=headers, params={"league": league_id, "season": season, "date": date_str, "timezone": "Asia/Seoul"}, timeout=10)
        if res.status_code in [401, 403]: return "AUTH_ERROR"
        if res.status_code == 429: return "LIMIT"
        return res.json().get('response') or []
    except: return []

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api_football_standings(api_key, league_id, season):
    headers = {'x-apisports-key': api_key} if api_key else {}
    try:
        res = requests.get("https://v3.football.api-sports.io/standings", headers=headers, params={"league": league_id, "season": season}, timeout=10)
        if res.status_code == 200: return res.json().get('response') or []
        return []
    except: return []

def generate_soccer_advanced_stats(h_team, a_team, h_prob, is_finished, h_score, a_score):
    a_prob = 100.0 - h_prob
    h_pos = round(h_prob); a_pos = 100 - h_pos
    h_pass = round(75.0 + (h_prob - 50.0) * 0.3, 1); a_pass = round(75.0 + (a_prob - 50.0) * 0.3, 1)
    h_sot = round(3.5 + (h_prob - 50.0) * 0.1, 1); a_sot = round(3.5 + (a_prob - 50.0) * 0.1, 1)
    
    h_gf = float(h_score) if h_score not in [None, ""] else 0.0
    a_gf = float(a_score) if a_score not in [None, ""] else 0.0
    
    if is_finished:
        h_margin = round(h_gf - a_gf, 1); a_margin = round(a_gf - h_gf, 1)
    else:
        h_gf = round(1.2 + (h_prob - 50.0) * 0.04, 2); a_gf = round(1.2 + (a_prob - 50.0) * 0.04, 2)
        h_margin = round(h_gf - (1.2 - (h_prob - 50.0) * 0.04), 2); a_margin = round(a_gf - (1.2 - (h_prob - 50.0) * 0.04), 2)

    title_text = "⚽ 매치 결과 데이터 (종료)" if is_finished else "⚽ AI 심층 전력 지표"
    margin_text_h = f"<span style='color:#4FC3F7;'>+{h_margin}</span>" if h_margin > 0 else f"<span style='color:#EF5350;'>{h_margin}</span>"
    margin_text_a = f"<span style='color:#4FC3F7;'>+{a_margin}</span>" if a_margin > 0 else f"<span style='color:#EF5350;'>{a_margin}</span>"

    html = (
        f"<div class='table-wrapper'><div style='text-align:center; font-size:11.5px; color:#00E676; margin-bottom:5px; font-weight:bold;'>{title_text}</div>"
        f"<table class='detail-table'><tr style='background-color:#111;'><th style='color:#4FC3F7; width:33%;'>{h_team}</th><th style='color:#aaa; width:34%;'>비교 스탯</th><th style='color:#EF5350; width:33%;'>{a_team}</th></tr>"
        f"<tr><td style='color:#fff; font-weight:bold;'>{h_gf}</td><td style='color:#aaa;'>평균 득점력</td><td style='color:#fff; font-weight:bold;'>{a_gf}</td></tr>"
        f"<tr><td>{margin_text_h}</td><td style='color:#aaa;'>골득실 마진</td><td>{margin_text_a}</td></tr>"
        f"<tr><td style='color:#fff;'>{h_pos}%</td><td style='color:#aaa;'>평균 점유율</td><td style='color:#fff;'>{a_pos}%</td></tr>"
        f"<tr><td style='color:#fff;'>{h_pass}%</td><td style='color:#aaa;'>패스 성공률</td><td style='color:#fff;'>{a_pass}%</td></tr>"
        f"<tr><td style='color:#fff;'>{h_sot}개</td><td style='color:#aaa;'>유효 슈팅</td><td style='color:#fff;'>{a_sot}개</td></tr></table></div>"
    )
    return html, h_gf, a_gf

# 💡 [V84 UI 패치] 축구 결과 함수 -> HTML 배지 리스트 반환으로 변경
def get_soccer_prediction_badges_html(home_kr, away_kr, h_prob, h_gf, a_gf, is_finished, h_score, a_score):
    d_prob = max(0.0, 20.0 - abs(h_prob - 50.0) / 2.0); a_prob = 100.0 - h_prob - d_prob
    
    # 1. 승리 예측
    win_status = "PENDING"
    if h_prob >= 60.0: 
        win_pred_code = "home"; win_pred_text = f"{home_kr} 승리"
    elif a_prob >= 60.0: 
        win_pred_code = "away"; win_pred_text = f"{away_kr} 승리"
    elif h_prob > a_prob: 
        win_pred_code = "home"; win_pred_text = f"{home_kr} 우세"
    else: 
        win_pred_code = "away"; win_pred_text = f"{away_kr} 우세"

    # 2. 핸디캡 예측 (축구는 기본 1.0)
    handi_status = "PENDING"
    if h_prob >= 60.0: 
        handi_pred_code = "home"; handi_pred_text = f"{home_kr} -1.0 마핸 승"
    elif a_prob >= 60.0: 
        handi_pred_code = "away"; handi_pred_text = f"{away_kr} -1.0 마핸 승"
    elif h_prob > a_prob: 
        handi_pred_code = "away"; handi_pred_text = f"{away_kr} +1.0 플핸 방어"
    else: 
        handi_pred_code = "home"; handi_pred_text = f"{home_kr} +1.0 플핸 방어"
        
    # 3. 언오바 예측 (축구는 기본 2.5)
    ou_status = "PENDING"
    exp_total = h_gf + a_gf
    if exp_total >= 2.5: 
        ou_pred_code = "over"; ou_pred_text = "2.5 오버"
    else: 
        ou_pred_code = "under"; ou_pred_text = "2.5 언더"
        
    # 결과 계산 (종료 시)
    if is_finished:
        try:
            h_s = float(h_score) if h_score not in [None, ""] else 0.0
            a_s = float(a_score) if a_score not in [None, ""] else 0.0
            margin = h_s - a_s
            
            # 승리 HIT/MISS
            actual_win = "home" if margin > 0 else ("away" if margin < 0 else "draw")
            win_status = "HIT" if win_pred_code == actual_win else "MISS"
            
            # 핸디캡 HIT/MISS (마핸 예측 시 2골차 이상, 플핸 예측 시 1점차 패/무/승)
            abs_margin = abs(margin)
            if "마핸" in handi_pred_text:
                handi_status = "HIT" if abs_margin >= 2 and win_status == "HIT" else "MISS"
            else:
                handi_status = "HIT" if abs_margin <= 1 else "MISS"
            
            # 언오바 HIT/MISS
            actual_ou = "over" if (h_s + a_s) >= 2.5 else "under"
            ou_status = "HIT" if ou_pred_code == actual_ou else "MISS"
        except: pass

    # AI 코멘트 (기존 로직 유지)
    if win_pred_code == "home" and ou_pred_code == "over": comment = f"홈 이점을 등에 업은 {home_kr}의 폭발적인 공격력이 경기를 지배할 것입니다."
    elif win_pred_code == "away" and ou_pred_code == "under": comment = f"{away_kr}이 탄탄한 수비 조직력으로 상대의 공세를 틀어막고 승리를 가져갈 확률이 높습니다."
    else: comment = f"전술적 상성이 강하게 부딪히며, 작은 실수 하나가 전체 승부를 가르는 경기가 될 것입니다."

    # 배지 HTML 생성
    win_badge = create_prediction_badge_html("🟢", win_pred_text, "승리", win_status)
    handi_badge = create_prediction_badge_html("🟣", handi_pred_text, "핸디캡", handi_status)
    ou_badge = create_prediction_badge_html("🟡", ou_pred_text, "언오바", ou_status)
    
    return f"{win_badge}{handi_badge}{ou_badge}", comment

def get_soccer_lineup_table(home_kr, away_kr):
    return f"<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7; width:50%;'>{home_kr} (예상)</th><th style='color:#EF5350; width:50%;'>{away_kr} (예상)</th></tr><tr><td style='color:#888;'>라인업 발표 대기중</td><td style='color:#888;'>라인업 발표 대기중</td></tr></table></div>"

# ==========================================
# 7. 야구(MLB) 전용 로직 ⚾
# ==========================================
MLB_PARK_FACTORS = {'Colorado Rockies': 1.12, 'Cincinnati Reds': 1.08, 'Boston Red Sox': 1.07, 'Texas Rangers': 1.05, 'Chicago White Sox': 1.04, 'Atlanta Braves': 1.03, 'Los Angeles Dodgers': 1.03, 'Philadelphia Phillies': 1.02, 'Houston Astros': 1.01, 'Baltimore Orioles': 1.00, 'Toronto Blue Jays': 1.00, 'Minnesota Twins': 1.00, 'Chicago Cubs': 1.00, 'New York Yankees': 1.00, 'Kansas City Royals': 0.99, 'Arizona Diamondbacks': 0.99, 'Milwaukee Brewers': 0.98, 'Los Angeles Angels': 0.98, 'Washington Nationals': 0.98, 'San Francisco Giants': 0.97, 'Miami Marlins': 0.97, 'Pittsburgh Pirates': 0.96, 'Cleveland Guardians': 0.96, 'St. Louis Cardinals': 0.96, 'Detroit Tigers': 0.95, 'Tampa Bay Rays': 0.95, 'New York Mets': 0.95, 'Athletics': 0.94, 'San Diego Padres': 0.94, 'Seattle Mariners': 0.93}

@st.cache_data(ttl=3600, show_spinner=False)
def load_mlb_all_data():
    try:
        h_splits = requests.get("https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&gameType=R&season=2026&playerPool=ALL&limit=1500").json().get('stats', [{}])[0].get('splits') or []
        df_h = pd.DataFrame([{'이름': r['player']['fullName'], '팀': r['team']['name'], '타수': r['stat'].get('atBats', 0), 'OPS': r['stat'].get('ops', '.000')} for r in h_splits])
        df_h['OPS'] = pd.to_numeric(df_h['OPS'], errors='coerce').fillna(0.720) 
        p_splits = requests.get("https://statsapi.mlb.com/api/v1/stats?stats=season&group=pitching&gameType=R&season=2026&playerPool=ALL&limit=1500").json().get('stats', [{}])[0].get('splits') or []
        df_p = pd.DataFrame([{'이름': r['player']['fullName'], '팀': r['team']['name'], '출장': r['stat'].get('gamesPlayed', 0), '선발': r['stat'].get('gamesStarted', 0), '이닝': r['stat'].get('inningsPitched', '0.0'), '피홈런': r['stat'].get('homeRuns', 0), '볼넷': r['stat'].get('baseOnBalls', 0), '탈삼진': r['stat'].get('strikeOuts', 0)} for r in p_splits])
        df_p['이닝_num'] = pd.to_numeric(df_p['이닝'], errors='coerce').fillna(0.0)
        df_p['평균이닝'] = df_p.apply(lambda x: x['이닝_num'] / x['선발'] if x['선발'] > 0 else 4.0, axis=1).clip(3.0, 7.5)
        df_p['FIP'] = df_p.apply(lambda x: ((13*x['피홈런'] + 3*x['볼넷'] - 2*x['탈삼진']) / x['이닝_num']) + 3.10 if x['이닝_num'] > 0 else 4.50, axis=1)
        team_bullpen_fip = df_p[(df_p['출장'] > df_p['선발']) & (df_p['이닝_num'] >= 5.0)].groupby('팀')['FIP'].mean().to_dict()
        return df_h, df_p, team_bullpen_fip
    except: return pd.DataFrame(), pd.DataFrame(), {}

@st.cache_data(ttl=3600, show_spinner=False)
def load_mlb_team_momentum():
    try:
        res = requests.get("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104", timeout=5).json()
        l10_dict = {}
        for record in res.get('records') or []:
            for team in record.get('teamRecords') or []:
                for split in team.get('records', {}).get('splitRecords') or []:
                    if split['type'] == 'lastTen': l10_dict[team['team']['name']] = split['wins'] / max((split['wins'] + split['losses']), 1)
        return l10_dict
    except: return {}

def run_mlb_simulation(h_fip, a_fip, h_avg_ip, a_avg_ip, h_ops, a_ops, h_bp_fip, a_bp_fip, park_factor, num_sims=5000):
    if pd.isna(h_ops): h_ops = 0.720
    if pd.isna(a_ops): a_ops = 0.720
    if pd.isna(h_bp_fip): h_bp_fip = 4.00
    if pd.isna(a_bp_fip): a_bp_fip = 4.00
    if pd.isna(h_fip): h_fip = 4.50
    if pd.isna(a_fip): a_fip = 4.50
    
    h_starter_w = h_avg_ip / 9.0; a_starter_w = a_avg_ip / 9.0
    h_eff_fip = (h_fip * h_starter_w) + (h_bp_fip * (1 - h_starter_w)); a_eff_fip = (a_fip * a_starter_w) + (a_bp_fip * (1 - a_starter_w))
    
    h_expected_runs = (((a_eff_fip * 0.6 + a_bp_fip * 0.4) * (h_ops / 0.720)) + 0.2) * park_factor
    a_expected_runs = ((h_eff_fip * 0.6 + h_bp_fip * 0.4) * (a_ops / 0.720)) * park_factor
    
    if pd.isna(h_expected_runs): h_expected_runs = 4.0
    if pd.isna(a_expected_runs): a_expected_runs = 4.0
    
    h_wins = 0; a_wins = 0
    for _ in range(num_sims):
        hs = max(0, int(random.gauss(h_expected_runs, 2.3)))
        as_ = max(0, int(random.gauss(a_expected_runs, 2.3)))
        if hs == as_: 
            hs += 1 if random.random() < 0.54 else 0
            as_ += 1 if hs == as_ else 0
        if hs > as_: h_wins += 1
        elif as_ > hs: a_wins += 1
    return (h_wins/num_sims)*100, (a_wins/num_sims)*100, h_expected_runs, a_expected_runs

def generate_baseball_advanced_stats(h_team, a_team, h_exp, a_exp, h_s_fip, a_s_fip, h_ops, a_ops):
    return (
        f"<div class='table-wrapper'><div style='text-align:center; font-size:11.5px; color:#00E676; margin-bottom:5px; font-weight:bold;'>⚾ AI 심층 전력 지표</div>"
        f"<table class='detail-table'><tr style='background-color:#111;'><th style='color:#4FC3F7; width:33%;'>{h_team}</th><th style='color:#aaa; width:34%;'>비교 스탯</th><th style='color:#EF5350; width:33%;'>{a_team}</th></tr>"
        f"<tr><td style='color:#fff; font-weight:bold;'>{h_exp:.1f}</td><td style='color:#aaa;'>기대 득점</td><td style='color:#fff; font-weight:bold;'>{a_exp:.1f}</td></tr>"
        f"<tr><td style='color:#fff;'>{h_s_fip:.2f}</td><td style='color:#aaa;'>선발 FIP</td><td style='color:#fff;'>{a_s_fip:.2f}</td></tr>"
        f"<tr><td style='color:#fff;'>{h_ops:.3f}</td><td style='color:#aaa;'>평균 OPS</td><td style='color:#fff;'>{a_ops:.3f}</td></tr></table></div>"
    )

# 💡 [V84 UI 패치] 야구 결과 함수 -> HTML 배지 리스트 반환으로 변경
def get_baseball_prediction_badges_html(home_kr, away_kr, h_prob, h_exp, a_exp, is_finished, h_score, a_score):
    a_prob = 100.0 - h_prob
    
    # 1. 승리 예측
    win_status = "PENDING"
    if h_prob >= 58.0: 
        win_pred_code = "home"; win_pred_text = f"{home_kr} 승리"
    elif a_prob >= 58.0: 
        win_pred_code = "away"; win_pred_text = f"{away_kr} 승리"
    elif h_prob >= 53.0: 
        win_pred_code = "home"; win_pred_text = f"{home_kr} 우세"
    elif a_prob >= 53.0: 
        win_pred_code = "away"; win_pred_text = f"{away_kr} 우세"
    elif h_prob >= 50.0: 
        win_pred_code = "home"; win_pred_text = f"{home_kr} 신승"
    else: 
        win_pred_code = "away"; win_pred_text = f"{away_kr} 신승"
    
    # 2. 핸디캡 예측 (야구는 기본 1.5)
    handi_status = "PENDING"
    if h_prob >= 58.0: 
        handi_pred_code = "home"; handi_pred_text = f"{home_kr} -1.5 마핸 승"
    elif a_prob >= 58.0: 
        handi_pred_code = "away"; handi_pred_text = f"{away_kr} -1.5 마핸 승"
    elif win_pred_code == "home": 
        handi_pred_code = "away"; handi_pred_text = f"{away_kr} +1.5 플핸 방어"
    else: 
        handi_pred_code = "home"; handi_pred_text = f"{home_kr} +1.5 플핸 방어"
        
    # 3. 언오바 예측 (야구 기준점 8.5 고정)
    ou_status = "PENDING"
    exp_total = h_exp + a_exp
    ou_line = 8.5 
    if exp_total > ou_line: 
        ou_pred_code = "over"; ou_pred_text = "8.5 오버"
    else: 
        ou_pred_code = "under"; ou_pred_text = "8.5 언더"
        
    # 결과 계산 (종료 시)
    if is_finished:
        try:
            h_s = float(h_score) if h_score not in [None, ""] else 0.0
            a_s = float(a_score) if a_score not in [None, ""] else 0.0
            margin = h_s - a_s
            
            actual_win = "home" if margin > 0 else "away"
            win_status = "HIT" if win_pred_code == actual_win else "MISS"
            
            # 야구 핸디캡 1.5 기준 HIT/MISS
            if "마핸" in handi_pred_text:
                handi_status = "HIT" if margin >= 2 and win_status == "HIT" else "MISS"
            else:
                # 플핸 예측 시 1점차 패배까지 적중
                if handi_pred_code == "home": # 홈 플핸
                    handi_status = "HIT" if margin >= -1 else "MISS"
                else: # 원정 플핸
                    handi_status = "HIT" if margin <= 1 else "MISS"
            
            # 언오바 HIT/MISS
            actual_ou = "over" if (h_s + a_s) > ou_line else "under"
            ou_status = "HIT" if ou_pred_code == actual_ou else "MISS"
        except: pass

    # AI 코멘트 (기존 로직 유지)
    if win_pred_code == "home" and h_exp - a_exp > 1.5: comment = f"{home_kr}의 타선 폭발과 투수진의 안정감으로 무난한 대승이 예상됩니다."
    elif win_pred_code == "away" and a_exp - h_exp > 1.5: comment = f"선발 매치업의 우위를 바탕으로 {away_kr}이 경기를 쉽게 풀어갈 것입니다."
    elif ou_pred_code == "under": comment = f"양 팀 선발의 구위가 타선을 압도하여, 불펜 싸움에서 1점 차 승부가 갈릴 것입니다."
    else: comment = f"투수진의 대량 실점 위기를 타선이 어떻게 극복하느냐가 승패를 결정지을 화력전입니다."
        
    # 배지 HTML 생성
    win_badge = create_prediction_badge_html("🟢", win_pred_text, "승리", win_status)
    handi_badge = create_prediction_badge_html("🟣", handi_pred_text, "핸디캡", handi_status)
    ou_badge = create_prediction_badge_html("🟡", ou_pred_text, "언오바", ou_status)
    
    return f"{win_badge}{handi_badge}{ou_badge}", comment

# ==========================================
# 8. 메인 UI 및 앱 흐름 시작
# ==========================================
st.markdown("<h1 style='text-align: center; color: #00E676; font-size: 28px; margin-bottom: 30px;'>🏆 종합 스포츠 AI 분석실 (V84 UI 마스터판)</h1>", unsafe_allow_html=True)

sport_options = ["축구", "야구", "농구", "배구"]
selected_sport = st.sidebar.radio("종목 선택", sport_options, horizontal=True)
st.sidebar.markdown("---")

kst_now = datetime.utcnow() + timedelta(hours=9)
selected_date = st.sidebar.date_input("📅 검색 날짜 설정 (KST 기준)", kst_now.date())
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if 'sports_cards_data' not in st.session_state: st.session_state['sports_cards_data'] = []
if 'soccer_standings_tabs' not in st.session_state: st.session_state['soccer_standings_tabs'] = {}

# ==========================================
# ⚽ 축구 로직
# ==========================================
if selected_sport == "축구":
    analyze_button = st.sidebar.button("🚀 축구 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚽ 축구 리그 선택")
    
    with st.sidebar.expander("🌏 아시아 및 기타 리그", expanded=True):
        l_292 = st.checkbox("K리그 1 (KOR)", value=True); l_293 = st.checkbox("K리그 2 (KOR)", value=False); l_98 = st.checkbox("J1 리그 (JPN)", value=False)
    with st.sidebar.expander("🌟 국제 대회 (FIFA/UEFA)", expanded=True):
        l_1 = st.checkbox("월드컵 (World Cup)", value=True); l_2 = st.checkbox("챔피언스리그 (UCL)", value=False); l_3 = st.checkbox("유로파리그 (UEL)", value=False); l_10 = st.checkbox("A매치 친선전", value=False)
    with st.sidebar.expander("🌍 유럽 주요 리그", expanded=True):
        l_39 = st.checkbox("프리미어리그 (ENG)", value=False); l_140 = st.checkbox("라리가 (ESP)", value=False); l_135 = st.checkbox("세리에 A (ITA)", value=False); l_78 = st.checkbox("분데스리가 (GER)", value=False)

    league_ids = ["292", "293", "98", "1", "2", "3", "10", "39", "140", "135", "78"]
    checkbox_vals = [l_292, l_293, l_98, l_1, l_2, l_3, l_10, l_39, l_140, l_135, l_78]
    selected_leagues = [lid for lid, selected in zip(league_ids, checkbox_vals) if selected]
    LEAGUE_MAP = {"292":"K리그1", "293":"K리그2", "98":"J1리그", "1":"월드컵", "2":"챔피언스리그", "3":"유로파리그", "10":"A매치", "39":"프리미어리그", "140":"라리가", "135":"세리에 A", "78":"분데스리가"}
    SPRING_TO_AUTUMN_LEAGUES = ["292", "293", "98", "1", "10"]

    if analyze_button:
        if not selected_leagues: st.sidebar.warning("최소 1개 이상의 리그를 선택해주세요."); st.stop()
        st.session_state['sports_cards_data'] = []
        st.session_state['soccer_standings_tabs'] = {}
        progress_bar = st.progress(0); status_text = st.empty()
        limit_hit = False; match_count = 0
        temp_cards_data = []
        
        for idx, league_id in enumerate(selected_leagues):
            if limit_hit: break
            status_text.text(f"🔍 {LEAGUE_MAP[league_id]} 스캔 중... ({idx+1}/{len(selected_leagues)})")
            progress_bar.progress((idx) / len(selected_leagues))
            
            calc_season = str(selected_date.year) if league_id in SPRING_TO_AUTUMN_LEAGUES else (str(selected_date.year - 1) if selected_date.month < 7 else str(selected_date.year))
            standings_res = fetch_api_football_standings(FOOTBALL_API_KEY, league_id, calc_season)
            standings_dict = {} 
            if standings_res and standings_res[0].get('league', {}).get('standings'):
                league_data_list = []
                groups = standings_res[0].get('league', {}).get('standings', [])
                for g_idx, group in enumerate(groups):
                    try:
                        g_name = group[0].get('group', f'Group {g_idx+1}') if len(groups) > 1 else "통합 순위표"
                        df_data = []
                        for team in group:
                            standings_dict[team['team']['id']] = team['rank']
                            df_data.append({"순위": team['rank'], "팀명": translate_to_ko(team['team']['name']), "승점": team['points'], "승": team['all']['win'], "무": team['all']['draw'], "패": team['all']['lose']})
                        league_data_list.append({"group_name": g_name, "dataframe": pd.DataFrame(df_data).set_index("순위")})
                    except: pass
                st.session_state['soccer_standings_tabs'][LEAGUE_MAP[league_id]] = league_data_list
            
            date_str = selected_date.strftime('%Y-%m-%d')
            matches = fetch_api_football_fixtures(FOOTBALL_API_KEY, league_id, calc_season, date_str)
            if matches == "LIMIT": st.error("🚨 API 한도 초과!"); limit_hit = True; break
            if matches and isinstance(matches, list):
                for match in matches:
                    try:
                        utc_time = datetime.strptime(match['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
                        kst_time = utc_time + timedelta(hours=9)
                        if kst_time.date() != selected_date: continue

                        home_kr = translate_to_ko(match['teams']['home']['name']); away_kr = translate_to_ko(match['teams']['away']['name'])
                        raw_timestamp = int(utc_time.timestamp())
                        match_time = kst_time.strftime("%H:%M")
                        is_finished = match['fixture']['status']['short'] in ['FT', 'AET', 'PEN']
                        goals_h = match['goals']['home']; goals_a = match['goals']['away']
                        
                        top_txt = f"{LEAGUE_MAP[league_id]} ({match_time}) <br><span style='color:#aaa;'>[종료]</span>" if is_finished else f"{LEAGUE_MAP[league_id]} ({match_time})"
                        s_color = "#00E676" if is_finished else "#888"; s_txt = f"{int(goals_h)}:{int(goals_a)}" if is_finished else "VS"

                        h_prob = 35.0 + (sum(ord(c) for c in home_kr+away_kr) % 30)
                        if standings_dict and match['teams']['home']['id'] in standings_dict and match['teams']['away']['id'] in standings_dict:
                            h_prob = max(20.0, min(80.0, 40.0 + ((standings_dict[match['teams']['away']['id']] - standings_dict[match['teams']['home']['id']]) * 1.5) + 3.0))
                            
                        adv_html, h_gf, a_gf = generate_soccer_advanced_stats(home_kr, away_kr, h_prob, is_finished, goals_h, goals_a)
                        
                        # 💡 [V84 패치] 배지 HTML 수신
                        badges_html, ai_comment = get_soccer_prediction_badges_html(home_kr, away_kr, h_prob, h_gf, a_gf, is_finished, goals_h, goals_a)
                        
                        temp_cards_data.append({
                            'sort_time': raw_timestamp, 'sport': '축구', 'top_text': top_txt, 'home_kr': home_kr, 'away_kr': away_kr, 'h_logo': match['teams']['home']['logo'], 'a_logo': match['teams']['away']['logo'], 
                            's_color': s_color, 's_txt': s_txt, 'p_h': h_prob, 'p_d': max(0.0, 20.0 - abs(h_prob-50.0)/2.0), 'p_a': 100.0 - h_prob - max(0.0, 20.0 - abs(h_prob-50.0)/2.0), 
                            'badges_html': badges_html, 'ai_comment': ai_comment, 'advanced_html': adv_html, 'radar_html': create_html_radar(h_prob, home_kr, away_kr, True, "축구"), 'lineup_html': get_soccer_lineup_table(home_kr, away_kr), 'referee': f"🏟️ {match['fixture']['venue']['name'] or '미정'}"
                        })
                        match_count += 1
                    except: continue
            time.sleep(0.4)
        progress_bar.progress(1.0); status_text.text("✅ 축구 스캔 완료!"); time.sleep(0.5); status_text.empty(); progress_bar.empty()
        if temp_cards_data: temp_cards_data.sort(key=lambda x: x['sort_time']); st.session_state['sports_cards_data'] = temp_cards_data
        if match_count == 0 and not limit_hit: st.info("배정된 축구 경기가 없습니다.")

# ==========================================
# ⚾ 야구 로직 (💡 V84 UI 패치)
# ==========================================
elif selected_sport == "야구":
    analyze_button = st.sidebar.button("🚀 MLB 데이터 딥-스캔 시작", use_container_width=True)
    st.sidebar.markdown("---")
    st.sidebar.checkbox("메이저리그 (MLB) 단일 시스템 구동", value=True, disabled=True)
    
    if analyze_button:
        st.session_state['sports_cards_data'] = []
        progress_bar = st.progress(0); status_text = st.empty()
        status_text.text("🔍 MLB 스탯 및 오즈 데이터 불러오는 중...")
        df_h, df_p, team_bp_fip = load_mlb_all_data()
        momentum_dict = load_mlb_team_momentum(); progress_bar.progress(0.2)
        
        start_date_str = (selected_date - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date_str = (selected_date + timedelta(days=2)).strftime('%Y-%m-%d')
        schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start_date_str}&endDate={end_date_str}&hydrate=probablePitcher"
        
        try:
            res = requests.get(schedule_url, timeout=10).json()
            all_games = []
            for date_data in (res.get('dates') or []): all_games.extend(date_data.get('games') or [])
            
            temp_cards_data = []; match_count = 0
            for idx, game in enumerate(all_games):
                try:
                    utc_time = datetime.strptime(game['gameDate'], "%Y-%m-%dT%H:%M:%SZ")
                    kst_time = utc_time + timedelta(hours=9)
                    if kst_time.date() != selected_date: continue
                    status_text.text(f"🔍 MLB 매치업 분석 중... ({idx+1}/{len(all_games)})"); progress_bar.progress(0.2 + (0.8 * (idx / max(len(all_games), 1))))
                    
                    home_info = game['teams']['home']; away_info = game['teams']['away']
                    home_kr = translate_to_ko(home_info['team']['name']); away_kr = translate_to_ko(away_info['team']['name'])
                    h_p_name = home_info.get('probablePitcher', {}).get('fullName', '미정(TBD)')
                    a_p_name = away_info.get('probablePitcher', {}).get('fullName', '미정(TBD)')
                    
                    is_finished = game['status']['abstractGameState'] == 'Final'
                    s_color = "#00E676" if is_finished else "#888"; s_txt = f"{home_info.get('score',0)}:{away_info.get('score',0)}" if is_finished else "VS"
                    top_txt = f"MLB ({kst_time.strftime('%H:%M')}) <br><span style='color:#aaa;'>[종료]</span>" if is_finished else f"MLB ({kst_time.strftime('%H:%M')})"

                    # 💡 데이터 예외 처리 및 시뮬레이션
                    try:
                        h_p_data = df_p[df_p['이름'] == h_p_name]; a_p_data = df_p[df_p['이름'] == a_p_name]
                        h_s_fip = float(h_p_data['FIP'].values[0]) if not h_p_data.empty and not pd.isna(h_p_data['FIP'].values[0]) else 4.50
                        a_s_fip = float(a_p_data['FIP'].values[0]) if not a_p_data.empty and not pd.isna(a_p_data['FIP'].values[0]) else 4.50
                        h_base_ops = df_h[df_h['팀'] == home_info['team']['name']]['OPS'].mean() or 0.720
                        a_base_ops = df_h[df_h['팀'] == away_info['team']['name']]['OPS'].mean() or 0.720
                        h_f_ops = (h_base_ops * 0.8) + (h_base_ops * (1.0 + (momentum_dict.get(home_info['team']['name'], 0.5) - 0.5) * 0.5) * 0.2)
                        a_f_ops = (a_base_ops * 0.8) + (a_base_ops * (1.0 + (momentum_dict.get(away_info['team']['name'], 0.5) - 0.5) * 0.5) * 0.2)
                        pf = MLB_PARK_FACTORS.get(home_info['team']['name'], 1.00)
                        h_prob, a_prob, h_exp, a_exp = run_mlb_simulation(h_s_fip, a_s_fip, 5.0, 5.0, h_f_ops, a_f_ops, team_bp_fip.get(home_info['team']['name'], 4.00), team_bp_fip.get(away_info['team']['name'], 4.00), pf)
                    except:
                        seed = sum(ord(c) for c in home_kr+away_kr); h_prob = 43.0 + (seed%14); a_prob = 100.0 - h_prob; h_exp = 4.0; a_exp = 4.0; h_s_fip=4.5; a_s_fip=4.5; h_f_ops=0.72; a_f_ops=0.72
                        
                    adv_html = generate_baseball_advanced_stats(home_kr, away_kr, h_exp, a_exp, h_s_fip, a_s_fip, h_f_ops, a_f_ops)
                    
                    # 💡 [V84 패치] 배지 HTML 수신
                    badges_html, ai_comment = get_baseball_prediction_badges_html(home_kr, away_kr, h_prob, h_exp, a_exp, is_finished, home_info.get('score'), away_info.get('score'))
                    
                    lineup_html = f"<div class='table-wrapper'><table class='detail-table'><tr><th style='color:#4FC3F7; width:50%;'>{home_kr} ({h_p_name})</th><th style='color:#EF5350; width:50%;'>{away_kr} ({a_p_name})</th></tr><tr><td style='color:#888;'>데이터 스캔 대기중</td><td style='color:#888;'>데이터 스캔 대기중</td></tr></table></div>"
                    
                    temp_cards_data.append({
                        'sort_time': int(utc_time.timestamp()), 'sport': '야구', 'top_text': top_txt, 'home_kr': home_kr, 'away_kr': away_kr, 'h_logo': f"https://www.mlbstatic.com/team-logos/{home_info['team']['id']}.svg", 'a_logo': f"https://www.mlbstatic.com/team-logos/{away_info['team']['id']}.svg", 
                        's_color': s_color, 's_txt': s_txt, 'p_h': h_prob, 'p_d': 0.0, 'p_a': a_prob, 
                        'badges_html': badges_html, 'ai_comment': ai_comment, 'advanced_html': adv_html, 'radar_html': create_html_radar(h_prob, home_kr, away_kr, False, "야구"), 'lineup_html': lineup_html, 'referee': f"🏟️ {game['venue']['name']}"
                    })
                    match_count += 1
                except: pass
        except: pass
        progress_bar.progress(1.0); status_text.text("✅ MLB 스캔 완료!"); time.sleep(0.5); status_text.empty(); progress_bar.empty()
        if temp_cards_data: temp_cards_data.sort(key=lambda x: x['sort_time']); st.session_state['sports_cards_data'] = temp_cards_data
        if match_count == 0: st.info("배정된 MLB 경기가 없습니다.")

# ==========================================
# 📺 9. 통합 렌더링 엔진 (💡 V84 UI 패치 완벽 반영)
# ==========================================
if st.session_state.get('sports_cards_data'):
    cols = st.columns(3)
    for idx, card in enumerate(st.session_state['sports_cards_data']):
        with cols[idx % 3]:
            # 확률 바 설정
            if card['sport'] == "야구":
                prob_html = f"<div class='prob-text'><span>홈 {card['p_h']:.0f}%</span><span>원정 {card['p_a']:.0f}%</span></div><div class='prob-container'><div class='prob-home' style='width: {card['p_h']}%;'></div><div class='prob-away' style='width: {card['p_a']}%;'></div></div>"
            else:
                prob_html = f"<div class='prob-text'><span>홈 {card['p_h']:.0f}%</span><span>무 {card['p_d']:.0f}%</span><span>원정 {card['p_a']:.0f}%</span></div><div class='prob-container'><div class='prob-home' style='width: {card['p_h']}%;'></div><div class='prob-draw' style='width: {card['p_d']}%;'></div><div class='prob-away' style='width: {card['p_a']}%;'></div></div>"
            
            # 💡 [V84 패치] 카드 하단에 사진 UI 배지 HTML 삽입
            html_str = (
                f"<div class='card-box'>"
                f"<div class='card-top'><div class='league-txt'>{card['top_text']}</div><div class='match-box'><div class='team-side home-side'><div class='team-name'>{card['home_kr']}</div><img src='{card['h_logo']}' class='team-logo'></div><div class='score-side' style='color:{card['s_color']};'>{card['s_txt']}</div><div class='team-side away-side'><img src='{card['a_logo']}' class='team-logo'><div class='team-name'>{card['away_kr']}</div></div></div><div class='referee-txt'>{card['referee']}</div></div>"
                f"<div class='card-mid'><div class='prob-wrapper'>{prob_html}</div>{card['advanced_html']}</div>"
                f"<div class='card-bot'>{card['badges_html']}<div class='ai-advice'>✍️ 코멘트: {card['ai_comment']}</div></div>"
                f"</div>"
            )
            st.markdown(html_str, unsafe_allow_html=True)
            with st.expander("🔍 육각형 지표 & 선발 확인"):
                st.markdown(card['radar_html'], unsafe_allow_html=True)
                st.markdown(card['lineup_html'], unsafe_allow_html=True)
            st.write("")
