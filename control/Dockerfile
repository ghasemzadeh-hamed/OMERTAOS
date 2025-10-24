FROM python:3.11-slim AS base
WORKDIR /app
ENV POETRY_VIRTUALENVS_CREATE=false
RUN pip install --no-cache-dir poetry
COPY pyproject.toml ./
RUN poetry install --no-root --no-interaction
COPY . .
RUN poetry install --no-interaction

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
