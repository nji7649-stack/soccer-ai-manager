import os
import requests

def run_deep_analysis():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    headers = {'x-apisports-key': api_key}

    # 💡 [핵심 패치] API 서버가 친절하게 허락해 준 정답지 날짜로 세팅!
    date_string = "2026-06-01" 
    season = "2026"

    print(f"=========================================")
    print(f"🧠 [축구 AI 분석실 v2.0] 무료 플랜 통과 테스트")
    print(f"👉 대상 날짜: {date_string}")
    print(f"=========================================\n")

    target_league = "66"  
    
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {
        "league": target_league,
        "season": season,
        "date": date_string,
        "timezone": "Asia/Seoul"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        
        # 서버에서 에러를 주면 그대로 출력
        if 'errors' in data and data['errors']:
            print(f"⚠️ 에러 발생: {data['errors']}")
            return

        fixtures = data.get('response', [])
        
        if not fixtures:
            print(f"❌ {date_string}에 {target_league}번 리그 일정이 없습니다.")
            return

        print(f"✅ 빙고! API 서버가 허락한 {date_string} 데이터 억세스 성공!\n")

        for match in fixtures[:3]: # 3경기만 샘플로 출력
            fixture_id = match['fixture']['id']
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            status = match['fixture']['status']['long']

            print(f"🔥 매치업: {home} vs {away} [{status}]")

            # 정밀 스탯 추출
            stats_url = "https://v3.football.api-sports.io/fixtures/statistics"
            stats_res = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
            stats_data = stats_res.json().get('response', [])

            if not stats_data:
                print("  ⚠️ 세부 스탯 데이터가 아직 서버에 없습니다.\n")
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

    except Exception as e:
        print(f"통신 에러: {e}")

if __name__ == "__main__":
    run_deep_analysis()
