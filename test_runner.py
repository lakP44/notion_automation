import os
import importlib
from datetime import datetime, timedelta
import pytz

def set_today_env(test_date):
    os.environ["TODAY_FOR_TEST"] = test_date.strftime("%Y-%m-%d")

KST = pytz.timezone("Asia/Seoul")
start_date = datetime(2025, 6, 15, tzinfo=KST)
end_date = datetime(2025, 6, 15, tzinfo=KST)

current_date = start_date

while current_date <= end_date:
    print(f"\n⏱️  {current_date.date()} 실행 중...")

    set_today_env(current_date)

    import utils.constants
    importlib.reload(utils.constants)
    # utils.constants.ResetTodayCache()  # 캐시 리셋

    import main
    importlib.reload(main)
    main.Run()

    input("▶ 다음 날짜로 진행하려면 Enter를 누르세요...")

    current_date += timedelta(days=1)