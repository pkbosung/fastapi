from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models.yolo_model import predict_symbols
from services.label_utils import process_symbols
from services.youtube_api import fetch_washing_info, fetch_youtube_videos
from services.wash_cycle import generate_search_keywords, get_recommended_wash_cycle
from services.price_data import laundry_prices  # 크린토피아 가격표

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 세탁 라벨 인식 및 추천 정보 API
@app.post("/predict/")
async def predict(
    file: UploadFile = File(...), 
    clothing_type: str = Form(...), 
    material: str = Form(...)
):
    detected_symbols = await predict_symbols(file)
    search_keywords = generate_search_keywords(clothing_type, material)
    washing_info = fetch_washing_info(search_keywords)
    youtube_videos = fetch_youtube_videos(search_keywords)
    recommended_days = get_recommended_wash_cycle(clothing_type)
    final_message = f"이 옷의 세탁 주기는 {recommended_days}일입니다. 세탁 알림 설정해 드릴까요?"

    response = process_symbols(
        detected_symbols, search_keywords, washing_info, youtube_videos
    )
    response.update({
        "recommended_cycle_days": recommended_days,
        "final_message": final_message,
        "clothing_type": clothing_type  # 의류 종류도 포함
    })

    return JSONResponse(content=response)

# ✅ 크린토피아 가격 조회 API
@app.get("/predict_price/")
def predict_price(item: str = Query(..., description="의류명 입력")):
    item_clean = item.strip().lower()

    # 부분 일치 검색
    for key in laundry_prices:
        if item_clean in key.lower():
            price = laundry_prices[key]
            return {
                "item": key,  # 실제 등록된 키 값 반환
                "estimated_price": f"{price}원",
                "price_source": "크린토피아 기준"
            }

    return {
        "error": "해당 의류의 가격 정보가 없습니다. 다른 품목을 시도해보세요."
    }

