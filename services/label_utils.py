from services.label_descriptions import LABEL_EXPLANATIONS
from services.material_scores import MATERIAL_SCORES
from services.price_data import laundry_prices
from difflib import get_close_matches

symbol_scores = {
    "DN_wash": 50, "DN_dry": 15, "DN_bleach": 10, "DN_tumble_dry": 20,
    "DN_iron": 5, "DN_steam": 5, "DN_wet_clean": 20, "DN_wring": 5,
    "DN_dry_clean": -10, "machine_wash_normal": -5, "machine_wash_delicate": -3, "hand_wash": -5,
    "30C": 3, "40C": 3, "50C": 5, "60C": 8, "70C": 10, "95C": 12,
    "iron_low": 2, "iron_medium": 5, "iron_high": 8,
    "bleach": 0, "chlorine_bleach": 2, "non_chlorine_bleach": 5,
    "dry_clean": 20, "tumble_dry_low": 0, "tumble_dry_normal": 2
}

difficulty_thresholds = [
    (30, "★☆☆☆☆", "가정 세탁 가능"),
    (60, "★★☆☆☆", "주의하면 세탁 가능"),
    (90, "★★★☆☆", "세심한 주의 필요"),
    (120, "★★★★☆", "가정 세탁 비권장"),
    (float('inf'), "★★★★★", "가정 세탁 불가")
]

def normalize_clothing_type(clothing_type: str) -> str:
    clothing_type = clothing_type.strip()
    candidates = list(laundry_prices.keys())
    match = get_close_matches(clothing_type, candidates, n=1, cutoff=0.6)
    return match[0] if match else clothing_type

def calculate_difficulty_score(symbols, material):
    try:
        base_score = sum(
            symbol_scores.get(label, 0)
            for label, confidence in symbols
            if confidence > 0.0  # 보완된 라벨 제외
        )
    except Exception as e:
        base_score = 0  # fallback

    return base_score



def get_difficulty_level(score):
    try:
        score = int(score)
    except (ValueError, TypeError):
        score = 0  # score가 None이거나 변환 실패 시 기본값 설정

    for threshold, stars, recommendation in difficulty_thresholds:
        if score <= threshold:
            return stars, recommendation
    return "★★★★★", "가정 세탁 불가"



def process_symbols(detected_symbols, material, search_keywords, washing_info, youtube_videos, clothing_type=None):
    score = calculate_difficulty_score(detected_symbols, material) or 0
    level, recommendation = get_difficulty_level(score)

    result = {
        "message": "다음 라벨들이 인식되었습니다!",
        "results": [{"description": LABEL_EXPLANATIONS.get(lbl, "설명 없음")} for lbl, _ in detected_symbols],
        "score": score,
        "level": level,
        "recommendation": recommendation,
        "recommended_search": search_keywords,
        "washing_info": washing_info,
        "youtube_videos": youtube_videos
    }

    if score >= 60 and clothing_type:
        normalized_type = normalize_clothing_type(clothing_type)
        price = laundry_prices.get(normalized_type)
        if price:
            result["estimated_prices"] = {normalized_type: f"{price}원"}
        else:
            result["estimated_prices"] = {normalized_type: "가격 정보 없음"}

    return result
