from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
import shutil
import os
import paddle
import json

app = FastAPI()

# Let PaddleOCR auto-select GPU if available, else CPU
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

    # Prepare clean results with just text, confidence, and bounding boxes
    clean_results = []

    try:
        # Handle the new PaddleX OCRResult object
        if isinstance(result, list) and len(result) > 0:
            ocr_result_obj = result[0]

            # Handle OCRResult object (dictionary-like)
            if hasattr(ocr_result_obj, 'keys'):
                # Get all available keys
                available_keys = list(ocr_result_obj.keys())
                print(f"Available keys in OCRResult: {available_keys}")

                # Extract data using dictionary-like access
                texts = ocr_result_obj.get('rec_texts', [])
                boxes = ocr_result_obj.get('rec_polys', [])
                scores = ocr_result_obj.get('rec_scores', [])

                print(f"Found {len(texts)} texts, {len(boxes)} boxes, {len(scores)} scores")

                # Combine the data
                for i, text in enumerate(texts):
                    if i < len(boxes) and i < len(scores):
                        # Convert numpy array to list of coordinates
                        box_coords = boxes[i].tolist() if hasattr(boxes[i], 'tolist') else boxes[i]

                        clean_results.append({
                            "text": text,
                            "confidence": round(float(scores[i]), 3),
                            "bounding_box": [[int(coord[0]), int(coord[1])] for coord in box_coords]
                        })

            # Handle traditional PaddleOCR format (list of [box, (text, score)])
            elif isinstance(ocr_result_obj, list):
                lines = ocr_result_obj
                for line in lines:
                    if isinstance(line, list) and len(line) == 2 and isinstance(line[1], tuple):
                        box, (text, score) = line
                        clean_results.append({
                            "text": str(text),
                            "confidence": round(float(score), 3),
                            "bounding_box": [[int(coord[0]), int(coord[1])] for coord in box]
                        })

    except Exception as e:
        # Fallback: try to extract any text we can find
        clean_results = [{"text": f"Error processing result: {str(e)}", "confidence": 0.0, "bounding_box": []}]

    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Detect which device was used
    try:
        if paddle.is_compiled_with_cuda() and paddle.device.get_device().startswith('gpu'):
            device_used = paddle.device.get_device()
        else:
            device_used = "cpu"
    except:
        device_used = "unknown"

    return {
        "device": device_used,
        "results": clean_results,
        "total_text_regions": len(clean_results)
    }



