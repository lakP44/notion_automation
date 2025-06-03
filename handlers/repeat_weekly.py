import pandas as pd
import os
from utils.constants import TODAY, week_start, week_end

# "매주 n회" 반복 유형 처리 함수
def handle_weekly_repeat(notion, title, data, total_view_db_result, all_view_db_result):
    weekly_count = data["매주 몇 회"]
    existing_weekly_pages = [
        (k, v) for k, v in total_view_db_result.items()
        if k.startswith(f"{title}") and
        "시작일" in v and
        week_start.date() <= pd.to_datetime(v["시작일"], errors="coerce").date() <= week_end.date()
    ]

    if TODAY.weekday() == 6:
        existing_weekly_pages += [
            (k, v) for k, v in all_view_db_result.items()
            if k.startswith(f"{title}") and
            "시작일" in v and
            (week_start.date() <= pd.to_datetime(v["시작일"], errors="coerce").date() <= week_end.date() or 
             pd.to_datetime(v["시작일"], errors="coerce").date() == week_start.date() - pd.Timedelta(days=1))
        ]

    if any(v.get("계획 상태") == "잠시 중지" for _, v in existing_weekly_pages):
        return

    completed = sum(1 for _, v in existing_weekly_pages if v.get("완료") is True)
    moved = False

    for k, v in existing_weekly_pages:
        if moved:
            break

        plan_date = pd.to_datetime(v["시작일"], errors="coerce").date()
        if plan_date == TODAY.date() - pd.Timedelta(days=1) and not v.get("완료", False) and TODAY.weekday() != 6:
            notion.pages.update(
                page_id=v["id"],
                properties={"시작일": {"date": {"start": TODAY.date().isoformat()}}}
            )
            moved = True
        elif plan_date == TODAY.date() - pd.Timedelta(days=1) and not v.get("완료", False) and TODAY.weekday() == 6:
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "실패"}}}
            )
        elif plan_date == TODAY.date() - pd.Timedelta(days=1) and v.get("완료", True) and TODAY.weekday() == 6:
            status = "완료" if "(1회 남음)" in k else "실패"
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": status}}}
            )
        elif plan_date == TODAY.date() - pd.Timedelta(days=1) and v.get("완료", True):
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "완료"}}}
            )

    current_count = completed + (1 if moved else 0)
    if current_count < weekly_count and not moved:
        remaining = weekly_count - completed
        if TODAY.weekday() == 6:
            remaining = weekly_count
        new_title = f"{title} ({remaining}회 남음)"
        key = f"{new_title}::{TODAY.date().isoformat()}"
        already_exists = any(k.startswith(title) for k in total_view_db_result if TODAY.date().isoformat() in k)

        if not already_exists:
            notion.pages.create(
                parent={"database_id": os.environ["NOTION_VIEW_PLAN_PAGE_ID"]},
                properties={
                    "계획명": {"title": [{"text": {"content": new_title}}]},
                    "시작일": {"date": {"start": TODAY.date().isoformat()}},
                    "계획 상태": {"status": {"name": "진행 중"}},
                    "완료": {"checkbox": False}
                }
            )
