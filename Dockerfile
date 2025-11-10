
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



