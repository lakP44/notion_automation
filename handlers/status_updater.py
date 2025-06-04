import pandas as pd

from utils.constants import TODAY
from utils.logger import write_log  # 로그 작성을 위한 유틸리티 함수

# 이전 주 계획 상태 업데이트
def update_old_plan_status(notion, total_view_db_result, all_view_db_result):
    write_log("logs", f"-------------------- 이전 계획 상태 업데이트 시작 --------------------")
    
    for k, v in total_view_db_result.items():
        plan_date = pd.to_datetime(v["시작일"], errors="coerce").date()
        plan_stat = v["계획 상태"]
        is_completed = v.get("완료", False)

        if "(" in k and "회 남음" in k:
            write_log("logs", f"계획 '{k}'은 매주 n회 반복 계획으로 이곳에서 처리하지 않습니다.")
            continue

        if plan_date < TODAY.date() and not is_completed and plan_stat != "잠시 중지":
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "실패"}}}
            )
            write_log("logs", f"계획 '{k}'이 실패 상태로 업데이트되었습니다.")
        elif plan_date < TODAY.date() and is_completed and plan_stat != "잠시 중지":
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "완료"}}}
            )
            write_log("logs", f"계획 '{k}'이 완료 상태로 업데이트되었습니다.")

    if TODAY.weekday() == 6:
        for k, v in all_view_db_result.items():
            plan_date = pd.to_datetime(v["시작일"], errors="coerce").date()
            is_completed = v.get("완료", False)

            if "(" in k and "회 남음" in k:
                write_log("logs", f"계획 '{k}'은 매주 n회 반복 계획으로 이곳에서 처리하지 않습니다.")
                continue

            if plan_date == TODAY.date() - pd.Timedelta(days=1) and v["계획 상태"] != "잠시 중지":
                new_stat = "완료" if is_completed else "실패"
                notion.pages.update(
                    page_id=v["id"],
                    properties={"계획 상태": {"status": {"name": new_stat}}}
                )
                write_log("logs", f"계획 '{k}'이 {new_stat} 상태로 업데이트되었습니다.")

    for k, v in total_view_db_result.items():
        if v["시작일"] == TODAY.date().isoformat():
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "진행 중"}}}
            )
            write_log("logs", f"계획 '{k}'이 진행 중 상태로 업데이트되었습니다.")
