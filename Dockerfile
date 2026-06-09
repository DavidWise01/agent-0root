# agent-0root · deterministic agent service
FROM python:3.12-slim

WORKDIR /app

# deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app
COPY app/ ./app/
COPY static/ ./static/
COPY tests/ ./tests/

# stamp the build with the commit if provided (Railway also injects RAILWAY_GIT_COMMIT_SHA at runtime)
ARG GIT_SHA=docker
ENV GIT_SHA=${GIT_SHA}

# Railway provides $PORT; default 8000 locally. Shell form so $PORT expands.
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
