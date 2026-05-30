# ========================================================
# Phase 1: Build stage
# ========================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install compilation dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pre-install wheels to speed up build cycles
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================================
# Phase 2: Runtime stage
# ========================================================
FROM python:3.11-slim as runner

WORKDIR /app

# Copy dependencies installed in builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application source code
COPY app/ /app/app/
COPY .env* /app/

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
