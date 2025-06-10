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


def send_daily_summary_to_slack(summary: dict):
    msg = (
        f"📊 *일일 로그 요약 ({summary['date']})*\n"
        f"총 요청 수: {summary['total_requests']}\n"
        f"의심 요청 수: {summary['suspicious_requests']}\n"
        f"메서드 분포: {summary['methods']}\n"
        f"Top 경로:\n" +
        "".join([f"• {path} ({count}회)\n" for path, count in summary['top_paths']]) +
        f"의심 사유:\n" +
        "".join([f"• {reason} ({count}회)\n" for reason, count in summary['suspicious_reasons']])
    )
    try:
        httpx.post(SLACK_WEBHOOK_URL, json={"text": msg})
    except Exception as e:
        print(f"[Slack 요약 실패] {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_daily_log_summary, 'cron', hour=9)  # 매일 오전 9시
    scheduler.start()