FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir \
        "fastapi>=0.115" \
        "uvicorn[standard]>=0.30" \
        "httpx>=0.27" \
        "pyyaml>=6.0" \
        "sqlalchemy>=2.0" \
        "psycopg2-binary>=2.9"

COPY control ./control
COPY schemas ./schemas
COPY registry/models ./registry/models
COPY policies ./policies
COPY observability ./observability
COPY shared ./shared

EXPOSE 8000 50051

CMD ["uvicorn", "control.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
