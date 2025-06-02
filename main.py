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
TODAY = pd.to_datetime("2025-06-21").normalize() # 오늘날짜 변경 테스트
# 일요일=0 ~ 토요일=6 기준으로 변환
sunday_start_weekday = (TODAY.weekday() + 1) % 7

# 이번 주 토요일까지의 offset 계산
delta = (6 - sunday_start_weekday)  # 토요일=6
SATURDAY = TODAY + pd.Timedelta(days=delta)

def extract_value(prop):
    if (not prop):
        return None
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
# 이번 주 범위 계산 (일요일 ~ 토요일)
# 일요일이 0, 월요일이 1, ..., 토요일이 6 이 되도록 조정
week_day = (TODAY.weekday() + 1) % 7  # ← 일요일이면 0, 월요일이면 1, ..., 토요일이면 6

week_start = TODAY - pd.Timedelta(days=week_day)
week_end = week_start + pd.Timedelta(days=6)

# 전체 페이지 저장용 (날짜 제한 없음)
all_view_db_result = {}

# 주간 필터링된 페이지 저장용
total_view_db_result = {}

for page in view_pages:
    props = page["properties"]
    title = extract_value(props["계획명"])
    start_day = extract_value(props["시작일"])

    if not start_day:
        continue

    plan_stat = extract_value(props["계획 상태"])["name"]
    repeat_type = extract_value(props.get("반복 유형", {}))  # ← 반복 유형 추출
    start_time = pd.to_datetime(start_day, errors='coerce').normalize().tz_localize(None)

    unique_key = f"{title}::{start_time.date().isoformat()}"

    # 1. 전체 저장용 → 조건 없이 전부 넣음
    all_view_db_result[unique_key] = {
        "id": page["id"],
        "계획 상태": plan_stat,
        "반복 유형": repeat_type,
        "시작일": start_time,
        **{
            k: extract_value(v)
            for k, v in props.items()
            if k not in ("계획명", "계획 상태", "반복 유형")
        }
    }

    # 2. 주간 필터링용 → 범위 내에 있는 경우만
    include_start = week_start - pd.Timedelta(days=1) if repeat_type == "매주 n회" else week_start
    if include_start.date() <= start_time.date() <= week_end.date():
        total_view_db_result[unique_key] = all_view_db_result[unique_key]

