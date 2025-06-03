## .env예시
```
NOTION_TOKEN=api 토큰 (ntn_~~~~~~~~~~~~~~~~~~~~~~~~~~~~~)
NOTION_DB_ID=데이터 베이스 uuid 형태 (00000000-0000-0000-0000-000000000000)
```

## 🧠 Notion 자동 계획 생성기

Notion의 "계획 생성 DB"를 기반으로, 반복 유형에 따라 "계획 보기용 DB"에 자동으로 일정을 생성하고 상태를 관리하는 Python 자동화 스크립트입니다.

---

## 🔄 실행 흐름 요약

```
main.py
│
├── 환경 변수 로드 (.env)
│
├── Notion Client 초기화
│
├── Notion DB 쿼리
│   ├── 생성용 DB → create_pages
│   └── 보기용 DB → view_pages
│
├── 생성 DB 데이터 파싱
│   └── fetch_create_plan_data() → total_create_db_result
│
├── 보기 DB 데이터 파싱 및 주간 필터링
│   └── fetch_view_plan_data() → all_view_db_result, total_view_db_result
│
└── 계획 생성 및 상태 갱신
    └── generate_calendar_plans()
        ├── 반복 유형 분기 처리
        │   ├── handle_daily_repeat()
        │   ├── handle_weekly_repeat()
        │   ├── handle_specific_day_repeat()
        │   └── handle_no_repeat()
        └── update_old_plan_status()
```

---

## 📁 디렉토리 구조

```
.
├── main.py
├── .env
├── README.md
├── utils/
│   ├── constants.py
│   ├── env_loader.py
│   ├── extractor.py
│   └── __init__.py
├── handlers/
│   ├── create_plan_handler.py
│   ├── view_plan_handler.py
│   ├── plan_generator.py
│   ├── repeat_daily.py
│   ├── repeat_weekly.py
│   ├── repeat_specific_days.py
│   ├── repeat_none.py
│   ├── status_updater.py
│   └── __init__.py
```

---

## ✅ 요구사항

- Python 3.9+
- Notion API 토큰 및 DB ID 설정
- `.env` 파일 설정 필수

```bash
pip install -r requirements.txt
```

---

## ✨ 사용법

```bash
python main.py
```
