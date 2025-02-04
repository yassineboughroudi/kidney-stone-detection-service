FROM python:3.10-slim

# 1) Set a working directory
WORKDIR /app

# 2) Install system build dependencies if needed (e.g., for wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 3) Create a virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# 4) Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 5) Copy the rest of your Python code
COPY . /app

# 6) Expose the FastAPI port
EXPOSE 8000

# 7) Run uvicorn from the venv
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]