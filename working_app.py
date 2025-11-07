from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
import shutil
import os
import paddle

app = FastAPI()

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.post("/ocr/")
async def ocr_endpoint(file: UploadFile = File(...)):
    # Save the uploaded image with its original extension
    ext = file.filename.split('.')[-1]
    temp_path = f"temp_img.{ext}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run OCR
    result = ocr.ocr(temp_path)

    # Prepare results for JSON serialization (detect nested structure)
    serializable_result = []

    # Check result nesting ([ [ [box, (text, score)], ... ] ])
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
        lines = result[0]
    else:
        lines = result

    for line in lines:
        if isinstance(line, list) and len(line) == 2 and isinstance(line[1], tuple):
            box, (text, score) = line
            serializable_result.append({
                "box": [float(x) for x in box],
                "text": str(text),
                "confidence": float(score)
            })
        else:
            serializable_result.append(str(line))

    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Detect which device was used
    if paddle.is_compiled_with_cuda() and paddle.device.get_device().startswith('gpu'):
        device_used = paddle.device.get_device()
    else:
        device_used = "cpu"

    return {
        "device": device_used,
        "result": serializable_result
    }