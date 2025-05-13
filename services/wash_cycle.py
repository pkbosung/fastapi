import difflib

# 세탁 주기 매핑 테이블 (단위: 일)
wash_cycles = {
    "셔츠": 7,
    "청바지": 14,
    "정장 재킷": 30,
    "운동복": 3,
    "니트": 14,
    "속옷": 1,
    "티셔츠": 7,
    "바지": 10,
    "코트": 60,
    "스웨터": 21
}

def get_recommended_wash_cycle(clothing_type: str) -> int:
    """
    사용자가 입력한 옷 종류와 가장 비슷한 항목을 찾아 세탁 주기를 반환합니다.
    일치하는 항목이 없으면 기본값 7일 반환.
    """
    possible_keys = list(wash_cycles.keys())
    match = difflib.get_close_matches(clothing_type, possible_keys, n=1, cutoff=0.4)
    return wash_cycles.get(match[0], 7) if match else 7  # 기본값: 7일
def generate_search_keywords(clothing_type: str, material: str) -> list:
    return [f"{material} {clothing_type} 세탁법"]
