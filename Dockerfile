#For testing locally
#FROM --platform=linux/arm64 python:3.11-slim-bookworm

# Force AMD64 for compatibility with GitHub Actions
FROM --platform=linux/amd64 python:3.11-slim

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    THINC_BACKEND=numpy \
    BLIS_ARCH=generic

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir numpy==1.26.4 && \
    pip install --no-cache-dir python-multipart==0.0.7 && \
    pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --no-binary blis,thinc  # Force source build with our arch settings

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]