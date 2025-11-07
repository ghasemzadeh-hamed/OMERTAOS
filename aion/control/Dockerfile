FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .[control]

ENV AION_CONFIG_FILE=/app/aion/config/aion.yaml

EXPOSE 8000

CMD ["uvicorn", "aion.control.catalog_api:app", "--host", "0.0.0.0", "--port", "8000"]
