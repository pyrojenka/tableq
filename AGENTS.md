# Agent instructions

This is TableQ, a restaurant waitlist manager. Full spec:
[_docs/specs.md](_docs/specs.md).

## Project layout

- `frontend/` — frontend app, all backend calls centralized in one module
- `backend/` — FastAPI backend, `uv` for package management, SQLAlchemy for
  the database (kept database-agnostic)

## Conventions

- Write tests for backend endpoints before implementing them.
- Keep backend calls in the frontend mocked and centralized until the real
  backend is wired up.
- Do not add features beyond what's in `_docs/specs.md` without updating the
  spec first.
