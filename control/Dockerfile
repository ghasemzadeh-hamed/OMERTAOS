FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10

WORKDIR /app

COPY control/requirements.docker.txt ./control/requirements.docker.txt

RUN pip install --no-cache-dir --requirement ./control/requirements.docker.txt

COPY control ./control
COPY schemas ./schemas
COPY registry/models ./registry/models
COPY policies ./policies
COPY shared ./shared

EXPOSE 8000 50051

CMD ["python", "-m", "control.app.serve"]
