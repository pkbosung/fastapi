from services.label_descriptions import LABEL_EXPLANATIONS

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

def calculate_difficulty_score(symbols):
    return sum(symbol_scores.get(lbl, 0) for lbl, _ in symbols)

def get_difficulty_level(score):
    for threshold, stars, recommendation in difficulty_thresholds:
        if score <= threshold:
            return stars, recommendation
    return "★★★★★", "가정 세탁 불가"

def process_symbols(detected_symbols, search_keywords, washing_info, youtube_videos):
    score = calculate_difficulty_score(detected_symbols)
    level, recommendation = get_difficulty_level(score)
    return {
        "message": "다음 라벨들이 인식되었습니다!",
        "results": [{"description": LABEL_EXPLANATIONS.get(lbl, "설명 없음")} for lbl, _ in detected_symbols],
        "score": score,
        "level": level,
        "recommendation": recommendation,
        "recommended_search": search_keywords,
        "washing_info": washing_info,
        "youtube_videos": youtube_videos
    }
