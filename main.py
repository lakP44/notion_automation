# 가상환경 생성 명령어 : python -m venv 가상환경이름
# 가상환경 선택방법

from dotenv import load_dotenv
import os

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
