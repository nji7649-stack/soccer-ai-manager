import os
import requests
from datetime import datetime, timedelta

def find_international_matches():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    if not api_key:
        print("❌ 에러: FOOTBALL_API_KEY가 없습니다.")
        return

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
    }

    # 한국 시간 기준 오늘 날짜 (KST)
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    
    print(f"=========================================")
    print(f"🌍 [축구 AI 분석실] 국가대표 매치업 정밀 탐색 모드")
    print(f"👉 검색 기준일: {date_string} (KST)")
    print(f"=========================================\n")

    # 월드컵(1)과 친선전(10) 모두 탐색
    target_leagues = ["1", "10"]
    # API 서버의 연도 표기 오류에 대비하여 3년 치를 모두 찔러봅니다.
    seasons_to_test = ["2024", "2025", "2026"] 
    
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    total_found = 0

    for league_id in target_leagues:
        league_type = "월드컵" if league_id == "1" else "A매치(친선전)"
        print(f"[{league_type}] 데이터베이스 스캔 중...")
        
        for season in seasons_to_test:
            querystring = {
                "league": league_id, 
                "season": season, 
                "date": date_string,
                "timezone": "Asia/Seoul" # 시차 문제 원천 차단
            }

            try:
                response = requests.get(url, headers=headers, params=querystring, timeout=10)
                data = response.json()
                
                if 'response' in data and data['response']:
                    fixtures = data['response']
                    print(f"  ✔️ 성공! (시즌 설정: {season}년 데이터에서 발견)")
                    
                    for match in fixtures:
                        total_found += 1
                        home = match['teams']['home']['name']
                        away = match['teams']['away']['name']
                        status = match['fixture']['status']['short']
                        print(f"     👉 {home} vs {away} [{status}]")
                        
            except Exception as e:
                pass # 에러가 나도 멈추지 않고 계속 탐색

    if total_found == 0:
        print("\n😭 API 서버에 오늘(KST 기준) 등록된 국가대표 일정이 존재하지 않습니다.")
        print("💡 API-Football이 해당 A매치를 다른 리그 ID(예: 지역 컵대회 예선 등)로 분류했을 가능성이 높습니다.")

if __name__ == "__main__":
    find_international_matches()
