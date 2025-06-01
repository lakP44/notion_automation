# 가상환경 생성 명령어 : python -m venv 가상환경이름
# 가상환경 선택방법 : activate 후 ctrl + shift + p -> Python: Select Interpreter -> 가상환경 선택
# requirements.txt 생성 명령어 : pip freeze > requirements.txt
# requirements.txt 설치 명령어 : pip install -r requirements.txt

from dotenv import load_dotenv
from notion_client import Client
import os
import pandas as pd

### .env 파일에서 환경변수 로드
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

NOTION_CREATE_PLAN_DB_ID = os.getenv("NOTION_CREATE_PLAN_DB_ID")
NOTION_CREATE_PLAN_PAGE_ID = os.getenv("NOTION_CREATE_PLAN_PAGE_ID")

NOTION_VIEW_PLAN_DB_ID = os.getenv("NOTION_VIEW_PLAN_DB_ID")
NOTION_VIEW_PLAN_PAGE_ID = os.getenv("NOTION_VIEW_PLAN_PAGE_ID")

################################################################################

# Notion API 클라이언트 초기화<
notion = Client(auth=os.environ["NOTION_TOKEN"])

create_response = notion.databases.query(database_id=NOTION_CREATE_PLAN_PAGE_ID)
view_response = notion.databases.query(database_id=NOTION_VIEW_PLAN_PAGE_ID)

create_pages = create_response["results"]
view_pages = view_response["results"]

# 오늘 날짜와 이번 주 일요일 계산
# TODAY = pd.Timestamp.today().normalize()
TODAY = pd.to_datetime("2025-06-10").normalize()# 오늘날짜 변경 테스트
# 일요일=0 ~ 토요일=6 기준으로 변환
sunday_start_weekday = (TODAY.weekday() + 1) % 7

# 이번 주 토요일까지의 offset 계산
delta = (6 - sunday_start_weekday)  # 토요일=6
SATURDAY = TODAY + pd.Timedelta(days=delta)

def extract_value(prop):
    t = prop["type"]
    if t == "title":
        return "".join([x["plain_text"] for x in prop[t]])
    elif t == "select":
        return prop[t]["name"] if prop[t] else None
    elif t == "multi_select":
        return [v["name"] for v in prop[t]]
    elif t == "date":
        return prop[t]["start"] if prop[t] else None
    elif t == "number":
        return prop[t]
    elif t == "checkbox":
        return prop[t]
    else:
        return prop.get(t, None)

############################################################################################################################################
# 결과 생성
total_create_db_result = {}

# 계획 생성표에서 각 페이지를 순회하며 속성 추출
for page in create_pages:
    props = page["properties"]
    title = extract_value(props["계획명"])
    # day_formula = extract_value(props["요일 선택 formula"])["number"]
    # week_count_formula = extract_value(props["매주 몇 회 formula"])["number"]
    start_time = extract_value(props["시작일"])
    repeat_prop = extract_value(props["반복 유형"])
    end_time = extract_value(props["종료일"])
    
    if (not start_time):
        continue

    # 기본 속성 추출
    parsed_props = {}
    for k, v in props.items():
        if ((k == "계획명") | (k == "요일 선택 formula") | (k == "매주 몇 회 formula")):
            continue
        parsed_props[k] = extract_value(v)

    # 종료일이 없으면 종료되지 않도록 설정
    if ("종료일" not in props) or (not extract_value(props["종료일"])):
        if repeat_prop == "없음":
            # 종료일을 체크 상태로 변경하기
            notion.pages.update(
                page_id=page["id"],
                properties={"종료일": {"date": {"start": start_time}}}
            )
            parsed_props["종료일"] = start_time
        else:
            parsed_props["종료일"] = "2200-12-31"
        

    total_create_db_result[title] = {
        "id": page["id"],
        # "요일 선택 formula": day_formula,
        # "매주 몇 회 formula": week_count_formula,
        **parsed_props
    }
    
############################################################################################################################################   
# 전체 계획에서 각 페이지를 순회하며 속성 추출
total_view_db_result = {}

for page in view_pages:
    props = page["properties"]
    title = extract_value(props["계획명"])
    start_day = extract_value(props["시작일"])

    if not start_day:
        continue

    plan_stat = extract_value(props["계획 상태"])["name"]
    start_time = pd.to_datetime(start_day, errors='coerce')

    # 시작일 날짜만 추출 + tz 제거
    start_time = start_time.normalize().tz_localize(None)

    # 오늘 ~ 일요일 범위 안에 포함되지 않으면 스킵
    if not (TODAY <= start_time <= SATURDAY):
        continue

    # 기본 속성 추출
    parsed_props = {}
    for k, v in props.items():
        if k in ("계획명", "계획 상태"):
            continue
        parsed_props[k] = extract_value(v)

    total_view_db_result[title] = {
        "id": page["id"],
        "계획 상태": plan_stat,
        **parsed_props
    }

############################################################################################################################################
# Notion에서 생성된 계획을 기반으로 캘린더 데이터 생성
for title, data in total_create_db_result.items():
    end_time = pd.to_datetime(data["종료일"], errors='coerce')
    start_time = pd.to_datetime(data["시작일"], errors='coerce')
    repeat = data["반복 유형"]
    
    end_time = end_time.normalize().tz_localize(None)
    start_time = start_time.normalize().tz_localize(None)
    
    if (end_time < TODAY):
        # 종료일을 체크 상태로 변경하기
        notion.pages.update(page_id=data["id"], properties={"종료됨": {"checkbox": True}})
        continue
    
    # 종료일이 오늘날짜보다 과거인 경우 건너뛰기
    if ((data["종료됨"]) or (start_time > TODAY)):
        continue
    
    if repeat == "매일":
        for i in range(7):
            current_day = TODAY + pd.Timedelta(days=i)
            day_title = title  # 제목이 날짜별로 고정이면 그대로 사용

            # 페이지가 이미 존재하는 경우 스킵
            if day_title in total_view_db_result and \
            pd.to_datetime(total_view_db_result[day_title]["시작일"]).date() == current_day.date():
                continue

            notion.pages.create(
                parent={"database_id": NOTION_VIEW_PLAN_PAGE_ID},
                properties={
                    "계획명": {"title": [{"text": {"content": day_title}}]},
                    "시작일": {"date": {"start": current_day.date().isoformat()}},
                    "수행 시간": {"number": data["수행 시간"]},
                    "완료": {"checkbox": False}
                }
            )
    elif (repeat == "매주 n회"):
        pass
    elif repeat == "특정 요일":
        weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

        for i in range(7):
            current_day = TODAY + pd.Timedelta(days=i)
            weekday_kor = weekday_names[current_day.weekday()]  # 현재 요일 한글

            if weekday_kor in data["요일 선택"]:
                # 중복 방지: 같은 제목의 페이지가 이미 current_day에 있으면 건너뜀
                if title in total_view_db_result:
                    existing_start = pd.to_datetime(total_view_db_result[title]["시작일"], errors="coerce")
                    if existing_start is not pd.NaT and existing_start.date() == current_day.date():
                        continue  # 같은 날짜의 동일 제목 페이지가 이미 존재

                # 페이지 생성
                notion.pages.create(
                    parent={"database_id": NOTION_VIEW_PLAN_PAGE_ID},
                    properties={
                        "계획명": {"title": [{"text": {"content": title}}]},
                        "시작일": {"date": {"start": current_day.date().isoformat()}},
                        "수행 시간": {"number": data["수행 시간"]},
                        "완료": {"checkbox": False}
                    }
                )
    elif (repeat == "없음"):
        pass
    
k = 1