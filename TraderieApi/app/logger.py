# app/logger.py

import os
import logging
from logging.handlers import RotatingFileHandler

# 로그 디렉토리 설정
LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# 🔹 /ping 로그 제외 필터 정의
class IgnorePingFilter(logging.Filter):
    def filter(self, record):
        return '/ping' not in record.getMessage()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)

# 🔹 필터 적용 to uvicorn.access
logging.getLogger("uvicorn.access").addFilter(IgnorePingFilter())

# 공용 로거 export
logger = logging.getLogger("app")
