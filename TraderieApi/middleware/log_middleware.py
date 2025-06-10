import os
import time
import json
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Message
from fastapi.responses import JSONResponse
from slack.slack_webhook import notify_slack


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.log_dir = "server_logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file_path = os.path.join(self.log_dir, "access.log")

        # 공격 패턴 예시 (확장 가능)
        self.suspicious_patterns = [
            r"(?:\bselect\b|\binsert\b|\bupdate\b|\bdelete\b).*?\bfrom\b",  # SQL 인젝션
            r"<script.*?>.*?</script>",  # XSS
            r"\b(or|and)\b\s+\d+=\d+",   # 조건문 인젝션
            r"\bUNION\b.*\bSELECT\b",    # UNION SQL
        ]

        # 민감 경로 감시
        self.restricted_paths = ["/admin", "/env", "/.git", "/config"]

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()


        try:
            body_bytes = await request.body()
        except Exception:
            body_bytes = b''

        async def receive() -> Message:
            return {"type": "http.request", "body": body_bytes}

        request = Request(request.scope, receive)
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else None
        query_string = request.url.query
        body_text = body_bytes.decode("utf-8", errors="ignore")
        suspicious = self._detect_attack(query_string + body_text)
        restricted_access = path in self.restricted_paths

        # 의심 행위가 탐지되거나 접근 제한 경로 접근 시
        if suspicious or restricted_access:
            alert_log = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "query": query_string,
                "body": body_text,
                "suspicious": suspicious,
                "restricted_access": restricted_access,
            }
            self._log(alert_log, alert=True)
            # 기존 self._log(alert_log, alert=True) 뒤에 추가
            await notify_slack(
                f"🚨 *의심 요청 탐지!*\n📍IP: {client_ip}\n📄경로: {path}\n🕒시간: {alert_log['timestamp']}"
            )


            # 차단 응답도 가능 (선택 사항)
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})

        try:
            response = await call_next(request)
        except Exception:
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        process_time = round((time.time() - start_time) * 1000, 2)

        access_log = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "client_ip": client_ip,
            "method": method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_ms": process_time,
            "headers": dict(request.headers),
            "body": body_text,
        }
        self._log(access_log)
       
        return response

    def _detect_attack(self, text: str) -> bool:
        """의심스러운 패턴 탐지"""
        text = text.lower()
        return any(re.search(pattern, text) for pattern in self.suspicious_patterns)

    def _log(self, data: dict, alert=False):
        """로그 파일 저장 (공격 탐지 여부 구분 가능)"""
        try:
            filename = "alerts.log" if alert else "access.log"
            path = os.path.join(self.log_dir, filename)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[LoggingMiddleware Error] 로그 저장 실패: {e}")

    