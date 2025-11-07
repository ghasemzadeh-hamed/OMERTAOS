FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential libblas-dev liblapack-dev libffi-dev git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY control/pyproject.toml ./pyproject.toml
COPY control/README.md ./README.md
COPY control/aionos_control ./aionos_control
COPY control/app ./app

RUN pip install --upgrade pip setuptools wheel
RUN pip install "."

ARG AION_EXTRAS=""
RUN if [ -n "$AION_EXTRAS" ]; then pip install ".[${AION_EXTRAS}]"; fi

COPY control/ ./
EXPOSE 8080
CMD ["uvicorn","aionos_control.main:app","--host","0.0.0.0","--port","8080"]
