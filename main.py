from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models.yolo_model import predict_symbols
from services.label_utils import process_symbols, normalize_clothing_type
from services.youtube_api import fetch_washing_info, fetch_youtube_videos
from services.wash_cycle import generate_search_keywords, get_recommended_wash_cycle
from services.price_data import laundry_prices
from services.material_warnings import MATERIAL_WARNINGS
from services.filter_utils import filter_detections
from services.label_descriptions import LABEL_EXPLANATIONS
from services.material_scores import MATERIAL_SCORES

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict/")
async def predict(
    file: UploadFile = File(...), 
    clothing_type: str = Form(...), 
    material: str = Form(...)
):
    # ✅ Step 1: 옷 종류 정규화
    normalized_type = normalize_clothing_type(clothing_type)
    # ✅ Step 2: YOLO 예측 결과 (label, confidence, box)
    raw_detections = await predict_symbols(file)

# ✅ Step 2-1: x 좌표 기준 정렬
    sorted_detections = sorted(raw_detections, key=lambda x: x[2][0])  # x1 기준 정렬

# ✅ Step 2-2: (label, confidence)만 추출
    detected_symbols = [(label, conf) for label, conf, _ in sorted_detections]

    # ✅ Step 2: YOLO 예측 결과 (label, confidence) 튜플 리스트
    

    # ✅ Step 3: YOLO 결과로부터 라벨 추출
    detected_labels = [label for label, _ in detected_symbols]

    # ✅ Step 6: 중복 제거 + 유사 기호 그룹 필터링
    final_symbols = filter_detections(detected_symbols)

    # ✅ Step 7: 검색 키워드, 유튜브, 세탁 정보 등 부가 정보 생성
    search_keywords = generate_search_keywords(normalized_type, material)
    washing_info = fetch_washing_info(search_keywords)
    youtube_videos = fetch_youtube_videos(search_keywords)
    recommended_days = get_recommended_wash_cycle(normalized_type)
    final_message = f"이 옷의 세탁 주기는 {recommended_days}일입니다. 세탁 알림 설정해 드릴까요?"
    material_warnings = MATERIAL_WARNINGS.get(material, MATERIAL_WARNINGS.get("기타", []))

    # ✅ Step 8: 종합 정보 처리
    response = process_symbols(
        detected_symbols=final_symbols,
        material=material,
        search_keywords=search_keywords,
        washing_info=washing_info,
        youtube_videos=youtube_videos,
        clothing_type=normalized_type
    )
    response["detection_info"] = [
    {"label": label, "confidence": conf}
    for label, conf in final_symbols
    ]
    recognized_only = [label for label, conf in final_symbols if conf > 0.0]
    response["results"] = [
    {"description": LABEL_EXPLANATIONS.get(label, label)}
    for label, conf in final_symbols
    if conf > 0.0
    ]
    # ✅ Step 9: 최종 결과 응답에 추가 정보 포함
    response.update({
        "material_warnings": material_warnings,
        "recommended_cycle_days": recommended_days,
        "final_message": final_message,
        "clothing_type": normalized_type
    })

    return JSONResponse(content=response, headers={"Content-Type": "application/json; charset=utf-8"})


@app.get("/predict_price/")
def predict_price(item: str = Query(..., description="의류명 입력")):
    item_clean = item.strip().lower()

    for key in laundry_prices:
        if item_clean in key.lower():
            price = laundry_prices[key]
            return JSONResponse(
                content={
                    "item": key,
                    "estimated_price": f"{price}원",
                    "price_source": "크린토피아 기준"
                },
                headers={"Content-Type": "application/json; charset=utf-8"}
            )

    return {"error": "해당 의류의 가격 정보가 없습니다. 다른 품목을 시도해보세요."}
