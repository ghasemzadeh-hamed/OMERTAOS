FROM python:3.11-slim

WORKDIR /srv/app

ENV PYTHONPATH=/srv/app:/srv/app/os

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY os/control/pyproject.toml ./pyproject.toml
COPY os/control/README.md ./README.md
COPY os/control/aionos_control ./aionos_control
COPY os ./os
COPY aion ./aion
COPY app ./app
COPY kernel-multitenant ./kernel-multitenant
COPY profiles ./profiles
COPY sitecustomize.py ./sitecustomize.py

RUN pip install --upgrade pip setuptools wheel \
    && pip install -e .

EXPOSE 8000

CMD ["python", "-m", "os.control.os.main"]
