import pandas as pd
from utils.constants import TODAY

# 이전 주 계획 상태 업데이트
def update_old_plan_status(notion, total_view_db_result, all_view_db_result):
    for k, v in total_view_db_result.items():
        plan_date = pd.to_datetime(v["시작일"], errors="coerce").date()
        plan_stat = v["계획 상태"]
        is_completed = v.get("완료", False)

        if "(" in k and "회 남음" in k:
            continue

        if plan_date < TODAY.date() and not is_completed and plan_stat != "잠시 중지":
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "실패"}}}
            )
        elif plan_date < TODAY.date() and is_completed and plan_stat != "잠시 중지":
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "완료"}}}
            )

    if TODAY.weekday() == 6:
        for k, v in all_view_db_result.items():
            plan_date = pd.to_datetime(v["시작일"], errors="coerce").date()
            is_completed = v.get("완료", False)

            if "(" in k and "회 남음" in k:
                continue

            if plan_date == TODAY.date() - pd.Timedelta(days=1) and v["계획 상태"] != "잠시 중지":
                new_stat = "완료" if is_completed else "실패"
                notion.pages.update(
                    page_id=v["id"],
                    properties={"계획 상태": {"status": {"name": new_stat}}}
                )

    for k, v in total_view_db_result.items():
        if v["시작일"] == TODAY.date().isoformat():
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "진행 중"}}}
            )
