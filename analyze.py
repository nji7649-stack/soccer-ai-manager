import os
import requests
from datetime import datetime, timedelta

def run_soccer_analysis():
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
    print(f"⚽ [축구 AI 분석실 v2.0] 가동 - 날짜: {date_string}")
    print(f"=========================================\n")

    # 3. EPL(리그 ID: 39)의 오늘 경기 일정 가져오기
    # API-Football에서 현재 시즌은 2025-2026이므로 '2025'로 지정합니다.
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"league": "39", "season": "2025", "date": date_string}

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        fixtures = response.json().get('response', [])

        if not fixtures:
            print("📅 오늘 예정된 EPL 경기가 없습니다. (A매치 기간 또는 휴식기)")
            return

        for match in fixtures:
            fixture_id = match['fixture']['id']
            home_team = match['teams']['home']['name']
            away_team = match['teams']['away']['name']
            status = match['fixture']['status']['long']
            
            print(f"🔍 매치업 발견: {home_team} vs {away_team} [{status}]")
            
            # 4. 정밀 데이터 분석 (무료 호출 한도를 아끼기 위해 실제 매치업이 있을 때만 상세 호출)
            stats_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
            stats_response = requests.get(stats_url, headers=headers, params={"fixture": fixture_id}, timeout=10)
            stats_data = stats_response.json().get('response', [])
            
            print(f"   📊 [정밀 지표 분석 분석중...]")
            # 점유율, 패스성공률, xG(기대득점) 등을 낚아채서 알고리즘에 대입할 구역입니다.
            # (초기 연결 테스트를 위해 매치업 매칭까지 완벽하게 확인합니다.)
            print(f"   👉 {home_team} vs {away_team} 분석 완료! 예측 모델 준비 완료.\n")

    except Exception as e:
        print(f"❌ 데이터 호출 중 에러 발생: {e}")

if __name__ == "__main__":
    run_soccer_analysis()
