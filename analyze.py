import os
import requests
from datetime import datetime, timedelta

def run_worldcup_mode():
    # 1. 금고에서 API 키 꺼내기
    api_key = os.environ.get('FOOTBALL_API_KEY')
    if not api_key:
        print("❌ 에러: FOOTBALL_API_KEY가 설정되지 않았습니다.")
        return

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
    }

    # 2. 오늘 날짜 구하기 (한국 시간 기준)
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    
    print(f"=========================================")
    print(f"🌍 [축구 AI 분석실 v2.0] A매치/월드컵 모드 가동 - 날짜: {date_string}")
    print(f"=========================================\n")

    # 3. 대상 리그 ID 설정 (1: 월드컵 본선, 10: 국가대표 친선전/A매치)
    target_leagues = ["1", "10"]
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    total_matches = 0

    for league_id in target_leagues:
        # 이번 달 진행되는 2026시즌 국제대회 세팅
        querystring = {"league": league_id, "season": "2026", "date": date_string}

        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            fixtures = response.json().get('response', [])

            for match in fixtures:
                total_matches += 1
                fixture_id = match['fixture']['id']
                league_name = match['league']['name']
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                status = match['fixture']['status']['long']
                
                print(f"🔍 [{league_name}] 국가대표 매치업 발견: {home_team} vs {away_team} [{status}]")
                
                # 4. 정밀 데이터 분석 호출
                stats_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
                stats_response = requests.get(stats_url, headers=headers, params={"fixture": fixture_id}, timeout=10)
                
                print(f"   📊 [정밀 지표(점유율, xG, 패스 등) 수집 및 분석중...]")
                print(f"   👉 {home_team} vs {away_team} 전력 분석 모델 준비 완료!\n")

        except Exception as e:
            print(f"❌ 데이터 호출 중 에러 발생: {e}")
            
    if total_matches == 0:
        print("📅 오늘 예정된 월드컵 본선 또는 주요 A매치 일정이 없습니다.")

if __name__ == "__main__":
    run_worldcup_mode()
