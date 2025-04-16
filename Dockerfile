FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN uv sync

ENV ENV=prod