from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models.yolo_model import predict_symbols
from services.label_utils import process_symbols
from services.youtube_api import fetch_washing_info, fetch_youtube_videos
from services.wash_cycle import generate_search_keywords, get_recommended_wash_cycle

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict/")
async def predict(file: UploadFile = File(...), clothing_type: str = Form(...), material: str = Form(...)):
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
