FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app/kernel
RUN pip install --no-cache-dir fastapi uvicorn pydantic

EXPOSE 8010

CMD ["uvicorn", "kernel.devserver:app", "--host", "0.0.0.0", "--port", "8010"]
