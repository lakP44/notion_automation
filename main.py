# 가상환경 생성 명령어 : python -m venv 가상환경이름
# 가상환경 선택방법 : activate 후 ctrl + shift + p -> Python: Select Interpreter -> 가상환경 선택
# requirements.txt 생성 명령어 : pip freeze > requirements.txt
# requirements.txt 설치 명령어 : pip install -r requirements.txt

from dotenv import load_dotenv
from notion_client import Client
import os

from utils.env_loader import load_env_variables
from utils.logger import write_log # 로그 작성을 위한 유틸리티 함수

from handlers.create_plan_handler import fetch_create_plan_data
from handlers.view_plan_handler import fetch_view_plan_data
from handlers.plan_generator import generate_calendar_plans

# .env 파일에서 환경변수 로드
load_dotenv()
load_env_variables()

# Notion API 클라이언트 초기화
notion = Client(auth=os.environ["NOTION_TOKEN"])

# Notion에서 페이지 정보 조회
create_pages = notion.databases.query(database_id=os.environ["NOTION_CREATE_PLAN_PAGE_ID"])["results"]
# write_log("logs", f"계획 생성표 추출 (생성하는 표): {create_pages}") # 페이지가 정상 추출됐는지 확인

view_pages = notion.databases.query(database_id=os.environ["NOTION_VIEW_PLAN_PAGE_ID"])["results"]
# write_log("logs", f"전체 계획표 추출 (생성되는 대상): {view_pages}") # 페이지가 정상 추출됐는지 확인

write_log("logs", f"-------------------- 가공 데이터 추출 시작 --------------------")

# 계획 생성표 데이터 추출
total_create_db_result = fetch_create_plan_data(notion, create_pages)
write_log("logs", f"가공된 계획 생성표 데이터 (종료일 설정 등등...): {total_create_db_result}")

# 전체 계획 및 주간 계획 데이터 추출
all_view_db_result, week_view_db_result = fetch_view_plan_data(view_pages)
write_log("logs", f"가공된 전체 계획표 데이터: {all_view_db_result}")
write_log("logs", f"가공된 주간 계획표 데이터: {week_view_db_result}")

write_log("logs", f"-------------------- 캘린더 계획 생성 및 업데이트 시작 --------------------")

# 캘린더 계획 생성 및 상태 업데이트 실행
generate_calendar_plans(notion, total_create_db_result, week_view_db_result, all_view_db_result)
write_log("logs", f"-------------------- 코드 전체 사이클 순회 완료 --------------------")