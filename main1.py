from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import shutil
import os
import uuid

# FastAPI 인스턴스 생성
app = FastAPI(
    title="YOLO 세탁 기호 인식 API",
    description="YOLO 모델로 세탁 라벨을 인식하고 결과 반환",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# YOLO 모델 로드 (경로는 환경에 맞게 수정)
model = YOLO(r"C:\Users\pkbos\servertest\best.pt")  # ✅ 실제 경로 확인 필요

# 이미지 저장 경로
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/predict/", summary="YOLO 모델로 라벨 인식 결과 반환")
async def predict(file: UploadFile = File(...)):
    # 임시 파일로 저장
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    image_path = os.path.join(UPLOAD_DIR, filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # YOLO 모델 추론
    results = model(image_path)

    detections = []
    for box in results[0].boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = box
        class_name = model.names[int(cls)]
        detections.append({
            "label": class_name,
            "confidence": f"{conf:.2f}"
        })

    return JSONResponse(content={"detections": detections})
