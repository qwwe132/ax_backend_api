FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.2 /uv /uvx /bin/
WORKDIR /srv/board
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY app ./app
RUN useradd --system board
USER board
EXPOSE 8000
CMD ["/srv/board/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
