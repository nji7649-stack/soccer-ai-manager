import os
import requests
from datetime import datetime, timedelta

def safe_num(value):
    if value is None or value == 'N/A': return 0
    if isinstance(value, str): return float(value.replace('%', ''))
    return float(value)

def run_pro_analysis():
    api_key = os.environ.get('FOOTBALL_API_KEY')
    headers = {'x-apisports-key': api_key}

    # 한국 시간 기준 오늘 날짜
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    season = kst_now.strftime('%Y')

    print(f"=========================================")
    print(f"🏆 [축구 AI 분석실 v5.0] 시각화 대시보드 모드")
    print(f"👉 분석 날짜: {date_string} (KST)")
    print(f"=========================================\n")

    # 월드컵, 친선, EPL(39), 라리가(140), 세리에A(135), 분데스(78), 리그1(61) 등
    target_leagues = ["1", "10", "39", "66", "140", "135", "78", "61"]
    url = "https://v3.football.api-sports.io/fixtures"
    
    # 🎨 HTML 웹페이지 뼈대 준비 (다크 모드 스포츠 UI)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI 축구 승부 예측 리포트</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #00E676; }}
            .date {{ text-align: center; color: #aaaaaa; margin-bottom: 30px; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
            .card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 12px; width: 350px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }}
            .league {{ font-size: 0.8em; color: #ff9800; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }}
            .match {{ font-size: 1.2em; font-weight: bold; margin-bottom: 15px; text-align: center; }}
            .stat-box {{ background: #2a2a2a; padding: 10px; border-radius: 8px; font-size: 0.9em; margin-bottom: 15px; color: #ccc; }}
            .result {{ font-size: 1em; font-weight: bold; color: #00E676; border-top: 1px dashed #444; padding-top: 15px; text-align: center; line-height: 1.6; }}
            .no-match {{ text-align: center; color: #ff5
