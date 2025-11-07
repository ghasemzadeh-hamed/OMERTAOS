FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/os"

WORKDIR /app

COPY os /app/os

RUN pip install --no-cache-dir fastapi uvicorn pydantic pyyaml

EXPOSE 8010

CMD ["uvicorn", "os.kernel.devserver:app", "--host", "0.0.0.0", "--port", "8010"]
