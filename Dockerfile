FROM python:3.11-slim

# 1. system deps (curl = health checks, gcc for FAISS wheel on slim images)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# 2. project files
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the source code
COPY . .

# 3. default runtime
ENV PYTHONUNBUFFERED=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    # make uvicorn hot-reload configurable
    FASTAPI_RELOAD=false

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000 ${FASTAPI_RELOAD:+--reload}"]
