FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

WORKDIR /app

COPY pyproject.toml /app/
COPY app /app/app
COPY config /app/config

RUN pip install --no-cache-dir fastapi uvicorn[standard] pyyaml requests

EXPOSE 9100

CMD ["uvicorn", "app.kernel.main:app", "--host", "0.0.0.0", "--port", "9100"]
