FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Copy dependency files first for layer caching
# Copying this separately prevents re-running uv sync on every code change.
COPY pyproject.toml uv.lock ./

ENV ENV=prod
ENV APP_HOME /app

WORKDIR $APP_HOME
COPY . ./

RUN uv sync

CMD ["python3", "indeed_client.py"]