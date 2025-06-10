# crawler_logger.py
import os, json
from datetime import datetime
from services.slack import send_slack_message

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_crawler_event(event_type: str, message: str, extra: dict = None, notify: bool = False):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    filepath = os.path.join(LOG_DIR, f"crawler_log_{today}.jsonl")
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "message": message,
        "extra": extra or {}
    }
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    if notify:
        send_slack_message(f"🛠️ *{event_type.upper()}*: {message}\n```{json.dumps(extra, ensure_ascii=False)}```")
