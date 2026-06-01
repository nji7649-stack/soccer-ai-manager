import os
import requests
from datetime import datetime, timedelta

def run_deep_analysis():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    if not api_key:
        print("❌ 에러: FOOTBALL_API_KEY가 없습니다.")
        return

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
    }

    # 한국 시간 기준 오늘 날짜
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    season = kst_now.strftime('%Y')

    print(f"=========================================")
    print(f"🧠 [축구 AI 분석실 v2.0] 정밀 스탯 추출 모드")
    print(f"👉 대상 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    # 🚨 [중요] 감독님이 사진에서 찾으신 '진짜 리그 ID'를 아래 숫자에 넣어주세요!
    # 예시: 사진에 [진짜 리그ID: 66] 이라고 나왔다면 "66"을 입력합니다.
    target_league = "66"  

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {
        "league": target_league,
        "season": season,
        "date": date_string,
        "timezone": "Asia/Seoul"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        fixtures = response.json().get('response', [])

        if not fixtures:
            print(f"❌ {target_league}번 리그의 오늘 일정을 찾지 못했습니다. (시즌 연도를 2025로 바꿔서 시도해보세요)")
            return

        for match in fixtures:
            fixture_id = match['fixture']['id']
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            status = match['fixture']['status']['long']

            print(f"\n🔥 매치업: {home} vs {away} [{status}]")

            # ---------------------------------------
            # 💡 드디어! 정밀 스탯(점유율, 패스 등) 호출
            # ---------------------------------------
            stats_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
            stats_res = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
            stats_data = stats_res.json().get('response', [])

            # 경기가 아직 시작 전이면 스탯 데이터가 없습니다.
            if not stats_data:
                print("  ⚠️ 경기 시작 전이거나, 서버에 세부 스탯이 아직 집계되지 않았습니다.")
                continue

            print("  📊 [핵심 전력 지표 비교]")
            for team_stat in stats_data:
                team_name = team_stat['team']['name']
                statistics = team_stat['statistics']

                # 원하는 정밀 데이터 뽑아내기 (점유율, 패스성공률, 유효슈팅)
                possession = next((item['value'] for item in statistics if item['type'] == 'Ball Possession'), 'N/A')
                passes = next((item['value'] for item in statistics if item['type'] == 'Passes %'), 'N/A')
                shots_on_goal = next((item['value'] for item in statistics if item['type'] == 'Shots on Goal'), 'N/A')

                print(f"  [{team_name}] 점유율: {possession} | 패스성공률: {passes} | 유효슈팅: {shots_on_goal}")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    run_deep_analysis()
