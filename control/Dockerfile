FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/app"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libblas-dev \
    liblapack-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md
COPY app /app/app
COPY control/aionos_control /app/aionos_control

RUN pip install --upgrade pip setuptools wheel
RUN pip install ".[control]"

ARG AION_EXTRAS=""
RUN if [ -n "$AION_EXTRAS" ]; then pip install ".[${AION_EXTRAS}]"; fi

COPY control/ /app/control

EXPOSE 8000

CMD ["uvicorn", "app.control.main:app", "--host", "0.0.0.0", "--port", "8000"]
