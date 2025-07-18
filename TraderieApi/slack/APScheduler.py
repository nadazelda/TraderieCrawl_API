from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from collections import Counter
import json, os
from pytz import timezone
from slack.slack_webhook import notify_slack  # 슬랙 전송 함수 임포트





def start_scheduler():
    scheduler = AsyncIOScheduler()
    # KST 시간대 지정
    kst = timezone("Asia/Seoul")

    @scheduler.scheduled_job(CronTrigger(hour='10,15,21', minute=00, timezone=kst)) # 매일 00:00 실행
    async def send_daily_log_stats():
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        file_path = f"logs/server_log_{date_str}.jsonl"
        
        # yesterday_utc = datetime.utcnow() - timedelta(days=1)
        # date_str = yesterday_utc.strftime("%Y-%m-%d")
        # file_path = f"logs/server_log_{date_str}.jsonl"

        suspicious_count = 0
        total_count = 0
        ips = Counter()

        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    log = json.loads(line)
                    total_count += 1
                    ip = log.get("ip")
                    if ip:
                        ips[ip] += 1
                    if log.get("suspicious"):
                        suspicious_count += 1

            # 슬랙 요약 메시지 전송
            summary = (
                f"📊 *{date_str} 로그 요약*\n"
                f"🔸 총 요청 수: {total_count}\n"
                f"🚨 의심 요청 수: {suspicious_count}\n"
                f"👥 고유 IP 수: {len(ips)}\n"
                f"🏆 Top IP: {', '.join([f'{ip}({cnt})' for ip, cnt in ips.most_common(3)])}"
            )
            await notify_slack(summary)

        except FileNotFoundError:
            await notify_slack(f"📂 {date_str} 로그 파일이 존재하지 않습니다.")
        except Exception as e:
            await notify_slack(f"⚠️ 슬랙 통계 전송 실패: {e}")

    scheduler.start()
