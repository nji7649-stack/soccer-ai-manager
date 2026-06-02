import os
import requests
from datetime import datetime, timedelta

# 숫자로 안전하게 변환해주는 마법의 헬퍼 함수
def safe_num(value):
    if value is None or value == 'N/A':
        return 0
    if isinstance(value, str):
        return float(value.replace('%', ''))
    return float(value)

def run_pro_analysis():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    headers = {'x-apisports-key': api_key}

    # 한국 시간 기준 오늘 날짜 (Pro 플랜이므로 오늘 실시간 데이터 억세스!)
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    season = kst_now.strftime('%Y')

    print(f"=========================================")
    print(f"🏆 [축구 AI 분석실 v4.0] 3-in-1 통합 예측 엔진 가동")
    print(f"👉 분석 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    target_leagues = ["1", "10", "39", "66"]  
    url = "https://v3.football.api-sports.io/fixtures"
    total_matches_found = 0
    
    for league_id in target_leagues:
        querystring = {"league": league_id, "season": season, "date": date_string, "timezone": "Asia/Seoul"}
        
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            fixtures = response.json().get('response', [])
            if not fixtures: continue

            total_matches_found += len(fixtures)
            print(f"\n✅ [리그 ID: {league_id}] {len(fixtures)}경기 인공지능 분석 시작!\n")

            for match in fixtures:
                fixture_id = match['fixture']['id']
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                status = match['fixture']['status']['short']

                stats_url = "https://v3.football.api-sports.io/fixtures/statistics"
                stats_res = requests.get(stats_url, headers=headers, params={"fixture": fixture_id})
                stats_data = stats_res.json().get('response', [])

                if not stats_data or len(stats_data) < 2:
                    print(f"⚽ {home_team} vs {away_team} [{status}] -> ⚠️ 분석 대기 중 (데이터 부족)")
                    continue

                # 양 팀 데이터 추출
                home_stats = stats_data[0]['statistics']
                away_stats = stats_data[1]['statistics']

                h_poss = safe_num(next((item['value'] for item in home_stats if item['type'] == 'Ball Possession'), 0))
                h_pass = safe_num(next((item['value'] for item in home_stats if item['type'] == 'Passes %'), 0))
                h_shot = safe_num(next((item['value'] for item in home_stats if item['type'] == 'Shots on Goal'), 0))

                a_poss = safe_num(next((item['value'] for item in away_stats if item['type'] == 'Ball Possession'), 0))
                a_pass = safe_num(next((item['value'] for item in away_stats if item['type'] == 'Passes %'), 0))
                a_shot = safe_num(next((item['value'] for item in away_stats if item['type'] == 'Shots on Goal'), 0))

                print(f"⚽ 매치업: {home_team} vs {away_team} [{status}]")
                print(f"   📊 [데이터] {home_team} (점유율 {h_poss}% / 슈팅 {h_shot}개) vs {away_team} (점유율 {a_poss}% / 슈팅 {a_shot}개)")

                # 💡 [모델 1] 승무패 예측 (점유율 0.1점, 유효슈팅 1.5점 가중치)
                h_score = (h_poss * 0.1) + (h_shot * 1.5)
                a_score = (a_poss * 0.1) + (a_shot * 1.5)
                
                if h_score > a_score + 2.5:
                    win_pick = f"[{home_team} 우세 📈]"
                elif a_score > h_score + 2.5:
                    win_pick = f"[{away_team} 우세 📈]"
                else:
                    win_pick = "[무승부 접전 ⚖️]"

                # 💡 [모델 2] 주도권(수비) 예측
                if h_poss > a_poss + 15:
                    control_pick = f"{home_team}의 일방적 경기 지배"
                elif a_poss > h_poss + 15:
                    control_pick = f"{away_team}의 일방적 경기 지배"
                else:
                    control_pick = "치열한 중원 싸움"

                # 💡 [모델 3] 언오버 예측 (유효슈팅 합산 기준)
                total_shots = h_shot + a_shot
                if total_shots >= 9:
                    over_under = "🔥 오버(다득점) 페이스"
                elif total_shots <= 5:
                    over_under = "🛡️ 언더(저득점) 페이스"
                else:
                    over_under = "⚖️ 예측 불가 (변수 큼)"

                print(f"   🤖 [AI 예측] {win_pick} | 주도권: {control_pick} | 흐름: {over_under}")
                print("-" * 50)

        except Exception as e:
            print(f"통신 에러 발생: {e}")

    if total_matches_found == 0:
        print("\n📅 타겟으로 설정하신 리그들에 오늘은 예정된 경기가 없습니다.")

if __name__ == "__main__":
    run_pro_analysis()
