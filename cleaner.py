# cleaner.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 💡 악성 유령 공백(\xa0)을 순수 일반 띄어쓰기로 100% 강제 치환
clean_content = content.replace('\xa0', ' ')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(clean_content)

print("✨ 세탁 완료! 이제 app.py를 다시 실행해보세요.")
