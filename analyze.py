import os
import requests
from datetime import datetime, timedelta

def run_worldcup_mode():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    if not api_key:
        print("❌ 에러: FOOTBALL_API_KEY가 없습니다.")
        return

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
    }

    # 한국 시간 오늘 날짜
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    
    print(f"=========================================")
    print(f"🌍 [축구 AI 분석실 v2.0] 가동 - 날짜: {date_string}")
    print(f"=========================================\n")

    # 월드컵(1)과 친선전(10) 조회
    target_leagues = ["1", "10"]
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    total_matches = 0

    for league_id in target_leagues:
        # 💡 해결책: 시즌을 2025년으로 변경하여 현재 진행 중인 A매치 찌르기
        querystring = {"league": league_id, "season": "2025", "date": date_string}

        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            data = response.json()
            
            # API 응답에 'response' 키가 아예 없거나 에러가 났을 때를 대비한 안전장치
            if 'response' not in data or not data['response']:
                continue # 에러 뿜지 말고 다음 리그로 넘어가라!

            fixtures = data['response']

            for match in fixtures:
                total_matches += 1
                fixture_id = match['fixture']['id']
                league_name = match['league']['name']
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                
                print(f"🔍 [{league_name}] 매치업 발견: {home_team} vs {away_team}")
                
        except Exception as e:
            print(f"⚠️ {league_id}번 리그 조회 중 문제 발생 (통과합니다) : {e}")
            
    if total_matches == 0:
        print("📅 오늘은 진행되는 주요 국제대회(A매치/월드컵) 일정이 없습니다.")
        print("💡 팁: 리그 ID를 클럽 대항전(EPL 등)으로 변경하여 테스트해 보세요.")

if __name__ == "__main__":
    run_worldcup_mode()
