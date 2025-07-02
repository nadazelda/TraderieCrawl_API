import httpx
import os

SLACK_WEBHOOK_URL=""

async def notify_slack(message: str):
    if not SLACK_WEBHOOK_URL:
        print("[Slack] Webhook URL이 설정되지 않았습니다.")
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(SLACK_WEBHOOK_URL, json={"text": message})
    except Exception as e:
        print(f"[Slack Notify Error] {e}")
