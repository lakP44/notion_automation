import os
import importlib
from datetime import datetime, timedelta
import pytz

# 환경변수로 오늘 날짜 설정
def set_today_env(test_date):
    os.environ["TODAY_FOR_TEST"] = test_date.strftime("%Y-%m-%d")

# 테스트 설정
KST = pytz.timezone("Asia/Seoul")
start_date = datetime(2025, 6, 8, tzinfo=KST)
end_date = datetime(2025, 6, 14, tzinfo=KST)

current_date = start_date

while current_date <= end_date:
    print(f"\n⏱️  {current_date.date()} 실행 중...")

    set_today_env(current_date)

    # constants.py 초기화
    import utils.constants
    importlib.reload(utils.constants)

    # main.py 실행 (main 내부가 함수로 구성되어 있다면 추천: import 후 함수 실행)
    import main
    importlib.reload(main)  # 매 회차마다 main.py를 새로 실행하도록 강제

    # 사용자 입력 대기
    input("▶ 다음 날짜로 진행하려면 Enter를 누르세요...")

    # 다음 날짜로
    current_date += timedelta(days=1)
