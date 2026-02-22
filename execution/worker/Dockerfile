FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .[control]

ENV AION_CONFIG_FILE=/app/aion/config/aion.yaml

CMD ["python", "-m", "aion.worker.catalog_sync"]
