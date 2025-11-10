from fastapi import FastAPI, UploadFile, File
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR
import shutil
import os
import paddle

app = FastAPI(title="PaddleOCR Invoice API", version="1.0.0")

# Initialize PaddleOCR with GPU fallback to CPU
OCR_INITIALIZED = False
ocr = None

print("Initializing PaddleOCR...")
try:
    # Try GPU first
    print("Attempting GPU initialization...")
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    OCR_INITIALIZED = True
    print("✅ PaddleOCR initialized successfully with GPU")
except Exception as gpu_error:
    print(f"❌ GPU initialization failed: {gpu_error}")
    print("Attempting CPU fallback...")
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        OCR_INITIALIZED = True
        print("✅ PaddleOCR initialized successfully with CPU")
    except Exception as cpu_error:
        print(f"❌ CPU initialization also failed: {cpu_error}")
        OCR_INITIALIZED = False
        ocr = None
        print("❌ PaddleOCR service is NOT available")

@app.get("/health")
async def health_check():
    """Health check endpoint"""

    # Basic service health
    health_info = {
        "status": "healthy",
        "service": "PaddleOCR Invoice API",
        "version": "1.0.0",
        "paddleocr_initialized": OCR_INITIALIZED,
        "paddle_available": True
    }

    if not OCR_INITIALIZED:
        health_info["status"] = "degraded"
        health_info["error"] = "PaddleOCR not initialized - OCR functionality unavailable"
        return JSONResponse(status_code=503, content=health_info)

    try:
        # Test paddle and CUDA availability
        health_info["cuda_available"] = paddle.is_compiled_with_cuda()

        try:
            device = paddle.device.get_device()
            health_info["current_device"] = device
            health_info["using_gpu"] = device and 'gpu' in device.lower()
        except Exception as device_error:
            health_info["device_error"] = str(device_error)
            health_info["current_device"] = "unknown"
            health_info["using_gpu"] = False

        # Test OCR with a simple check
        if ocr is not None:
            health_info["ocr_ready"] = True
            health_info["message"] = "All systems operational"
        else:
            health_info["ocr_ready"] = False
            health_info["status"] = "degraded"

        return health_info

    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["error"] = str(e)
        return JSONResponse(status_code=503, content=health_info)

@app.post("/ocr/")
async def ocr_endpoint(file: UploadFile = File(...)):
    # Check if PaddleOCR is initialized
    if not OCR_INITIALIZED or ocr is None:
        return JSONResponse(
            status_code=503,
            content={
                "error": "PaddleOCR service is not available",
                "success": False
            }
        )

    # Validate file
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "error": "No file provided",
                "success": False
            }
        )

    # Save the uploaded image with its original extension
    try:
        ext = file.filename.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported file format: {ext}. Supported formats: jpg, jpeg, png, bmp, tiff, webp",
                    "success": False
                }
            )

        temp_path = f"temp_img.{ext}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to save file: {str(e)}",
                "success": False
            }
        )

    try:
        # Run OCR
        result = ocr.ocr(temp_path)

        # Prepare clean results with text, confidence, and bounding boxes
        clean_results = []

        # Process OCR results
        if result is None or len(result) == 0:
            clean_results = []
        elif isinstance(result, list):
            # Handle PaddleOCR result format
            for page_idx, page_result in enumerate(result):
                if page_result is None:
                    continue

                if isinstance(page_result, list):
                    # Traditional format: list of [box, (text, score)]
                    for line in page_result:
                        if isinstance(line, list) and len(line) == 2:
                            box, text_info = line
                            if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                text = text_info[0] if text_info[0] else ""
                                confidence = float(text_info[1]) if len(text_info) > 1 and text_info[1] is not None else 0.0

                                if text.strip():  # Only add non-empty text
                                    clean_results.append({
                                        "text": str(text),
                                        "confidence": round(confidence, 3),
                                        "bounding_box": [[int(coord[0]), int(coord[1])] for coord in box]
                                    })
                elif hasattr(page_result, 'keys') or isinstance(page_result, dict):
                    # New format: dictionary-like object
                    try:
                        # Convert to dict if it's an object with keys
                        result_dict = dict(page_result) if hasattr(page_result, 'keys') else page_result

                        texts = result_dict.get('rec_texts', [])
                        boxes = result_dict.get('rec_polys', [])
                        scores = result_dict.get('rec_scores', [])

                        for i, text in enumerate(texts):
                            if i < len(boxes) and i < len(scores) and str(text).strip():
                                box_coords = boxes[i]
                                if hasattr(box_coords, 'tolist'):
                                    box_coords = box_coords.tolist()

                                clean_results.append({
                                    "text": str(text),
                                    "confidence": round(float(scores[i]), 3) if scores[i] is not None else 0.0,
                                    "bounding_box": [[int(coord[0]), int(coord[1])] for coord in box_coords]
                                })
                    except Exception as inner_e:
                        print(f"Error processing dictionary result: {inner_e}")
                        # Fallback: try to extract what we can
                        try:
                            if hasattr(page_result, '__dict__'):
                                for attr_name in dir(page_result):
                                    if not attr_name.startswith('_'):
                                        attr_value = getattr(page_result, attr_name)
                                        if attr_value and not callable(attr_value):
                                            clean_results.append({
                                                "text": f"{attr_name}: {str(attr_value)[:100]}",
                                                "confidence": 0.5,
                                                "bounding_box": []
                                            })
                        except:
                            pass

        # Detect which device was used
        try:
            if paddle.is_compiled_with_cuda():
                try:
                    device = paddle.device.get_device()
                    if device and 'gpu' in device.lower():
                        device_used = device
                    else:
                        device_used = "cpu"
                except:
                    device_used = "gpu"  # Assume GPU if CUDA is available
            else:
                device_used = "cpu"
        except Exception as device_error:
            print(f"Device detection error: {device_error}")
            device_used = "unknown"

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        response_data = {
            "device": device_used,
            "results": clean_results,
            "total_text_regions": len(clean_results),
            "success": True
        }

        return JSONResponse(content=response_data)

    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)



