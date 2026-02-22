FROM python:3.11-slim

WORKDIR /srv/app

ENV PYTHONPATH=/srv/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

COPY control/pyproject.toml ./control/pyproject.toml
COPY control/README.md ./control/README.md
COPY control ./control
COPY config ./config
COPY kernel ./kernel
COPY secret_store ./secret_store
#COPY ai_registry ./ai_registry
COPY policies ./policies

RUN pip install --upgrade pip setuptools wheel \
    && pip install -e ./control

EXPOSE 8000

CMD ["python", "-m", "control.os.main"]
