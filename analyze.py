import os
import requests
from datetime import datetime, timedelta

def run_pro_analysis():
    # 깃허브 금고에서 열쇠 꺼내기
    api_key = os.environ.get('FOOTBALL_API_KEY')
    headers = {'x-apisports-key': api_key}

    # 한국 시간 기준 '오늘' 날짜 자동 추적
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    season = kst_now.strftime('%Y') # 2026 등 자동 인식

    print(f"=========================================")
    print(f"🏆 [축구 AI 분석실 v3.0] PRO 플랜 가동 중")
    print(f"👉 분석 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    # 분석할 리그 ID 모음 (1: 월드컵, 10: A매치 친선, 39: 프리미어리그, 66: 기타 친선 등)
    # Pro 플랜이므로 원하는 리그를 마음껏 추가하실 수 있습니다.
    target_leagues = ["1", "10", "39", "66"]  
    
    url = "https://v3.football.api-sports.io/fixtures"
    total_matches_found = 0
    
    for league_id in target_leagues:
        querystring = {
            "league": league_id,
            "season": season,
            "date": date_string,
            "timezone": "Asia/Seoul"
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            data = response.json()
            
            if 'errors' in data and data['errors']:
                continue # 에러나면 조용히 다음 리그로 패스

            fixtures = data.get('response', [])
            if not fixtures:
                continue # 해당 리그에 오늘 경기가 없으면 패스

            total_matches_found += len(fixtures)
            print(f"\n✅ [리그 ID: {league_id}] {len(fixtures)}경기 분석 시작!")

            for match in fixtures:
                fixture_id = match['fixture']['id']
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                status = match['fixture']['status']['long']

                print(f"🔥 매치업: {home} vs {away} [{status}]")

                # PRO 전용 정밀 스탯 추출
                stats_url = "https://v3.football.api-sports.io/fixtures/statistics"
                stats_res = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
                stats_data = stats_res.json().get('response', [])

                if not stats_data:
                    print("  ⚠️ 경기 전이거나 세부 스탯 대기 중입니다.")
                    continue

                print("  📊 [핵심 전력 지표]")
                for team_stat in stats_data:
                    team_name = team_stat['team']['name']
                    statistics = team_stat['statistics']

                    possession = next((item['value'] for item in statistics if item['type'] == 'Ball Possession'), 'N/A')
                    passes = next((item['value'] for item in statistics if item['type'] == 'Passes %'), 'N/A')
                    shots_on_goal = next((item['value'] for item in statistics if item['type'] == 'Shots on Goal'), 'N/A')

                    print(f"  [{team_name}] 점유율: {possession} | 패스성공률: {passes} | 유효슈팅: {shots_on_goal}")
                print("-" * 40)

        except Exception as e:
            print(f"통신 에러 발생: {e}")

    if total_matches_found == 0:
        print("\n📅 타겟으로 설정하신 리그들에 오늘은 예정된 경기가 없습니다.")

if __name__ == "__main__":
    run_pro_analysis()
