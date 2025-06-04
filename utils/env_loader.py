import os

from utils.logger import write_log # 로그 작성을 위한 유틸리티 함수

# 환경변수 로드 함수
def load_env_variables():
    '''
    환경변수를 로드하는 함수
    
    Args:
        이 함수는 인자를 받지 않습니다.
        
    Returns:
        이 함수는 반환값이 없습니다. 환경변수 로드 상태를 로그로 기록합니다.
    '''
    required_keys = [
        "NOTION_TOKEN",
        "NOTION_CREATE_PLAN_DB_ID",
        "NOTION_CREATE_PLAN_PAGE_ID",
        "NOTION_VIEW_PLAN_DB_ID",
        "NOTION_VIEW_PLAN_PAGE_ID"
    ]
    for key in required_keys:
        if os.getenv(key) is None:
            write_log("logs", f"환경변수 '{key}'가 설정되지 않았습니다.")
        else:
            write_log("logs", f"환경변수 '{key}'가 정상적으로 로드되었습니다.")
