import os
import pandas as pd
import pytz

KST = pytz.timezone("Asia/Seoul")

def GetToday():
    testDate = os.environ.get("TODAY_FOR_TEST")
    if testDate:
        return pd.to_datetime(testDate).tz_localize(KST).normalize()
    return pd.Timestamp.now(tz=KST).normalize()


def GetYesterday():
    return GetToday() - pd.Timedelta(days=1)


def GetTodayStr():
    return GetToday().date().isoformat()


def GetSunday():  # 주 시작 (일요일)
    today = GetToday()
    weekday = (today.weekday() + 1) % 7  # 월=0 ~ 일=6 → 일=0 되도록 보정
    return today - pd.Timedelta(days=weekday)


def GetMonday():
    return GetSunday() + pd.Timedelta(days=1)

def GetTuesday():
    return GetSunday() + pd.Timedelta(days=2)

def GetWednesday():
    return GetSunday() + pd.Timedelta(days=3)

def GetThursday():
    return GetSunday() + pd.Timedelta(days=4)

def GetFriday():
    return GetSunday() + pd.Timedelta(days=5)

def GetSaturday():  # 주 끝 (토요일)
    return GetSunday() + pd.Timedelta(days=6)


def GetWeekRange():
    return GetSunday(), GetSaturday()


def GetWeekDays():
    sunday = GetSunday()
    return [sunday + pd.Timedelta(days=i) for i in range(7)]
