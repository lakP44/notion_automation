import os
import pandas as pd
import pytz

KST = pytz.timezone("Asia/Seoul")

# 테스트 여부 판단
TODAY_FOR_TEST = os.environ.get("TODAY_FOR_TEST")
TEST = TODAY_FOR_TEST is not None

if TEST:
    TODAY = pd.to_datetime(TODAY_FOR_TEST).tz_localize(KST).normalize()
else:
    TODAY = pd.Timestamp.now(tz=KST).normalize()
    
TODAY_STR = TODAY.date().isoformat()

# 이번 주 일요일 계산
sunday_start_weekday = (TODAY.weekday() + 1) % 7

# 이번 주 토요일 계산
SATURDAY = TODAY + pd.Timedelta(days=(6 - sunday_start_weekday))

# 이번 주 시작 (일요일)과 끝 (토요일) 계산
week_day = (TODAY.weekday() + 1) % 7
week_start = TODAY - pd.Timedelta(days=week_day)
week_end = week_start + pd.Timedelta(days=6)
