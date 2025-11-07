
FROM paddlepaddle/paddle:3.2.1-gpu-cuda12.6-cudnn9.5

# Install dependencies
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir paddleocr fastapi uvicorn opencv-python-headless numpy python-multipart "paddlex[ocr]==3.3.6" pillow

# Avoid font downloads
ENV PADDLEOCR_NO_VISUALIZE=1
RUN mkdir -p /root/.paddlex/PaddleX3.0 && rm -rf /root/.paddlex/PaddleX3.0/fonts

# Preload model to cache
RUN python3 -c "from paddleocr import PaddleOCR"

# Copy app files
WORKDIR /app
COPY app.py /app/

# Expose port for API
EXPOSE 8080

# Start FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]



