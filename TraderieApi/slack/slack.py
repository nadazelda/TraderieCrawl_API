# utils/slack.py
import httpx

SLACK_WEBHOOK_URL="https://hooks.slack.com/services/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"

def send_slack_message(text: str):
    try:
        httpx.post(SLACK_WEBHOOK_URL, json={"text": text})
    except Exception as e:
        print(f"[Slack 전송 실패] {e}")
