# GANADI TODO Discord Bot

이 저장소는 간단한 할일 관리용 디스코드 봇입니다. 슬래시 명령어를 사용하여 개인별 할일을 추가하거나 조회하고 완료 표시를 할 수 있습니다.

## 주요 기능
- `/할일추가 [내용]` : 새로운 할일을 등록합니다.
- `/할일목록` : 진행 중 또는 완료된 할일 목록을 확인합니다.
- `/할일완료 [번호]` : 특정 할일을 완료 처리합니다.
- `/할일삭제 [번호]` : 할일을 목록에서 삭제합니다.
- `/할일초기화` : 모든 할일을 삭제합니다.
- `/도움말` : 명령어 사용법을 보여줍니다.

## 실행 방법
1. Python 3.8 이상을 준비합니다.
2. 의존성 설치:
   ```bash
   pip install discord python-dotenv
   ```
3. `.env` 파일을 생성하고 다음 내용을 넣습니다.
   ```
   DISCORD_BOT_TOKEN=디스코드_봇_토큰
   ```
4. 봇 실행:
   ```bash
   python GANADIBOT_todo.py
   ```

봇 실행 중 생성되는 `todos.json` 파일에 사용자별 할일 정보가 저장됩니다.
