FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/app"

WORKDIR /app

COPY app /app/app

RUN pip install --no-cache-dir fastapi uvicorn pydantic pyyaml

EXPOSE 8010

CMD ["uvicorn", "app.kernel.devserver:app", "--host", "0.0.0.0", "--port", "8010"]
