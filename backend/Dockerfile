# Multi-stage Dockerfile for TinyURL backend MVP
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .[dev]

FROM base AS runtime
# Create non-root user
RUN useradd -m tinyurl
USER tinyurl
WORKDIR /app
COPY --chown=tinyurl:tinyurl pyproject.toml ./
COPY --chown=tinyurl:tinyurl src ./src
ENV PORT=8000
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
