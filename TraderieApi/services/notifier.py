import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from services.daily_report import run_daily_log_summary
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/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"

    
def notify_admin(log):
    message = (
        f"🚨 *의심 접근 감지!*\n"
        f"*IP:* {log['ip']}\n"
        f"*경로:* {log['path']}\n"
        f"*사유:* {log.get('reason', '알 수 없음')}\n"
        f"*UA:* {log['user_agent']}"
    )
    try:
        httpx.post(SLACK_WEBHOOK_URL, json={"text": message})
    except Exception as e:
        print(f"Slack 알림 실패: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_daily_log_summary, 'cron', hour=9)  # 매일 오전 9시
    scheduler.start()