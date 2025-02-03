FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (if you need to compile some packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements to leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the service code
COPY . /app

# Expose the FastAPI port
EXPOSE 8000

# Launch the FastAPI service using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
