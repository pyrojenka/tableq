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

## Status

Frontend, backend, and database are wired up end-to-end. Built as part of
the AI Dev Camp 2026 homework.
