import pandas as pd

# 테스트용 오늘 날짜 설정
# TODAY_FOR_TEST = "2025-06-09"
# TODAY = pd.to_datetime(TODAY_FOR_TEST).normalize()

# 실제 오늘 날짜 사용
TODAY = pd.Timestamp.today().normalize()

# 이번 주 일요일 계산
sunday_start_weekday = (TODAY.weekday() + 1) % 7

# 이번 주 토요일 계산
SATURDAY = TODAY + pd.Timedelta(days=(6 - sunday_start_weekday))

# 이번 주 시작 (일요일)과 끝 (토요일) 계산
week_day = (TODAY.weekday() + 1) % 7
week_start = TODAY - pd.Timedelta(days=week_day)
week_end = week_start + pd.Timedelta(days=6)
