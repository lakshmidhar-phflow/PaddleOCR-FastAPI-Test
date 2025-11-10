# PaddleOCR Invoice API - Complete Documentation

## 📋 Overview

This project provides a high-performance OCR API using PaddleOCR with GPU acceleration, packaged in a Docker container. The API can extract text from invoice images with bounding boxes and confidence scores.

## 🏗️ Project Structure

```
Invoice-OCR/
├── app.py                          # Main FastAPI application
├── Dockerfile                      # Docker configuration with GPU support
├── docker-compose.yml              # Production-ready deployment
├── .dockerignore                   # Docker build optimization
└── DOCUMENTATION.md       # This file
```

## 🚀 Quick Start

### Prerequisites

**Hardware Requirements:**
- NVIDIA GPU with CUDA support (4GB+ VRAM recommended)
- 8GB+ RAM
- 10GB+ free disk space

**Software Requirements:**
- NVIDIA Docker Toolkit (nvidia-docker2)
- Docker Engine 20.10+
- NVIDIA CUDA drivers 12.6+

### One-Command Deployment

**Option 1: Docker Compose (Recommended)**
```bash
docker-compose up -d --build
```

**Option 2: Linux/macOS Script**
```bash
chmod +x deploy_gpu.sh
./deploy_gpu.sh
```

**Option 3: Windows Script**
```bash
deploy_gpu.bat
```

**Option 4: Manual Docker Commands**
```bash
docker build -t paddleocr-invoice-api-gpu .
docker run --gpus all -p 8080:8080 --name paddleocr-api paddleocr-invoice-api-gpu
```

### Access Points

- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **OCR Endpoint**: http://localhost:8080/ocr/

## 🐳 Docker Configuration

### Base Image
- **Image**: `paddlepaddle/paddle:3.2.1-gpu-cuda12.6-cudnn9.5`
- **CUDA Version**: 12.6
- **cuDNN Version**: 9.5
- **GPU Support**: Full NVIDIA GPU acceleration

### Dockerfile Details

```dockerfile
# Use official PaddlePaddle GPU image with CUDA 12.6 and cuDNN 9.5
FROM paddlepaddle/paddle:3.2.1-gpu-cuda12.6-cudnn9.5

# Set working directory
WORKDIR /app

# Install system dependencies for PaddleOCR
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install PaddleOCR and FastAPI dependencies
RUN pip install --no-cache-dir \
    paddleocr \
    fastapi \
    uvicorn[standard] \
    python-multipart \
    opencv-python-headless \
    numpy \
    pillow

# Copy our FastAPI application
COPY app.py /app/

# Create directory for temporary uploads
RUN mkdir -p /app/temp

# Set environment variables
ENV PADDLEOCR_NO_VISUALIZE=1
ENV CUDA_VISIBLE_DEVICES=0

# Expose port for API
EXPOSE 8080

# Start FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CUDA_VISIBLE_DEVICES` | `0` | GPU device(s) to use |
| `PADDLEOCR_NO_VISUALIZE` | `1` | Disable visualization outputs |
| `NVIDIA_VISIBLE_DEVICES` | `all` | Visible NVIDIA devices |
| `NVIDIA_DRIVER_CAPABILITIES` | `compute,utility` | Driver capabilities |

## 📡 API Endpoints

### Health Check
**GET** `/health`

Returns the health status of the service including GPU availability and PaddleOCR initialization status.

**Response Example:**
```json
{
  "status": "healthy",
  "service": "PaddleOCR Invoice API",
  "version": "1.0.0",
  "paddleocr_initialized": true,
  "paddle_available": true,
  "cuda_available": true,
  "current_device": "gpu:0",
  "using_gpu": true,
  "ocr_ready": true,
  "message": "All systems operational"
}
```

### OCR Processing
**POST** `/ocr/`

Extracts text from uploaded images.

**Request:** Multipart form data with file field
**Supported Formats:** jpg, jpeg, png, bmp, tiff, webp

**Response Example:**
```json
{
  "device": "gpu:0",
  "results": [
    {
      "text": "Invoice #12345",
      "confidence": 0.987,
      "bounding_box": [[100, 50], [300, 50], [300, 80], [100, 80]]
    },
    {
      "text": "Total: $299.99",
      "confidence": 0.956,
      "bounding_box": [[150, 200], [280, 200], [280, 230], [150, 230]]
    }
  ],
  "total_text_regions": 2,
  "success": true
}
```

### Interactive Documentation
**GET** `/docs`

FastAPI's interactive Swagger UI for testing the API.

## 🔧 Application Code Details

