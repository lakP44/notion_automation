# 캘린더 계획 생성 및 상태 갱신 로직을 포함하는 모듈
from utils.constants import TODAY
from .repeat_daily import handle_daily_repeat
from .repeat_weekly import handle_weekly_repeat
from .repeat_specific_days import handle_specific_day_repeat
from .repeat_none import handle_no_repeat
from .status_updater import update_old_plan_status

# 전체 생성 계획에 대해 반복 유형에 따라 처리
def generate_calendar_plans(notion, total_create_db_result, total_view_db_result, all_view_db_result):
    for title, data in total_create_db_result.items():
        repeat = data["반복 유형"]
        
        if data["종료됨"] or data["일시중지"]:
            continue

        if repeat == "매일":
            handle_daily_repeat(notion, title, data, total_view_db_result)
        elif repeat == "매주 n회":
            handle_weekly_repeat(notion, title, data, total_view_db_result, all_view_db_result)
        elif repeat == "특정 요일":
            handle_specific_day_repeat(notion, title, data, total_view_db_result)
        elif repeat == "없음":
            handle_no_repeat(notion, title, data, total_view_db_result)

    # 이전 주 계획 상태 업데이트
    update_old_plan_status(notion, total_view_db_result, all_view_db_result)
