import os
from datetime import datetime
import pytz

def write_log(log_dir: str, message: str):
    os.makedirs(log_dir, exist_ok=True)
    kst = pytz.timezone("Asia/Seoul")
    now = datetime.now(kst)
    today = now.strftime("%Y-%m-%d")
    log_path = os.path.join(log_dir, f"cron_{today}.log")

    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")