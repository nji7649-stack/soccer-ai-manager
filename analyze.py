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

    # 한국 시간 오늘 날짜와 연도
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    current_year = kst_now.strftime('%Y') # 2026년 자동 추출
    
    print(f"=========================================")
    print(f"🌍 [축구 AI 분석실 v2.0] 가동 - 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    # 월드컵(1)과 친선전(10) 조회
    target_leagues = ["1", "10"]
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    total_matches = 0

    for league_id in target_leagues:
        # 💡 핵심 패치: timezone을 아시아/서울로 명시하고, 시즌을 current_year(2026)로 변경
        querystring = {
            "league": league_id, 
            "season": current_year, 
            "date": date_string,
            "timezone": "Asia/Seoul"
        }

        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            data = response.json()
            
            if 'response' not in data or not data['response']:
                continue 

            fixtures = data['response']

            for match in fixtures:
                total_matches += 1
                fixture_id = match['fixture']['id']
                league_name = match['league']['name']
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                status = match['fixture']['status']['short'] # 경기 상태 (NS: 예정, 1H: 전반전 등)
                
                print(f"🔍 [{league_name}] 매치업 발견: {home_team} vs {away_team} [{status}]")
                
        except Exception as e:
            print(f"⚠️ {league_id}번 리그 조회 중 문제 발생: {e}")
            
    if total_matches == 0:
        print("📅 오늘은 진행되는 주요 국제대회(A매치/월드컵) 일정이 없습니다.")

if __name__ == "__main__":
    run_worldcup_mode()
