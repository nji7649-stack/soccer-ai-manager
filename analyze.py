import os
import requests
from datetime import datetime, timedelta

# 💡 [한글 패치 사전 1] 팀 이름
TEAM_KO_MAP = {
    # K리그 1
    "Gimcheon Sangmu FC": "김천 상무",
    "Pohang Steelers": "포항 스틸러스",
    "Jeju United FC": "제주 유나이티드",
    "Ulsan Hyundai FC": "울산 HD",
    "Daejeon Citizen": "대전 하나시티즌",
    "Daegu FC": "대구 FC",
    "Jeonbuk Hyundai Motors": "전북 현대",
    "FC Seoul": "FC 서울",
    "Gwangju FC": "광주 FC",
    "Incheon United FC": "인천 유나이티드",
    "Gangwon FC": "강원 FC",
    "Suwon City": "수원 FC",
    # 해외 인기 클럽
    "Manchester City": "맨시티", "Arsenal": "아스널", "Liverpool": "리버풀", 
    "Tottenham": "토트넘", "Manchester United": "맨유", "Chelsea": "첼시",
    "Real Madrid": "레알 마드리드", "Barcelona": "바르셀로나", "Bayern Munich": "뮌헨",
    "Paris Saint Germain": "PSG", "Inter": "인터밀란", "AC Milan": "AC밀란",
    # 국가대표
    "South Korea": "대한민국", "Japan": "일본", "China": "중국", "France": "프랑스",
    "England": "잉글랜드", "Spain": "스페인", "Germany": "독일", "Brazil": "브라질"
}

# 💡 [한글 패치 사전 2] 리그 이름
LEAGUE_KO_MAP = {
    "K League 1": "K리그 1",
    "Premier League": "프리미어리그",
    "La Liga": "라리가",
    "Bundesliga": "분데스리가",
    "Serie A": "세리에 A",
    "Ligue 1": "리그 1",
    "World Cup": "월드컵",
    "Friendlies": "A매치 친선전"
}

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

def run_pro_analysis():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    headers = {'x-apisports-key': api_key}

    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    season = kst_now.strftime('%Y')

    print(f"=========================================")
    print(f"🏆 [축구 AI 분석실 v5.1] 한글 패치 모드 가동")
    print(f"👉 분석 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    # K리그(292) 포함 주요 리그 세팅
    target_leagues = ["1", "10", "39", "66", "140", "135", "78", "61", "292"]
    url = "https://v3.football.api-sports.io/fixtures"
    
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
            .match {{ font-size: 1.2em; font-weight: bold; margin-bottom: 15px; text-align: center; letter-spacing: -0.5px; }}
            .stat-box {{ background: #2a2a2a; padding: 12px; border-radius: 8px; font-size: 0.9em; margin-bottom: 15px; color: #ccc; line-height: 1.5; }}
            .stat-team {{ color: #fff; font-weight: bold; }}
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
                
                # 💡 사전에서 한글 이름을 꺼내오고, 사전에 없으면 원래 영어 이름 유지
                league_en = match['league']['name']
                home_en = match['teams']['home']['name']
                away_en = match['teams']['away']['name']
                
                league_name = LEAGUE_KO_MAP.get(league_en, league_en)
                home_team = TEAM_KO_MAP.get(home_en, home_en)
                away_team = TEAM_KO_MAP.get(away_en, away_en)
                
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
                if total_shots >= 9: over_under = "🔥 오버 (다득점 페이스)"
                elif total_shots <= 5: over_under = "❄️ 언더 (저득점 늪축구)"
                else: over_under = "⚖️ 언오버 팽팽"

                html_content += f"""
                <div class="card">
                    <div class="league">{league_name}</div>
                    <div class="match">{home_team} vs {away_team}</div>
                    <div class="stat-box">
                        <span class="stat-team">{home_team}</span> : 점유율 {h_poss}% / 유효슈팅 {h_shot}개<br>
                        <span class="stat-team">{away_team}</span> : 점유율 {a_poss}% / 유효슈팅 {a_shot}개
                    </div>
                    <div class="result">
                        🎯 승무패: {win_pick}<br>
                        ⚔️ 주도권: {control_pick}<br>
                        📊 언오버: {over_under}
                    </div>
                </div>
                """
                print(f"✅ {home_team} vs {away_team} 한글 패치 분석 완료")

        except Exception as e:
            pass

    if total_matches_found == 0:
        html_content += "<div class='no-match'>오늘은 분석할 스탯 데이터가 없습니다.</div>"

    html_content += """
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    run_pro_analysis()
