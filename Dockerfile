FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}" \
    RUNTIME_DIR=/app/runtime

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/runtime \
    && chown -R appuser:appuser /app/runtime

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').getenv('PORT','8080') + '/health', timeout=3).read()" || exit 1

CMD ["sh", "-c", "uv run uvicorn web_control:app --host 0.0.0.0 --port ${PORT:-8080}"]
