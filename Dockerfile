# Stage 1: build the frontend static assets with Node.
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
# Same origin as the backend in this image, so API calls are relative
# (see app/api/client.ts: request() prepends BASE_URL + "/api").
ENV VITE_API_URL=""
RUN npm run build

# Stage 2: the backend, serving the built frontend as static files.
FROM python:3.12-slim AS backend
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /uvx /usr/local/bin/

COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/app ./app
COPY --from=frontend-builder /app/frontend/dist ./app/static

ENV DATABASE_URL=sqlite:////data/tableq.db
VOLUME ["/data"]

EXPOSE 8000
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
