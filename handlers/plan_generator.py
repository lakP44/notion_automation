# 캘린더 계획 생성 및 상태 갱신 로직을 포함하는 모듈
import time

from utils.logger import write_log # 로그 작성을 위한 유틸리티 함수

from .repeat_daily import handle_daily_repeat
from .repeat_weekly import handle_weekly_repeat
from .repeat_specific_days import handle_specific_day_repeat
from .repeat_none import handle_no_repeat
from .status_updater import update_old_plan_status

# 전체 생성 계획에 대해 반복 유형에 따라 처리
def generate_calendar_plans(notion, total_create_db_result, week_view_db_result, all_view_db_result):
    '''
    전체 생성 계획에 대해 반복 유형에 따라 처리
    
    Args:
        notion (Client): Notion API 클라이언트 인스턴스
        total_create_db_result (dict): 생성 계획 데이터
        total_view_db_result (dict): 전체 계획 데이터
        all_view_db_result (dict): 주간 필터링된 전체 계획 데이터
        
    Returns:
        이 함수는 반환값이 없습니다. 각 계획에 대해 적절한 반복 유형을 처리하고, 상태를 업데이트합니다.
    '''
    write_log("logs", "전체 생성 계획을 반복 유형에 따라 처리합니다.", False)

    for title, data in total_create_db_result.items():
        
        repeat = data["반복 유형"]
        
        if data["종료됨"] or data["일시중지"]:
            if data["반복 유형"] != "매주 n회":
                write_log("logs", f"계획 '{title}'은 종료되었거나 일시중지 상태입니다. 건너뜁니다.", False)
                continue

        if repeat == "매일":
            handle_daily_repeat(notion, title, data, week_view_db_result)
        elif repeat == "매주 n회":
            handle_weekly_repeat(notion, title, data, week_view_db_result, all_view_db_result)
        elif repeat == "특정 요일":
            handle_specific_day_repeat(notion, title, data, week_view_db_result)
        elif repeat == "없음":
            handle_no_repeat(notion, title, data, week_view_db_result)
            
        time.sleep(0.5)  # API 호출 간의 지연을 추가하여 요청 속도 제한을 피함

    # 이전 주 계획 상태 업데이트
    update_old_plan_status(notion, week_view_db_result, all_view_db_result)
