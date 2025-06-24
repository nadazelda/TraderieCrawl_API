# utils/slack.py
import httpx

SLACK_WEBHOOK_URL=""

def send_slack_message(text: str):
    try:
        httpx.post(SLACK_WEBHOOK_URL, json={"text": text})
    except Exception as e:
        print(f"[Slack 전송 실패] {e}")
