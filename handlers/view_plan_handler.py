import pandas as pd
import time

from utils.extractor import extract_value
from utils.constants import TODAY, week_start, week_end

# 전체 보기용 계획 데이터 및 주간 필터된 데이터 반환 함수
def fetch_view_plan_data(view_pages):
    all_view_db_result = {}
    total_view_db_result = {}

    for page in view_pages:
        props = page["properties"]
        title = extract_value(props["계획명"])
        start_day = extract_value(props["시작일"])

        if not start_day:
            continue

        plan_stat = extract_value(props["계획 상태"])["name"]
        repeat_type = extract_value(props.get("반복 유형", {}))
        start_time = pd.to_datetime(start_day, errors='coerce').normalize().tz_localize(None)
        unique_key = f"{title}::{start_time.date().isoformat()}"

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

        include_start = week_start - pd.Timedelta(days=1) if repeat_type == "매주 n회" else week_start
        if include_start.date() <= start_time.date() <= week_end.date():
            total_view_db_result[unique_key] = all_view_db_result[unique_key]

    time.sleep(0.5)  # API 호출 간의 지연을 추가하여 요청 속도 제한을 피함

    return all_view_db_result, total_view_db_result
