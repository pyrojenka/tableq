# TableQ

Restaurant waitlist manager. A hostess manages the waitlist and table
assignments; guests check their own status via a personal QR-linked page.

See [_docs/specs.md](_docs/specs.md) for the full specification and
[openapi.yaml](openapi.yaml) for the API.

## Stack

- Backend: FastAPI (Python, `uv`)
- Frontend: React + Vite + TypeScript, Tailwind CSS
- Database: SQLite via SQLAlchemy (database-agnostic — swap `DATABASE_URL`
  for any SQLAlchemy-supported database)

## Running locally

Backend (http://localhost:8000):

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Frontend (http://localhost:5173):

```bash
cd frontend
npm install
npm run dev
```

Backend tests:

```bash
cd backend
uv run pytest -v
```

All API routes are under `/api` (e.g. `GET /api/tables`); anything else is
served as the frontend.

## Running with Docker

Builds the frontend, then bundles it with the backend into a single image
that serves both:

```bash
docker build -t tableq .
docker run -p 8000:8000 -v tableq-data:/data tableq
```

Open http://localhost:8000. The SQLite file lives at `/data/tableq.db`
inside the container; the `-v` flag persists it across restarts.

### With Postgres

`docker-compose.yml` runs the same image against a real Postgres instead:

```bash
docker compose up --build
```

This sets `DATABASE_URL=postgresql+psycopg://tableq:tableq@db:5432/tableq`
for the app service. To point any backend run at Postgres yourself (e.g.
outside Docker), set `DATABASE_URL` to a `postgresql+psycopg://` URL —
`app/store.py` doesn't change either way.

## Status

Frontend, backend, and database are wired up end-to-end. Built as part of
the AI Dev Camp 2026 homework.
