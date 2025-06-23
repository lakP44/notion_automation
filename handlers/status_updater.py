import pandas as pd

from utils.constants import GetToday, GetTodayStr
from utils.logger import write_log  # 로그 작성을 위한 유틸리티 함수

# 이전 주 계획 상태 업데이트
def update_old_plan_status(notion, week_view_db_result, all_view_db_result):
    '''
    이전 주 계획의 상태를 업데이트하는 함수
    
    Args:
        notion (Client): Notion API 클라이언트 인스턴스
        week_view_db_result (dict): 주간 필터링된 전체 계획 데이터
        all_view_db_result (dict): 전체 계획 데이터
        
    Returns:
        이 함수는 반환값이 없습니다. Notion에 계획 상태를 업데이트합니다.
    '''
    TODAY = GetToday()
    TODAY_STR = GetTodayStr()

    write_log("logs", f"-------------------- 이전 계획 상태 업데이트 시작 --------------------", False)

    for k, v in week_view_db_result.items():
        plan_date = v["시작일"]
        plan_stat = v["계획 상태"]
        is_completed = v.get("완료", False)

        if "(" in k and "회 남음" in k:
            write_log("logs", f"계획 '{k}'은 매주 n회 반복 계획으로 이곳에서 처리하지 않습니다.", False)
            continue

        if ((plan_date.date() < TODAY.date()) and (not is_completed) and (plan_stat != "잠시 중지")):
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "실패"}}}
            )
            write_log("logs", f"계획 '{k}'이 실패 상태로 업데이트되었습니다.", False)
        elif ((plan_date.date() < TODAY.date()) and is_completed and (plan_stat != "잠시 중지")):
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "완료"}}}
            )
            write_log("logs", f"계획 '{k}'이 완료 상태로 업데이트되었습니다.", False)

    if (TODAY.weekday() == 6):
        for k, v in all_view_db_result.items():
            plan_date = v["시작일"].date()
            is_completed = v.get("완료", False)

            if "(" in k and "회 남음" in k:
                write_log("logs", f"계획 '{k}'은 매주 n회 반복 계획으로 이곳에서 처리하지 않습니다.", False)
                continue

            if ((plan_date == TODAY.date() - pd.Timedelta(days=1)) and (v["계획 상태"] != "잠시 중지")):
                new_stat = "완료" if is_completed else "실패"
                notion.pages.update(
                    page_id=v["id"],
                    properties={"계획 상태": {"status": {"name": new_stat}}}
                )
                write_log("logs", f"계획 '{k}'이 {new_stat} 상태로 업데이트되었습니다.", False)

    write_log("logs", f"-------------------- 오늘 계획 상태 업데이트 시작 --------------------", False)
    for k, v in week_view_db_result.items():
        if ((v["시작일"] == TODAY) and (v["계획 상태"] != "진행 중")):
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "진행 중"}}}
            )
            write_log("logs", f"계획 '{k}'이 진행 중 상태로 업데이트되었습니다.", False)
