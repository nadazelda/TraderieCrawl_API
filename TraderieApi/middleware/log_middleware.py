import time, os, json
from datetime import datetime
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from services.notifier import notify_admin

class LoggingMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, log_dir="logs"):
        super().__init__(app)
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_filepath(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"server_log_{today}.jsonl")

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        ip = request.client.host
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "")
        suspicious = False
        reason = None
        try:
            body = await request.body()
            body_str = body.decode('utf-8') if body else ""
        except:
            body_str = ""

        try:
            response = await call_next(request)
        except Exception as e:
            response = JSONResponse(content={"detail": "Internal Server Error"}, status_code=500)
            reason = "서버 내부 에러"
            suspicious = True
        duration = round((time.time() - start_time) * 1000, 2)



        # 비정상 파라미터 및 공격 시도 탐지
        suspicious_keywords = ["drop ", "union ", "<script", "1=1", "alert(", "onerror=", "document.cookie"]
        if any(word in body_str.lower() for word in suspicious_keywords):
            suspicious = True
            reason = "SQL/스크립트 공격 의심"

        # 특정 경로에 대한 접근 제한 및 감시
        if path.startswith("/admin") or path.startswith("/internal"):
            suspicious = True
            reason = "비허용 경로 접근 시도"

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "ip": ip,
            "method": method,
            "path": path,
            "query": str(request.query_params),
            "body": body_str,
            "status_code": response.status_code,
            "user_agent": user_agent,
            "duration_ms": duration,
            "suspicious": suspicious
        }

        if suspicious and reason:
            log_data["reason"] = reason

        with open(self._get_log_filepath(), "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")

        if suspicious:
            notify_admin(log_data)

        return response

