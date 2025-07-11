import pandas as pd
import os

from utils.constants import GetToday, GetWeekRange
from utils.logger import write_log  # 로그 작성을 위한 유틸리티 함수

# "특정 요일" 반복 유형 처리 함수
def handle_specific_day_repeat(notion, title, data, week_view_db_result):
    '''
    "특정 요일" 반복 유형을 처리하는 함수
    
    Args:
        notion (Client): Notion API 클라이언트 인스턴스
        title (str): 계획 제목
        data (dict): 계획 데이터
        week_view_db_result (dict): 주간 계획 데이터
        
    Returns:
        이 함수는 반환값이 없습니다. Notion에 계획을 생성합니다.
    '''
    TODAY = GetToday()  # 오늘 날짜 가져오기
    week_start, week_end = GetWeekRange()  # 이번 주 시작일과 종료일 가져오기

    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    
    end_date = data["종료일"]

    for i in range((week_end - TODAY).days + 1):
        current_day = TODAY + pd.Timedelta(days=i)
        current_day_str = current_day.date().isoformat()
        
        if current_day > end_date:  # 종료일 이후는 생략
            continue
        
        weekday_kor = weekday_names[current_day.weekday()]

        if weekday_kor in data["요일 선택"]:
            key = f"{title}::{current_day_str}"
            if key in week_view_db_result:
                write_log("logs", f"계획 '{title}'은 이미 {current_day.date()}에 생성되어 있습니다. 건너뜁니다.", False)
                continue

            plan_stat = "진행 중" if current_day.date() == TODAY.date() else "시작 전"

            notion.pages.create(
                parent={"database_id": os.environ["NOTION_VIEW_PLAN_PAGE_ID"]},
                properties={
                    "계획명": {"title": [{"text": {"content": title}}]},
                    "시작일": {"date": {"start": current_day_str}},
                    "수행 시간": {"number": data["수행 시간"]},
                    "완료": {"checkbox": False},
                    "계획 상태": {"status": {"name": plan_stat}}
                }
            )
            write_log("logs", f"계획 '{title}'이 {current_day.date()}에 생성되었습니다.", False)
