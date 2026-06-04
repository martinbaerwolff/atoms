FROM python:3.13-slim AS base
WORKDIR /app
RUN pip install uv

FROM base AS dev
COPY pyproject.toml uv.lock* ./
RUN uv sync
COPY . .

FROM base AS prod
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
