import pandas as pd

from utils.constants import KST

# Notion 속성 값 추출 함수
def extract_value(prop):
    '''
    Notion 속성 값을 추출하는 함수
    date는 KST로 변환하여 반환합니다.
    
    Args:
        prop: Notion 페이지의 속성 정보
        
    Returns:
        속성 값. 타입에 따라 문자열, 리스트, 또는 None을 반환
    '''
    if not prop:
        return None
    
    t = prop["type"]
    
    if t == "title":
        return "".join([x["plain_text"] for x in prop[t]])
    elif t == "select":
        return prop[t]["name"] if prop[t] else None
    elif t == "multi_select":
        return [v["name"] for v in prop[t]]
    elif t == "date":
        # return prop[t]["start"] if prop[t] else None
        date_str = prop[t]["start"] if prop[t] else None
        if not date_str:
            return None
        dt = pd.to_datetime(date_str, errors='coerce')
        if dt.tzinfo is None:
            dt = dt.tz_localize(KST)
        else:
            dt = dt.tz_convert(KST)
        return dt.normalize()
    elif t == "number":
        return prop[t]
    elif t == "checkbox":
        return prop[t]
    else:
        return prop.get(t, None)
