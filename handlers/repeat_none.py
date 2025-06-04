import pandas as pd
import os

from utils.constants import TODAY
from utils.logger import write_log  # 로그 작성을 위한 유틸리티 함수

# "없음" 반복 유형 처리 함수
def handle_no_repeat(notion, title, data, week_view_db_result):
    '''
    "없음" 반복 유형을 처리하는 함수
    
    Args:
        notion (Client): Notion API 클라이언트 인스턴스
        title (str): 계획 제목
        data (dict): 계획 데이터
        week_view_db_result (dict): 주간 계획 데이터
        
    Returns:
        이 함수는 반환값이 없습니다. Notion에 계획을 생성하거나 업데이트합니다.
    '''
    start_time = pd.to_datetime(data["시작일"], errors='coerce')

    # 시작일이 오늘보다 이전이면 생성하지 않음
    if start_time.date() < TODAY.date():
        return

    notion.pages.update(
        page_id=data["id"],
        properties={"종료일": {"date": {"start": start_time.date().isoformat()}}}
    )

    key = f"{title}::{data['시작일']}"
    if key in week_view_db_result:
        write_log("logs", f"계획 '{title}'은 이미 {data['시작일']}에 생성되어 있습니다. 건너뜁니다.")
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
    write_log("logs", f"계획 '{title}'이 {data['시작일']}에 생성되었습니다.")
