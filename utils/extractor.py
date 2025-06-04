# Notion 속성 값 추출 함수
def extract_value(prop):
    '''
    Notion 속성 값을 추출하는 함수
    
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
        return prop[t]["start"] if prop[t] else None
    elif t == "number":
        return prop[t]
    elif t == "checkbox":
        return prop[t]
    else:
        return prop.get(t, None)