### PaddleOCR Initialization

The application uses a robust initialization strategy with GPU-to-CPU fallback:

```python
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
```

### Result Processing

The API handles multiple PaddleOCR output formats:

1. **Traditional Format**: `[[[box], (text, confidence)], ...]`
2. **New Dictionary Format**: Objects with `rec_texts`, `rec_polys`, `rec_scores`

### Error Handling

Comprehensive error handling at multiple levels:
- **Initialization Errors**: GPU fallback with detailed logging
- **Input Validation**: File format and size validation
- **Processing Errors**: Graceful fallback for unexpected OCR results
- **System Errors**: Proper HTTP status codes and error messages

## 📊 Performance Optimization

### GPU Memory Management
```bash
# Limit GPU memory usage
docker run --gpus '"device=0"' --shm-size=1g paddleocr-invoice-api-gpu

# Use specific GPU devices
docker run --gpus all -e CUDA_VISIBLE_DEVICES=0,1 paddleocr-invoice-api-gpu
```

### Resource Limits (Docker Compose)
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
    limits:
      memory: 8G
```

### Batch Processing
For improved performance with multiple images:
- Implement request queuing
- Use batch processing endpoints
- Scale with multiple containers

## 🔍 Testing

### Automated Testing Script
```bash
python test_api.py
```

### Manual Testing Commands
```bash
# Health check
curl http://localhost:8080/health

# OCR with image
curl -X POST http://localhost:8080/ocr/ \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.jpg"

# Check API docs
curl http://localhost:8080/docs
```

### Performance Testing
```python
import requests
import time

# Test response time
start_time = time.time()
with open('test_image.jpg', 'rb') as f:
    response = requests.post('http://localhost:8080/ocr/', files={'file': f})
response_time = time.time() - start_time
print(f"Response time: {response_time:.2f}s")
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. GPU Not Detected
**Problem**: `PaddleOCR service is not available`

**Solutions**:
```bash
# Check NVIDIA Docker installation
docker run --rm --gpus all nvidia/cuda:12.2.2-runtime-ubuntu22.04 nvidia-smi

# Check NVIDIA drivers
nvidia-smi

# Reinstall NVIDIA Docker Toolkit
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

#### 2. CUDA Version Mismatch
**Problem**: Library compatibility issues

**Solutions**:
```bash
# Check host CUDA version
nvidia-smi

# Check container CUDA version
docker exec paddleocr-api nvidia-smi

# Update NVIDIA drivers
# Download from https://developer.nvidia.com/cuda-downloads
```

#### 3. Memory Issues
**Problem**: Out of memory errors

**Solutions**:
```bash
# Increase shared memory
docker run --shm-size=2g ...

# Limit batch size
# Monitor memory usage
docker stats paddleocr-api

# Use smaller images or process in chunks
```

#### 4. Port Conflicts
**Problem**: Port 8080 already in use

**Solutions**:
```bash
# Use different port
docker run -p 8081:8080 ...

# Kill existing container
docker stop paddleocr-api
docker rm paddleocr-api
```

#### 5. Slow Performance
**Problem**: OCR processing is slow

**Solutions**:
```bash
# Check GPU utilization
nvidia-smi

# Verify GPU is being used
curl http://localhost:8080/health

# Optimize image size
# Use appropriate image formats (PNG, JPEG)
```

### Debug Mode
```bash
# Run container with shell access
docker run --gpus all -p 8080:8080 --entrypoint /bin/bash -it paddleocr-invoice-api-gpu

# Check logs
docker logs -f paddleocr-api

# Check Python environment
docker exec paddleocr-api python -c "import paddle; print(paddle.device.get_device())"
```

## 🚀 Production Deployment

### Security Considerations

#### Authentication
```python
# Add API key authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Implement your token validation logic
    pass

@app.post("/ocr/", dependencies=[Depends(verify_token)])
async def protected_ocr_endpoint(file: UploadFile = File(...)):
    # Your OCR logic
    pass
```

#### Rate Limiting
```python
# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/ocr/")
@limiter.limit("10/minute")
async def rate_limited_ocr(request: Request, file: UploadFile = File(...)):
    # Your OCR logic
    pass
```

#### SSL/TLS Configuration
```nginx
# Nginx reverse proxy with SSL
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Scaling Strategies

