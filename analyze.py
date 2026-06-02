import os
import requests
import json
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

# 자동 번역기 세팅
def translate_to_ko(text):
    try:
        return GoogleTranslator(source='en', target='ko').translate(text)
    except:
        return text

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

def run_ultimate_dashboard():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    headers = {'x-apisports-key': api_key}

    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    season = kst_now.strftime('%Y')

    print(f"=========================================")
    print(f"🌍 [축구 AI 분석실 v6.0] 글로벌 라이브 팝업 웹사이트 구축")
    print(f"=========================================\n")

    # 주요 리그 한정 (API 폭탄 방지용) - 필요한 리그 번호만 콤마로 추가하세요!
    target_leagues = ["1", "10", "39", "66", "140", "135", "78", "61", "292"]
    url = "https://v3.football.api-sports.io/fixtures"
    
    match_data_for_popup = {}
    cards_html = ""

    for league_id in target_leagues:
        querystring = {"league": league_id, "season": season, "date": date_string, "timezone": "Asia/Seoul"}
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            fixtures = response.json().get('response', [])
            if not fixtures: continue

            for match in fixtures:
                fixture_id = str(match['fixture']['id'])
                
                # 번역기 가동! (실시간 번역)
                league_name = translate_to_ko(match['league']['name'])
                home_team = translate_to_ko(match['teams']['home']['name'])
                away_team = translate_to_ko(match['teams']['away']['name'])
                
                # 1. 스탯 불러오기
                stats_url = "https://v3.football.api-sports.io/fixtures/statistics"
                stats_res = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
                stats_data = stats_res.json().get('response', [])

                # 2. 라인업(선발 명단) 불러오기
                lineup_url = "https://v3.football.api-sports.io/fixtures/lineups"
                lineup_res = requests.get(lineup_url, headers=headers, params={"fixture": fixture_id})
                lineup_data = lineup_res.json().get('response', [])

                if not stats_data or len(stats_data) < 2: continue
                
                h_poss = safe_num(next((item['value'] for item in stats_data[0]['statistics'] if item['type'] == 'Ball Possession'), 0))
                h_shot = safe_num(next((item['value'] for item in stats_data[0]['statistics'] if item['type'] == 'Shots on Goal'), 0))
                a_poss = safe_num(next((item['value'] for item in stats_data[1]['statistics'] if item['type'] == 'Ball Possession'), 0))
                a_shot = safe_num(next((item['value'] for item in stats_data[1]['statistics'] if item['type'] == 'Shots on Goal'), 0))

                # 알고리즘 계산
                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                
                win_pick = f"🟢 {home_team} 승" if h_score > a_score + 2.5 else (f"🔵 {away_team} 승" if a_score > h_score + 2.5 else "🟡 무승부")
                
                # 팝업창(모달)에 전달할 세부 데이터 저장
                h_lineup = [p['player']['name'] for p in lineup_data[0]['startXI']] if lineup_data else ["명단 미발표"]
                a_lineup = [p['player']['name'] for p in lineup_data[1]['startXI']] if lineup_data and len(lineup_data) > 1 else ["명단 미발표"]

                match_data_for_popup[fixture_id] = {
                    "home": home_team, "away": away_team,
                    "h_poss": h_poss, "a_poss": a_poss,
                    "h_shot": h_shot, "a_shot": a_shot,
                    "h_lineup": h_lineup, "a_lineup": a_lineup
                }

                # 메인 화면 카드 UI (클릭 시 팝업 띄우는 onclick 속성 추가)
                cards_html += f"""
                <div class="card" onclick="openModal('{fixture_id}')">
                    <div class="league">{league_name}</div>
                    <div class="match">{home_team} <br><span style="font-size:0.7em;color:#888;">vs</span><br> {away_team}</div>
                    <div class="result">{win_pick} (예측)</div>
                    <div style="text-align:center; margin-top:10px; font-size:0.8em; color:#00bcd4;">👆 클릭하여 세부 스탯/라인업 보기</div>
                </div>
                """
                print(f"✅ {home_team} vs {away_team} 웹사이트 연동 완료")

        except Exception as e:
            pass

    # 🎨 자바스크립트 및 HTML 완성본
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>라이브 AI 축구 분석</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: #121212; color: #fff; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #00E676; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
            .card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 12px; width: 300px; padding: 20px; cursor: pointer; transition: 0.3s; }}
            .card:hover {{ border-color: #00E676; transform: scale(1.02); }}
            .league {{ font-size: 0.8em; color: #ff9800; font-weight: bold; margin-bottom: 10px; }}
            .match {{ font-size: 1.2em; font-weight: bold; text-align: center; margin-bottom: 10px; }}
            .result {{ font-size: 1em; font-weight: bold; color: #00E676; text-align: center; }}
            
            /* 팝업(모달) CSS */
            .modal {{ display: none; position: fixed; z-index: 999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); }}
            .modal-content {{ background-color: #222; margin: 10% auto; padding: 20px; border: 1px solid #00E676; border-radius: 10px; width: 90%; max-width: 500px; color: #fff; }}
            .close {{ color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }}
            .close:hover {{ color: #fff; }}
            .team-box {{ background: #333; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>⚽ 글로벌 라이브 승부 예측</h1>
        <div class="container">{cards_html}</div>

        <div id="matchModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <h2 id="modal-title" style="text-align:center; color:#00bcd4;"></h2>
                <div class="team-box">
                    <h3 id="modal-h-team" style="color:#00E676;"></h3>
                    <p>📊 점유율: <span id="modal-h-poss"></span>% | 유효슈팅: <span id="modal-h-shot"></span>개</p>
                    <p style="font-size:0.8em; color:#ccc;">🏃 선발 라인업: <span id="modal-h-lineup"></span></p>
                </div>
                <div class="team-box">
                    <h3 id="modal-a-team" style="color:#ff5252;"></h3>
                    <p>📊 점유율: <span id="modal-a-poss"></span>% | 유효슈팅: <span id="modal-a-shot"></span>개</p>
                    <p style="font-size:0.8em; color:#ccc;">🏃 선발 라인업: <span id="modal-a-lineup"></span></p>
                </div>
            </div>
        </div>

        <script>
            // 파이썬이 서버에서 가져온 팝업 데이터 JSON 주입!
            const popupData = {json.dumps(match_data_for_popup)};

            function openModal(id) {{
                const data = popupData[id];
                if(data) {{
                    document.getElementById('modal-title').innerText = data.home + " vs " + data.away;
                    document.getElementById('modal-h-team').innerText = "🏠 " + data.home;
                    document.getElementById('modal-h-poss').innerText = data.h_poss;
                    document.getElementById('modal-h-shot').innerText = data.h_shot;
                    document.getElementById('modal-h-lineup').innerText = data.h_lineup.join(', ');

                    document.getElementById('modal-a-team').innerText = "✈️ " + data.away;
                    document.getElementById('modal-a-poss').innerText = data.a_poss;
                    document.getElementById('modal-a-shot').innerText = data.a_shot;
                    document.getElementById('modal-a-lineup').innerText = data.a_lineup.join(', ');

                    document.getElementById('matchModal').style.display = "block";
                }}
            }}
            function closeModal() {{ document.getElementById('matchModal').style.display = "none"; }}
            window.onclick = function(event) {{
                if (event.target == document.getElementById('matchModal')) {{ closeModal(); }}
            }}
        </script>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    run_ultimate_dashboard()
