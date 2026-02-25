#FROM python:3.11 AS builder
#
#ENV PYTHONUNBUFFERED=1 \
#    PYTHONDONTWRITEBYTECODE=1
#WORKDIR /app
#
#RUN python -m venv .venv
#COPY pyproject.toml ./
#RUN .venv/bin/pip install .
#FROM python:3.11-slim
#WORKDIR /app
#COPY --from=builder /app/.venv .venv/
#COPY . .
#CMD ["/app/.venv/bin/fastapi", "run"]


FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Prevent .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (layer caching)
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ app/

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]