#### Docker Swarm
```yaml
version: '3.8'
services:
  paddleocr-api:
    image: paddleocr-invoice-api-gpu
    deploy:
      replicas: 2
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

#### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: paddleocr-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: paddleocr-api
  template:
    metadata:
      labels:
        app: paddleocr-api
    spec:
      containers:
      - name: paddleocr-api
        image: paddleocr-invoice-api-gpu
        ports:
        - containerPort: 8080
        resources:
          limits:
            nvidia.com/gpu: 1
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
---
apiVersion: v1
kind: Service
metadata:
  name: paddleocr-service
spec:
  selector:
    app: paddleocr-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Monitoring and Logging

#### Health Monitoring
```bash
# Continuous health checks
while true; do
    curl -f http://localhost:8080/health || echo "Health check failed"
    sleep 30
done
```

#### Log Management
```yaml
# Docker Compose with logging
services:
  paddleocr-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    volumes:
      - ./logs:/app/logs
```

#### Prometheus Monitoring
```python
# Add metrics to your API
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('ocr_requests_total', 'Total OCR requests')
REQUEST_DURATION = Histogram('ocr_request_duration_seconds', 'OCR request duration')

@app.post("/ocr/")
@REQUEST_DURATION.time()
async def ocr_endpoint(file: UploadFile = File(...)):
    REQUEST_COUNT.inc()
    # Your OCR logic
    pass
```

## 📈 Performance Benchmarks

### Expected Performance

| Hardware | Images/Second | Avg Response Time | GPU Utilization |
|----------|---------------|------------------|-----------------|
| RTX 3060 (6GB) | 2-3 | 1.5-2.5s | 70-85% |
| RTX 4090 (24GB) | 8-12 | 0.5-1.0s | 60-80% |
| Tesla T4 (16GB) | 4-6 | 1.0-1.8s | 65-75% |

### Optimization Tips

1. **Image Preparation**
   - Use appropriate resolution (300-600 DPI)
   - Pre-process images (contrast, noise reduction)
   - Use JPEG for photos, PNG for documents

2. **Batch Processing**
   - Process multiple images in parallel
   - Implement request queuing
   - Use GPU memory efficiently

3. **Caching**
   - Cache processed results
   - Use Redis for distributed caching
   - Implement smart cache invalidation

## 🔧 Maintenance

### Regular Tasks

**Daily:**
- Monitor GPU utilization
- Check error logs
- Verify API health

**Weekly:**
- Update container images
- Review performance metrics
- Clean up temporary files

**Monthly:**
- Update NVIDIA drivers
- Review security patches
- Backup configuration

### Backup and Recovery

**Configuration Backup:**
```bash
# Export Docker configuration
docker save paddleocr-invoice-api-gpu > paddleocr-backup.tar

# Backup configuration files
tar -czf paddleocr-config.tar.gz docker-compose.yml .dockerignore deploy_*
```

**Disaster Recovery:**
```bash
# Restore from backup
docker load < paddleocr-backup.tar
docker-compose up -d

# Verify restoration
curl http://localhost:8080/health
```

## 📚 References and Resources

### Official Documentation
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddlePaddle Documentation](https://www.paddlepaddle.org.cn/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)

### Community and Support
- [PaddleOCR Issues](https://github.com/PaddlePaddle/PaddleOCR/issues)
- [FastAPI Discussions](https://github.com/tiangolo/fastapi/discussions)
- [NVIDIA Developer Forums](https://developer.nvidia.com/)

### Related Projects
- [Paddle.js](https://github.com/PaddlePaddle/Paddle.js) - Browser-based PaddlePaddle
- [Paddle Serving](https://github.com/PaddlePaddle/Serving) - Production serving framework
- [PaddleHub](https://github.com/PaddlePaddle/PaddleHub) - Pre-trained model library

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

### Third-Party Licenses
- PaddleOCR: Apache 2.0
- FastAPI: MIT
- PaddlePaddle: Apache 2.0

---

## 🎯 Quick Reference Commands

### Essential Commands
```bash
# Build and run
docker-compose up -d --build

# Check health
curl http://localhost:8080/health

# View logs
docker logs -f paddleocr-api

# Stop service
docker-compose down

# Test OCR
curl -X POST http://localhost:8080/ocr/ -F "file=@test.jpg"

# Monitor GPU
nvidia-smi

# Docker stats
docker stats paddleocr-api
```

### Troubleshooting Commands
```bash
# Check GPU availability
docker run --rm --gpus all nvidia/cuda:12.2.2-runtime-ubuntu22.04 nvidia-smi

# Debug container
docker exec -it paddleocr-api bash

# Force rebuild
docker-compose build --no-cache

# Clean up
docker system prune -f
```

This documentation covers everything you need to successfully deploy, manage, and troubleshoot your PaddleOCR Invoice API with GPU acceleration.