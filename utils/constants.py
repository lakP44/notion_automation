import os
import pandas as pd
import pytz

KST = pytz.timezone("Asia/Seoul")

def GetToday():
    '''
    현재 날짜를 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    testDate = os.environ.get("TODAY_FOR_TEST")
    if testDate:
        return pd.to_datetime(testDate).tz_localize(KST).normalize()
    return pd.Timestamp.now(tz=KST).normalize()


def GetYesterday():
    '''
    어제제 날짜를 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetToday() - pd.Timedelta(days=1)


def GetTodayStr():
    '''
    현재 날짜를 KST로 가져오고, 시간은 00:00:00으로 설정하여 문자열로 반환합니다.
    '''
    return GetToday().date().isoformat()


def GetSunday():  # 주 시작 (일요일)
    '''
    현재 날짜를 기준으로 주의 시작일(일요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    today = GetToday()
    weekday = (today.weekday() + 1) % 7  # 월=0 ~ 일=6 → 일=0 되도록 보정
    return today - pd.Timedelta(days=weekday)


def GetMonday():
    '''
    현재 날짜를 기준으로 주의 두 번째 날(월요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetSunday() + pd.Timedelta(days=1)

def GetTuesday():
    '''
    현재 날짜를 기준으로 주의 세 번째 날(화요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetSunday() + pd.Timedelta(days=2)

def GetWednesday():
    '''
    현재 날짜를 기준으로 주의 네 번째 날(수요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetSunday() + pd.Timedelta(days=3)

def GetThursday():
    '''
    현재 날짜를 기준으로 주의 다섯 번째 날(목요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetSunday() + pd.Timedelta(days=4)

def GetFriday():
    '''
    현재 날짜를 기준으로 주의 여섯 번째 날(금요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetSunday() + pd.Timedelta(days=5)

def GetSaturday():  # 주 끝 (토요일)
    '''
    현재 날짜를 기준으로 주의 마지막 날(토요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetSunday() + pd.Timedelta(days=6)


def GetWeekRange():
    '''
    현재 날짜를 기준으로 주의 시작일(일요일)과 마지막 날(토요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    return GetSunday(), GetSaturday()


def GetLastWeekRange():
    '''
    현재 날짜를 기준으로 지난 주의 시작일(일요일)과 마지막 날(토요일)을 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    week_start, _ = GetWeekRange()
    last_week_start = week_start - pd.Timedelta(days=7)
    last_week_end = week_start - pd.Timedelta(days=1)
    return last_week_start, last_week_end


def GetWeekDays():
    '''
    현재 날짜를 기준으로 주의 모든 날짜(일요일 ~ 토요일)를 KST로 가져오고, 시간은 00:00:00으로 설정하여 반환합니다.
    '''
    sunday = GetSunday()
    return [sunday + pd.Timedelta(days=i) for i in range(7)]