for k, v in total_view_db_result.items():
    # 시작일이 오늘 날짜인 경우
    if ((v["시작일"]) == TODAY.date().isoformat()):
        # 오늘 날짜에 해당하는 모든 계획의 상태를 "진행 중"으로 변경
        notion.pages.update(
            page_id=v["id"],
            properties={
                "계획 상태": {"status": {"name": "진행 중"}}
            }
        )

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
        # 이번 주 토요일까지 범위 계산
        # week_start = TODAY - pd.Timedelta(days=TODAY.weekday() + 1)  # 이번 주 일요일
        # week_end = week_start + pd.Timedelta(days=6)                 # 이번 주 토요일

        for i in range((week_end - TODAY).days + 1):  # 오늘 ~ 토요일까지 반복
            current_day = TODAY + pd.Timedelta(days=i)
            day_title = title
            key = f"{day_title}::{current_day.date().isoformat()}"

            # 해당 날짜에 이미 같은 제목이 있는 경우 생략
            if key in total_view_db_result:
                continue

            # 페이지 생성
            notion.pages.create(
                parent={"database_id": NOTION_VIEW_PLAN_PAGE_ID},
                properties={
                    "계획명": {"title": [{"text": {"content": day_title}}]},
                    "시작일": {"date": {"start": current_day.date().isoformat()}},
                    "수행 시간": {"number": data["수행 시간"]},
                    "완료": {"checkbox": False}
                }
            )

    elif repeat == "매주 n회":
        weekly_count = data["매주 몇 회"]  # 정확한 속성명 사용
        # this_week_start = TODAY - pd.Timedelta(days=TODAY.weekday() + 1)  # 이번 주 일요일
        # this_week_end = this_week_start + pd.Timedelta(days=6)            # 이번 주 토요일

        # 이번 주 생성된 관련 페이지들 필터링
        existing_weekly_pages = [
            (k, v) for k, v in total_view_db_result.items()
            if k.startswith(f"{title}") and  # ← 수정됨: 키 형식 반영
            "시작일" in v and
            week_start.date() <= pd.to_datetime(v["시작일"], errors="coerce").date() <= week_end.date()
        ]
        
        if TODAY.weekday() == 6:
                # 일요일인 경우, 바로 전날인 토요일의 계획도 포함
                existing_weekly_pages += [
                    (k, v) for k, v in all_view_db_result.items()
                    if k.startswith(f"{title}") and  # ← 수정됨: 키 형식 반영
                    "시작일" in v and
                    (week_start.date() <= pd.to_datetime(v["시작일"], errors="coerce").date() <= week_end.date() or
                    pd.to_datetime(v["시작일"], errors="coerce").date() == week_start.date() - pd.Timedelta(days=1))
                ]

        # 이번 주에 잠시 중지 상태가 있다면 아무 작업도 하지 않음
        if any(v.get("계획 상태") == "잠시 중지" for _, v in existing_weekly_pages):
            continue

        # 완료된 횟수 체크박스로 계산
        completed = sum(1 for _, v in existing_weekly_pages if v.get("완료") is True)

        moved = False  # 계획이 이동됐는지 체크하는 플래그
        if repeat == "매주 n회":
            # 어제 계획 중 완료되지 않은 것 → 오늘로 이동 (단, 하루에 하나만)
            for k, v in existing_weekly_pages:
                if moved:
                    break

                plan_date = pd.to_datetime(v["시작일"], errors="coerce").date()
                # 완료 체크박스가 없거나 False인 경우에만 이동
                if plan_date == TODAY.date() - pd.Timedelta(days=1) and not v.get("완료", False) and TODAY.weekday() != 6:
                    # 기존 계획 아카이브
                    # notion.pages.update(
                    #     page_id=v["id"],
                    #     archived=True
                    # )

                    # 오늘로 이동
                    original_title = k.split("::")[0]  # ← 수정됨: title 추출
                    notion.pages.update(
                        # parent={"database_id": NOTION_VIEW_PLAN_PAGE_ID},
                        page_id=v["id"],
                        properties={
                            # "계획명": {"title": [{"text": {"content": original_title}}]},
                            "시작일": {"date": {"start": TODAY.date().isoformat()}},
                            # "계획 상태": {"status": {"name": "진행 중"}},
                            # "완료": {"checkbox": False}
                        }
                    )
                    moved = True
                # 일요일인데 이전 계획이 완료되지 않은 경우 (그 전에 완료했다면 일요일에 일정이 안생겼을거임, 그니까 무조건 실패)
                elif plan_date == TODAY.date() - pd.Timedelta(days=1) and not v.get("완료", False) and TODAY.weekday() == 6:
                    # 기존 페이지의 상태만 "실패"로 변경
                    notion.pages.update(
                        page_id=v["id"],
                        properties={
                            "계획 상태": {"status": {"name": "실패"}}
                        }
                    )
                
                # 일요일인데 이전 계획이 완료된 경우 (이때는 토요일에 완료된 일정이 몇번째인지 따져봐야 함)
                elif plan_date == TODAY.date() - pd.Timedelta(days=1) and v.get("완료", True) and TODAY.weekday() == 6:
                    # 제목에 "(1회 남음)"이 포함되어 있었을 경우
                    if "(1회 남음)" in k:
                        # 기존 페이지의 상태만 "완료"로 변경
                        notion.pages.update(
                            page_id=v["id"],
                            properties={
                                "계획 상태": {"status": {"name": "완료"}}
                            }
                        )
                    else:
                        # 기존 페이지의 상태만 "실패"로 변경
                        notion.pages.update(
                            page_id=v["id"],
                            properties={
                                "계획 상태": {"status": {"name": "실패"}}
                            }
                        )
                # 이전 계획이 완료된 경우
                elif plan_date == TODAY.date() - pd.Timedelta(days=1) and v.get("완료", True):
                    # 기존 페이지의 상태만 "완료"로 변경
                    notion.pages.update(
                        page_id=v["id"],
                        properties={
                            "계획 상태": {"status": {"name": "완료"}}
                        }
                    )

        # 새 계획 생성이 필요한 경우
        current_count = completed + (1 if moved else 0)
        if current_count < weekly_count and not moved:
            remaining = weekly_count - completed
            if TODAY.weekday() == 6:
                remaining = weekly_count
            new_title = f"{title} ({remaining}회 남음)"
            key = f"{new_title}::{TODAY.date().isoformat()}"  # ← 수정됨: 중복 확인용 key 구성

            # 오늘 같은 제목 이미 있으면 생략
            if key not in total_view_db_result:
                notion.pages.create(
                    parent={"database_id": NOTION_VIEW_PLAN_PAGE_ID},
                    properties={
                        "계획명": {"title": [{"text": {"content": new_title}}]},
                        "시작일": {"date": {"start": TODAY.date().isoformat()}},
                        "계획 상태": {"status": {"name": "진행 중"}},
                        "완료": {"checkbox": False}
                    }
                )

    elif repeat == "특정 요일":
        weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

        # 이번 주 토요일 계산
        # week_start = TODAY - pd.Timedelta(days=TODAY.weekday() + 1)  # 이번 주 일요일
        # week_end = week_start + pd.Timedelta(days=6)                 # 이번 주 토요일

        for i in range((week_end - TODAY).days + 1):  # 오늘 ~ 토요일까지 반복
            current_day = TODAY + pd.Timedelta(days=i)
            weekday_kor = weekday_names[current_day.weekday()]  # 현재 요일 (한글)

            if weekday_kor in data["요일 선택"]:
                key = f"{title}::{current_day.date().isoformat()}"  # ← 수정됨

                # 중복 방지: 같은 제목+시작일 조합이 이미 있으면 스킵
                if key in total_view_db_result:
                    continue

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

# 이전 주 계획 상태 업데이트
for k, v in total_view_db_result.items():
    plan_date = pd.to_datetime(v["시작일"], errors="coerce").date()
    is_completed = v.get("완료", False)

    # 제목에 "(n회 남음)" 패턴이 포함되어 있으면 제외
    if "(" in k and "회 남음" in k:
        continue

    if plan_date < TODAY.date() and not is_completed:
        notion.pages.update(
            page_id=v["id"],
            properties={
                "계획 상태": {"status": {"name": "실패"}}
            }
        )
    elif plan_date < TODAY.date() and is_completed:
        notion.pages.update(
            page_id=v["id"],
            properties={
                "계획 상태": {"status": {"name": "완료"}}
            }
        )


k = 1