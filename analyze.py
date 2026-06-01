import os
import requests
from datetime import datetime, timedelta

def run_deep_analysis():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    if not api_key:
        print("❌ 에러: FOOTBALL_API_KEY가 없습니다.")
        return

    # 🚨 [핵심 패치 1] 열쇠 구멍 이름을 본사 규격(x-apisports-key)으로 변경!
    headers = {
        'x-apisports-key': api_key
    }

    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')

    print(f"=========================================")
    print(f"🧠 [축구 AI 분석실 v2.0] 본사 다이렉트 연결 모드")
    print(f"👉 대상 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    target_league = "66"  
    seasons_to_try = ["2025", "2026"]
    fixtures = []
    
    # 🚨 [핵심 패치 2] 접속 주소를 본사(v3.football.api-sports.io)로 변경!
    url = "https://v3.football.api-sports.io/fixtures"
    
    for season in seasons_to_try:
        querystring = {
            "league": target_league,
            "season": season,
            "date": date_string,
            "timezone": "Asia/Seoul"
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            data = response.json()
            
            # API 키가 틀렸거나 문제가 생기면 숨기지 않고 화면에 뱉어내도록 안전장치 추가
            if 'errors' in data and data['errors']:
                print(f"⚠️ {season}년 조회 에러: {data['errors']}")
            if 'message' in data:
                print(f"❌ 본사 서버 인증 에러: {data['message']}")
                return

            if 'response' in data and data['response']:
                fixtures = data['response']
                print(f"✅ 빙고! 본사 서버의 '{season}년' 카테고리에서 매치업을 찾아냈습니다!\n")
                break 
        except Exception as e:
            print(f"통신 에러: {e}")

    if not fixtures:
        print(f"❌ {target_league}번 리그의 오늘 일정을 찾지 못했습니다.")
        return

    for match in fixtures:
        fixture_id = match['fixture']['id']
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        status = match['fixture']['status']['long']

        print(f"🔥 매치업: {home} vs {away} [{status}]")

        # 🚨 스탯 추출 주소도 본사 주소로 변경!
        stats_url = "https://v3.football.api-sports.io/fixtures/statistics"
        stats_res = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
        stats_data = stats_res.json().get('response', [])

        if not stats_data:
            print("  ⚠️ 경기 시작 전이거나, 서버에 세부 스탯이 아직 집계되지 않았습니다.\n")
            continue

        print("  📊 [핵심 전력 지표 비교]")
        for team_stat in stats_data:
            team_name = team_stat['team']['name']
            statistics = team_stat['statistics']

            possession = next((item['value'] for item in statistics if item['type'] == 'Ball Possession'), 'N/A')
            passes = next((item['value'] for item in statistics if item['type'] == 'Passes %'), 'N/A')
            shots_on_goal = next((item['value'] for item in statistics if item['type'] == 'Shots on Goal'), 'N/A')

            print(f"  [{team_name}] 점유율: {possession} | 패스성공률: {passes} | 유효슈팅: {shots_on_goal}")
        print("-" * 40)

if __name__ == "__main__":
    run_deep_analysis()
