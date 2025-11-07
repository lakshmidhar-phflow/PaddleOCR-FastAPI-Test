# Invoice OCR System Documentation

## Overview
This project implements an OCR (Optical Character Recognition) system using PaddleOCR running in a Docker container with a FastAPI REST interface. The system extracts text from invoice images along with confidence scores and bounding box coordinates.

## Architecture
- **Backend**: FastAPI web framework
- **OCR Engine**: PaddleOCR with GPU support
- **Container**: Docker with NVIDIA CUDA support
- **Output**: Clean JSON with text, confidence scores, and bounding boxes

## Prerequisites
- Docker installed
- NVIDIA Docker runtime (for GPU support)
- An image file for OCR processing

## File Structure
```
Invoice-OCR/
├── app.py                    # Main FastAPI application
├── Dockerfile               # Docker configuration for building images
├── Dockerfile.cpu           # CPU-only Docker configuration (alternative)
├── README.md               # This documentation file
├── images/                 # Sample images for testing
│   └── aug_035.jpg
└── simple_ocr.py           # Standalone OCR script (alternative)
```

## Setup and Installation

### 1. Using Existing Docker Container (Recommended)

The system uses a pre-built `paddleocr-api` Docker image. To run it:

```bash
# Start the existing container
docker start loving_rhodes

# Or create a new container from the image
docker run -d -p 8080:8080 --name ocr-container paddleocr-api
```

### 2. Building from Scratch (Alternative)

If you need to build from source:

```bash
# Build the Docker image
docker build -t ocr-app .

# Run the container
docker run -d -p 8080:8080 --name ocr-container ocr-app
```

## API Usage

### Endpoint
- **URL**: `http://localhost:8080/ocr/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

### Request
```bash
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/image.jpg;type=image/jpeg'
```

### Response Format
```json
{
    "device": "gpu:0",
    "results": [
        {
            "text": "XPO",
            "confidence": 0.995,
            "bounding_box": [
                [329, 124],
                [515, 128],
                [513, 200],
                [327, 197]
            ]
        },
        {
            "text": "Page 1 of1",
            "confidence": 0.866,
            "bounding_box": [
                [1129, 134],
                [1389, 134],
                [1389, 186],
                [1129, 186]
            ]
        }
    ],
    "total_text_regions": 94
}
```

### Response Fields
- **device**: Processing device used (gpu:0, cpu, etc.)
- **results**: Array of extracted text regions
  - **text**: Recognized text content
  - **confidence**: Confidence score (0.0 to 1.0)
  - **bounding_box**: Four corner coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
- **total_text_regions**: Total number of text regions detected

## Code Implementation

### FastAPI Application (app.py)

The main application handles:
- File upload and temporary storage
- OCR processing using PaddleOCR
- Result parsing and formatting
- Cleanup of temporary files

#### Key Components:

1. **OCR Initialization**:
```python
ocr = PaddleOCR(use_angle_cls=True, lang='en')
```

2. **File Processing**:
```python
# Save uploaded image temporarily
ext = file.filename.split('.')[-1]
temp_path = f"temp_img.{ext}"
with open(temp_path, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)
```

3. **OCR Processing**:
```python
result = ocr.ocr(temp_path)
```

4. **Result Parsing**:
The system handles both traditional PaddleOCR format and new PaddleX OCRResult objects:

```python
if hasattr(ocr_result_obj, 'keys'):
    # Extract data from PaddleX OCRResult object
    texts = ocr_result_obj.get('rec_texts', [])
    boxes = ocr_result_obj.get('rec_polys', [])
    scores = ocr_result_obj.get('rec_scores', [])
```

## Troubleshooting

### Common Issues and Solutions

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   docker ps

   # Stop existing container
   docker stop ocr-container

   # Use a different port
   docker run -d -p 8081:8080 --name ocr-container ocr-app
   ```

2. **CUDA/GPU Issues**
   ```bash
   # Check GPU availability
   nvidia-smi

   # Use CPU-only mode if GPU unavailable
   docker run -d -p 8080:8080 -e CUDA_VISIBLE_DEVICES="" ocr-app
   ```

3. **Container Fails to Start**
   ```bash
   # Check container logs
   docker logs ocr-container

   # Common error: libcuda.so.1 missing
   # Solution: Use CPU-only mode or install NVIDIA Container Toolkit
   ```

4. **OCR Returns Empty Results**
   ```bash
   # Check if image is being processed
   docker logs ocr-container --tail 20

   # Verify image format and quality
   # Supported formats: JPG, PNG, BMP
   ```

### Debug Mode

To enable debug output, modify the app.py file to include print statements or check container logs:

```bash
# Real-time log monitoring
docker logs -f ocr-container
```

## Performance Considerations

- **GPU Processing**: Significantly faster than CPU for large batches
- **Image Size**: Large images are automatically resized (max_side_limit: 4000px)
- **Memory Usage**: PaddleOCR models require ~2GB RAM
- **Concurrent Requests**: FastAPI handles multiple simultaneous requests

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## Model Information

- **Text Detection**: PP-OCRv5_server_det
- **Text Recognition**: en_PP-OCRv5_mobile_rec (English)
- **Document Orientation**: PP-LCNet_x1_0_doc_ori
- **Document Unwarping**: UVDoc
- **Textline Orientation**: PP-LCNet_x1_0_textline_ori

## API Testing

### Using curl
```bash
# Test with sample image
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@images/aug_035.jpg;type=image/jpeg'
```

### Using Python requests
```python
import requests

url = 'http://localhost:8080/ocr/'
with open('path/to/image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)
    print(response.json())
```

## Deployment Notes

### Production Considerations
1. **Security**: Add authentication/authorization
2. **Rate Limiting**: Implement request throttling
3. **Logging**: Configure structured logging
4. **Monitoring**: Add health checks and metrics
5. **Scaling**: Use container orchestration (Kubernetes/Docker Swarm)

### Environment Variables
- `CUDA_VISIBLE_DEVICES`: Control GPU visibility
- `PADDLEOCR_NO_VISUALIZE`: Disable visualization (set to 1)

## Maintenance

### Model Updates
```bash
# Pull latest PaddleOCR updates
pip install --upgrade paddleocr

# Rebuild Docker image
docker build -t ocr-app .
```

### Log Rotation
Configure log rotation to prevent disk space issues:
```bash
# Configure Docker logging driver
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 ocr-app
```

## Contributing

When modifying the code:
1. Test with various image formats
2. Verify JSON output format
3. Check memory usage
4. Update documentation

## License

This project uses PaddleOCR which is licensed under Apache 2.0.

---

**Last Updated**: 2025-01-07
**Version**: 1.0
**Compatible PaddleOCR Version**: 2.x with PaddleX integration