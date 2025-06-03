import pandas as pd
import os
from utils.constants import TODAY, week_end

# "특정 요일" 반복 유형 처리 함수
def handle_specific_day_repeat(notion, title, data, total_view_db_result):
    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

    for i in range((week_end - TODAY).days + 1):
        current_day = TODAY + pd.Timedelta(days=i)
        weekday_kor = weekday_names[current_day.weekday()]

        if weekday_kor in data["요일 선택"]:
            key = f"{title}::{current_day.date().isoformat()}"
            if key in total_view_db_result:
                continue

            plan_stat = "진행 중" if current_day.date() == TODAY.date() else "시작 전"

            notion.pages.create(
                parent={"database_id": os.environ["NOTION_VIEW_PLAN_PAGE_ID"]},
                properties={
                    "계획명": {"title": [{"text": {"content": title}}]},
                    "시작일": {"date": {"start": current_day.date().isoformat()}},
                    "수행 시간": {"number": data["수행 시간"]},
                    "완료": {"checkbox": False},
                    "계획 상태": {"status": {"name": plan_stat}}
                }
            )
