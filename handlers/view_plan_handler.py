import pandas as pd
import time

from utils.extractor import extract_value
from utils.constants import TODAY, week_start, week_end

# 전체 보기용 계획 데이터 및 주간 필터된 데이터 반환 함수
def fetch_view_plan_data(view_pages):
    all_view_db_result = {}
    total_view_db_result = {}

    # 보여지는 페이지에서 각 계획의 속성을 추출하고 가공
    for page in view_pages:
        props = page["properties"]
        title = extract_value(props["계획명"])
        start_day = extract_value(props["시작일"])

        # 시작일이 없으면 건너뜀
        if not start_day:
            continue

        plan_stat = extract_value(props["계획 상태"])["name"]
        repeat_type = extract_value(props.get("반복 유형", {}))
        unique_key = f"{title}::{start_day.date().isoformat()}"

        all_view_db_result[unique_key] = {
            "id": page["id"],
            "계획 상태": plan_stat,
            "반복 유형": repeat_type,
            "시작일": start_day,
            **{
                k: extract_value(v)
                for k, v in props.items()
                if k not in ("계획명", "계획 상태", "반복 유형")
            }
        }

        include_start = week_start - pd.Timedelta(days=1) if repeat_type == "매주 n회" else week_start
        if include_start.date() <= start_day.date() <= week_end.date():
            total_view_db_result[unique_key] = all_view_db_result[unique_key]

    time.sleep(0.5)  # API 호출 간의 지연을 추가하여 요청 속도 제한을 피함

    return all_view_db_result, total_view_db_result
