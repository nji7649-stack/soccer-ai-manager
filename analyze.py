import os
import requests
from datetime import datetime, timedelta

def run_all_catch_radar():
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
    print(f"📡 [축구 AI 분석실] 전 세계 모든 경기 레이더망 가동")
    print(f"👉 검색 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    # 리그 지정 없이 오늘 날짜의 '모든' 경기 호출
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"date": date_string, "timezone": "Asia/Seoul"}

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        
        if 'response' in data and data['response']:
            fixtures = data['response']
            print(f"✅ 통신 성공! 오늘 전 세계에서 총 {len(fixtures)}개의 경기가 감지되었습니다.\n")
            print("🎯 [국가대표(World) 및 주요 매치업 필터링 결과]")
            
            found_target = False
            
            for match in fixtures:
                country = match['league']['country']
                league_name = match['league']['name']
                league_id = match['league']['id']
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                status = match['fixture']['status']['short']
                
                # API 분류상 국가대표(World)이거나, 팀 이름에 'Canada' 또는 주요 키워드가 들어간 경기만 쏙 뽑아냅니다.
                if country == 'World' or 'Canada' in home or 'Canada' in away:
                    print(f"👉 [진짜 리그ID: {league_id} | {country} - {league_name}] {home} vs {away} [{status}]")
                    found_target = True
                    
            if not found_target:
                print("😭 캐나다 경기나 World 카테고리를 찾지 못했습니다.")
                print("💡 (참고) 오늘 감지된 전체 리그 목록 중 일부:")
                leagues = list(set([f"{m['league']['country']} - {m['league']['name']} (ID: {m['league']['id']})" for m in fixtures]))
                for l in leagues[:10]:
                    print(f"  - {l}")
                    
        else:
            print("❌ API 서버가 오늘 날짜의 전체 경기 데이터를 주지 않고 있습니다.")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    run_all_catch_radar()
