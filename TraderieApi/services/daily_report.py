import json
import httpx


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