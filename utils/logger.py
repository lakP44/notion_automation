import os
from datetime import datetime
import pytz # 한국 시간대 처리를 위한 pytz 모듈

def write_log(log_dir: str, message: str, flag: bool = True) -> None:
    '''
    로그 메시지를 지정된 디렉토리에 날짜별로 저장하는 함수
    
    Args:
        log_dir: 로그 파일을 저장할 디렉토리 경로
        message: 로그로 기록할 메시지
        flag: 로그 기록 여부를 결정하는 플래그 (기본값: True)
    Returns:
        이 함수는 반환값이 없습니다. 로그 파일에 메시지를 기록합니다.
    '''
    if flag:
        os.makedirs(log_dir, exist_ok=True)
        kst = pytz.timezone("Asia/Seoul")
        now = datetime.now(kst)
        today = now.strftime("%Y-%m-%d")
        log_path = os.path.join(log_dir, f"cron_{today}.log")

        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")