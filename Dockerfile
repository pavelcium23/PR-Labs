FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY memory_scramble /app/memory_scramble
COPY kvstore /app/kvstore
COPY boards /app/boards

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn kvstore.app:app --factory --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]
