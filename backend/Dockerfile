FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Install deps from pyproject.toml + uv.lock (layer cached on dep change only)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy app code
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Install project itself (separate layer so code changes don't reinstall deps)
RUN uv sync --frozen --no-dev

EXPOSE 8000

# Apply pending migrations, then start the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.entrypoints.web.app:app --host 0.0.0.0 --port 8000"]
