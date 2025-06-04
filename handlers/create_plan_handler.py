import pandas as pd
import time

from utils.extractor import extract_value
from utils.constants import TODAY, KST

# 생성 계획 데이터를 구조화하여 반환하는 함수
def fetch_create_plan_data(notion, create_pages):
    '''
    생성 계획 데이터를 구조화하여 반환하는 함수
    
    Args:
        notion (Client): Notion API 클라이언트 인스턴스
        create_pages (list): 생성 계획 페이지 목록
        
    Returns:
        dict: 계획 이름을 키로 하고, 각 계획의 속성을 값으로 하는 딕셔너리
    '''
    total_create_db_result = {}

    for page in create_pages:
        props = page["properties"]
        title = extract_value(props["계획명"])
        start_time = extract_value(props["시작일"])
        repeat_prop = extract_value(props["반복 유형"])
        end_time = extract_value(props["종료일"])

        if not start_time:
            continue

        # 기본 속성 추출
        parsed_props = {}
        for k, v in props.items():
            if k in ("계획명", "요일 선택 formula", "매주 몇 회 formula"):
                continue
            parsed_props[k] = extract_value(v)

        # 종료일 없을 경우 설정
        if ("종료일" not in props) or (not end_time):
            if repeat_prop == "없음":
                notion.pages.update(
                    page_id=page["id"],
                    properties={"종료일": {"date": {"start": start_time}}}
                )
                parsed_props["종료일"] = start_time
            else:
                parsed_props["종료일"] = "2200-12-31"
                
        # 시간대를 KST로 변환
        parsed_end = pd.to_datetime(parsed_props["종료일"], errors="coerce").normalize()
        
        if parsed_end.tzinfo is None:
            parsed_end = parsed_end.tz_localize(KST)
        else:
            parsed_end = parsed_end.tz_convert(KST)
                
        # 종료일이 오늘보다 이전이면 종료 상태로 변경
        if parsed_end.date() < TODAY.date():
            notion.pages.update(
                page_id=page["id"],
                properties={"종료됨": {"checkbox": True}}
            )
            parsed_props["종료됨"] = True  # ← 추가됨
        else:
            parsed_props["종료됨"] = False  # ← 추가됨: 종료 안 된 경우도 명시적으로 처리

        total_create_db_result[title] = {
            "id": page["id"],
            **parsed_props
        }
        
        time.sleep(0.5)  # API 호출 간의 지연을 추가하여 요청 속도 제한을 피함

    return total_create_db_result
