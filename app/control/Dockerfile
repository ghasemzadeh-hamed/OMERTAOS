FROM python:3.11-slim

WORKDIR /srv/app

ENV PYTHONPATH=/srv/app:/srv/app/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY app/control/pyproject.toml ./pyproject.toml
COPY app/control/README.md ./README.md
COPY app/control/aionos_control ./aionos_control
COPY app/control/app ./app
COPY app/kernel ./app/kernel

RUN pip install --upgrade pip setuptools wheel \
    && pip install -e .

EXPOSE 8000

CMD ["python", "-m", "app.control.app.main"]
