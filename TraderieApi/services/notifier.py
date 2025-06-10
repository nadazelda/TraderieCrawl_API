# services/notifier.py
from apscheduler.schedulers.background import BackgroundScheduler
from utils.slack import send_slack_message
from services.daily_report import run_daily_log_summary


def notify_admin(log):
    message = (
        f"🚨 *의심 접근 감지!*\n"
        f"*IP:* {log['ip']}\n"
        f"*경로:* {log['path']}\n"
        f"*사유:* {log.get('reason', '알 수 없음')}\n"
        f"*UA:* {log['user_agent']}"
    )
    send_slack_message(message)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_daily_log_summary, 'cron', hour=9)
    scheduler.start()
