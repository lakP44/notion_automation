# 가상환경 생성 명령어 : python -m venv 가상환경이름
# 가상환경 선택방법 : activate 후 ctrl + shift + p -> Python: Select Interpreter -> 가상환경 선택
# requirements.txt 생성 명령어 : pip freeze > requirements.txt

from dotenv import load_dotenv
from notion_client import Client
import os

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

NOTION_CREATE_PLAN_DB_ID = os.getenv("NOTION_CREATE_PLAN_DB_ID")
NOTION_CREATE_PLAN_PAGE_ID = os.getenv("NOTION_CREATE_PLAN_PAGE_ID")

notion = Client(auth=os.environ["NOTION_TOKEN"])

response = notion.databases.query(database_id=NOTION_CREATE_PLAN_PAGE_ID)

pages = response["results"]

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


# 결과 생성
total_db_result = {}

for page in pages:
    props = page["properties"]
    title = extract_value(props["계획명"])
    day_formula = extract_value(props["요일 선택 formula"])["number"]
    week_count_formula = extract_value(props["매주 몇 회 formula"])["number"]

    # 기본 속성 추출
    parsed_props = {}
    for k, v in props.items():
        if ((k == "계획명") | (k == "요일 선택 formula") | (k == "매주 몇 회 formula")):
            continue
        parsed_props[k] = extract_value(v)

    # 종료일이 없으면 기본값으로 설정
    if "종료일" not in props or not extract_value(props["종료일"]):
        parsed_props["종료일"] = "9999-12-31"

    total_db_result[title] = {
        "id": page["id"],
        "요일 선택 formula": day_formula,
        "매주 몇 회 formula": week_count_formula,
        **parsed_props
    }

k = 1