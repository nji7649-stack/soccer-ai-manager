import os
import requests
from datetime import datetime, timedelta

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

def run_pro_analysis():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    headers = {'x-apisports-key': api_key}

    # 한국 시간 기준 오늘 날짜
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    season = kst_now.strftime('%Y')

    print(f"=========================================")
    print(f"🏆 [축구 AI 분석실 v5.0] 시각화 대시보드 모드")
    print(f"👉 분석 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    # 월드컵, 친선, EPL(39), 라리가(140), 세리에A(135), 분데스(78), 리그1(61) 등
    target_leagues = ["1", "10", "39", "66", "140", "135", "78", "61"]
    url = "https://v3.football.api-sports.io/fixtures"
    
    # 🎨 HTML 웹페이지 뼈대 준비 (다크 모드 스포츠 UI)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI 축구 승부 예측 리포트</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #00E676; }}
            .date {{ text-align: center; color: #aaaaaa; margin-bottom: 30px; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
            .card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 12px; width: 350px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
            .league {{ font-size: 0.8em; color: #ff9800; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }}
            .match {{ font-size: 1.2em; font-weight: bold; margin-bottom: 15px; text-align: center; }}
            .stat-box {{ background: #2a2a2a; padding: 10px; border-radius: 8px; font-size: 0.9em; margin-bottom: 15px; color: #ccc; }}
            .result {{ font-size: 1em; font-weight: bold; color: #00E676; border-top: 1px dashed #444; padding-top: 15px; text-align: center; line-height: 1.6; }}
            .no-match {{ text-align: center; color: #ff5252; font-size: 1.2em; width: 100%; }}
        </style>
    </head>
    <body>
        <h1>🏆 AI 축구 승부 예측 리포트</h1>
        <div class="date">업데이트: {date_string} (KST)</div>
        <div class="container">
    """

    total_matches_found = 0

    for league_id in target_leagues:
        querystring = {"league": league_id, "season": season, "date": date_string, "timezone": "Asia/Seoul"}
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            fixtures = response.json().get('response', [])
            if not fixtures: continue

            for match in fixtures:
                fixture_id = match['fixture']['id']
                league_name = match['league']['name']
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                
                stats_url = "https://v3.football.api-sports.io/fixtures/statistics"
                stats_res = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
                stats_data = stats_res.json().get('response', [])

                if not stats_data or len(stats_data) < 2: continue

                total_matches_found += 1
                
                home_stats = stats_data[0]['statistics']
                away_stats = stats_data[1]['statistics']

                h_poss = safe_num(next((item['value'] for item in home_stats if item['type'] == 'Ball Possession'), 0))
                h_shot = safe_num(next((item['value'] for item in home_stats if item['type'] == 'Shots on Goal'), 0))
                a_poss = safe_num(next((item['value'] for item in away_stats if item['type'] == 'Ball Possession'), 0))
                a_shot = safe_num(next((item['value'] for item in away_stats if item['type'] == 'Shots on Goal'), 0))

                # 알고리즘 계산
                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                
                if h_score > a_score + 2.5: win_pick = f"🟢 {home_team} 승리 예상"
                elif a_score > h_score + 2.5: win_pick = f"🔵 {away_team} 승리 예상"
                else: win_pick = "🟡 무승부 접전"

                if h_poss > a_poss + 15: control_pick = f"{home_team} 주도"
                elif a_poss > h_poss + 15: control_pick = f"{away_team} 주도"
                else: control_pick = "팽팽한 중원 싸움"

                total_shots = h_shot + a_shot
                if total_shots >= 9: over_under = "🔥 오버 (다득점)"
                elif total_shots <= 5: over_under = "❄️ 언더 (저득점)"
                else: over_under = "⚖️ 예측 불가"

                # 🎨 분석 카드를 HTML에 추가
                html_content += f"""
                <div class="card">
                    <div class="league">{league_name}</div>
                    <div class="match">{home_team} vs {away_team}</div>
                    <div class="stat-box">
                        <strong>{home_team}</strong>: 점유율 {h_poss}% / 유효슈팅 {h_shot}개<br>
                        <strong>{away_team}</strong>: 점유율 {a_poss}% / 유효슈팅 {a_shot}개
                    </div>
                    <div class="result">
                        승무패: {win_pick}<br>
                        경기흐름: {control_pick}<br>
                        언오버: {over_under}
                    </div>
                </div>
                """
                print(f"✅ {home_team} vs {away_team} 분석 완료")

        except Exception as e:
            print(f"에러 발생: {e}")

    if total_matches_found == 0:
        html_content += "<div class='no-match'>오늘은 분석할 스탯 데이터가 없습니다.</div>"

    html_content += """
        </div>
    </body>
    </html>
    """

    # 🎨 최종적으로 index.html 이라는 파일명으로 예쁜 리포트 저장
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("\n🎨 시각화 리포트(index.html) 생성 완료!")

if __name__ == "__main__":
    run_pro_analysis()
