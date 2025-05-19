import os
from ultralytics import YOLO

model = YOLO(r'/Users/bosung/wash_friends_app/fastapi/best.pt')

async def predict_symbols(file):
    image_path = f"./static/uploads/{file.filename}"
    os.makedirs("./static/uploads", exist_ok=True)
    with open(image_path, "wb") as img_file:
        img_file.write(await file.read())

    results = model(image_path)
    detected_symbols = []
    for result in results:
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            continue
        for i in range(len(boxes.cls)):
            cls_idx = int(boxes.cls[i].cpu().numpy())
            confidence = float(boxes.conf[i].cpu().numpy()) * 100
            cls_name = model.names.get(cls_idx, "Unknown Class").strip()
            detected_symbols.append((cls_name, confidence))
    return detected_symbols
