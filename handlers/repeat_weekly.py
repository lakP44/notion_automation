import pandas as pd
import os

from utils.constants import GetToday, GetWeekRange, GetTodayStr
from utils.logger import write_log  # 로그 작성을 위한 유틸리티 함수

# "매주 n회" 반복 유형 처리 함수
def handle_weekly_repeat(notion, title, data, week_view_db_result, all_view_db_result):
    '''
    "매주 n회" 반복 유형을 처리하는 함수
    
    Args:
        notion (Client): Notion API 클라이언트 인스턴스
        title (str): 계획 제목
        data (dict): 계획 데이터
        week_view_db_result (dict): 주간 필터링된 전체 계획 데이터
        all_view_db_result (dict): 전체 계획 데이터
        
    Returns:
        이 함수는 반환값이 없습니다. Notion에 계획을 생성하거나 업데이트합니다.
    '''
    TODAY = GetToday()  # 오늘 날짜 가져오기
    TODAY_STR = GetTodayStr()  # 오늘 날짜 문자열 가져오기
    week_start, week_end = GetWeekRange()  # 이번 주 시작일과 종료일 가져오기

    weekly_count = data["매주 몇 회"] # 매주 몇 회 반복되는지 가져오기
    # 해당 일자가 속한 주의 계획 페이지를 가져오기
    existing_weekly_pages = [
        (k, v) for k, v in week_view_db_result.items()
        if k.startswith(f"{title}") and
        "시작일" in v and
        week_start.date() <= v["시작일"].date() <= week_end.date()
    ]

    # 일요일에 시작일이 어제인 계획도 포함
    if TODAY.weekday() == 6:
        existing_weekly_pages += [
            (k, v) for k, v in all_view_db_result.items()
            if k.startswith(f"{title}") and
            "시작일" in v and
            (week_start.date() <= v["시작일"].date() <= week_end.date() or 
             v["시작일"].date() == week_start.date() - pd.Timedelta(days=1))
        ]

    # 계획 상태가 "잠시 중지"인 경우 건너뜀
    if any(v.get("계획 상태") == "잠시 중지" for _, v in existing_weekly_pages):
        write_log("logs", f"계획 '{title}'은 현재 '잠시 중지' 상태입니다. 이번주는 건너뜁니다.", False)
        return

    # 이번주에 완료된 계획 수를 계산
    completed = sum(1 for _, v in existing_weekly_pages if v.get("완료") is True)
    moved = False # 시작일이 이동되었는지 여부를 추적하는 변수

    for k, v in existing_weekly_pages:
        plan_date = v["시작일"].date()

        # 시작일이 어제이고 완료되지 않은 경우
        if plan_date == TODAY.date() - pd.Timedelta(days=1) and not v.get("완료", False):
            # 일요일이 아니고 종료되지 않은 계획인 경우
            if (TODAY.weekday() != 6) and (not data["종료됨"]):
                notion.pages.update(
                    page_id=v["id"],
                    properties={"시작일": {"date": {"start": TODAY_STR}}}
                )
                moved = True
                write_log("logs", f"일요일이 아닐 때에 완료되지 않은 계획 '{k}'의 시작일을 {TODAY.date()}로 이동했습니다.", False)
            # 오늘이 일요일이거나 이미 종료된 계획인 경우
            elif (TODAY.weekday() == 6) or data["종료됨"]:
                notion.pages.update(
                    page_id=v["id"],
                    properties={"계획 상태": {"status": {"name": "실패"}}}
                )
                write_log("logs", f"일요일에 완료되지 않은 계획 '{k}'이 실패 상태로 업데이트되었습니다.", False)
        elif plan_date == TODAY.date() - pd.Timedelta(days=1) and v.get("완료", True) and TODAY.weekday() == 6:
            status = "완료" if "(1회 남음)" in k else "실패"
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": status}}}
            )
            write_log("logs", f"일요일에 완료된 계획 '{k}'이 {status} 상태로 업데이트되었습니다.", False)
        elif plan_date == TODAY.date() - pd.Timedelta(days=1) and v.get("완료", True):
            notion.pages.update(
                page_id=v["id"],
                properties={"계획 상태": {"status": {"name": "완료"}}}
            )
            write_log("logs", f"일요일이 아닐 때에 완료된 계획 '{k}'이 완료 상태로 업데이트되었습니다.", False)

    current_count = completed + (1 if moved else 0)
    if current_count < weekly_count and not moved:
        remaining = weekly_count - completed
        if TODAY.weekday() == 6:
            remaining = weekly_count
        new_title = f"{title} ({remaining}회 남음)"
        key = f"{new_title}::{TODAY_STR}"
        # already_exists = any(k.startswith(title) for k in week_view_db_result if TODAY_STR in k)
        already_exists = key in week_view_db_result

        if not already_exists and not data["종료됨"]:
            notion.pages.create(
                parent={"database_id": os.environ["NOTION_VIEW_PLAN_PAGE_ID"]},
                properties={
                    "계획명": {"title": [{"text": {"content": new_title}}]},
                    "시작일": {"date": {"start": TODAY_STR}},
                    "계획 상태": {"status": {"name": "진행 중"}},
                    "완료": {"checkbox": False}
                }
            )
            write_log("logs", f"계획 '{new_title}'이 {TODAY.date()}에 생성되었습니다.", False)
