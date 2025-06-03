import pandas as pd
import os
from utils.constants import TODAY

# "없음" 반복 유형 처리 함수
def handle_no_repeat(notion, title, data, total_view_db_result):
    start_time = pd.to_datetime(data["시작일"], errors='coerce')

    # 시작일이 오늘보다 이전이면 생성하지 않음
    if start_time.date() < TODAY.date():
        return

    notion.pages.update(
        page_id=data["id"],
        properties={"종료일": {"date": {"start": start_time.date().isoformat()}}}
    )

    key = f"{title}::{data['시작일']}"
    if key in total_view_db_result:
        return

    plan_stat = "진행 중" if data["시작일"] == TODAY.date().isoformat() else "시작 전"

    notion.pages.create(
        parent={"database_id": os.environ["NOTION_VIEW_PLAN_PAGE_ID"]},
        properties={
            "계획명": {"title": [{"text": {"content": title}}]},
            "시작일": {"date": {"start": data["시작일"]}},
            "수행 시간": {"number": data["수행 시간"]},
            "완료": {"checkbox": False},
            "계획 상태": {"status": {"name": plan_stat}}
        }
    )
