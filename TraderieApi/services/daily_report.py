import json
import httpx
from services.notifier import send_daily_summary_to_slack

def run_daily_log_summary():
    try:
        res = httpx.get("http://localhost:8000/logs/stats")  # fast api 내부 엔드포인트 주소를 호출 
        if res.status_code == 200:
            summary = res.json()
            send_daily_summary_to_slack(summary)
        else:
            print("[요약 실패] stats API 응답 오류", res.status_code)
    except Exception as e:
        print("[요약 실패] 예외 발생", e)
