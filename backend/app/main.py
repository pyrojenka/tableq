import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import app.db_models  # noqa: F401  registers models on Base before create_all
from app.db import Base, SessionLocal, engine, get_db
from app.models import AddGuestRequest, DailyStats, Table, WaitlistGuest
from app.store import GuestNotFoundError, GuestNotReadyError, TableNotFoundError, WaitlistStore

# Meal duration is accelerated for the demo so the "table likely free" reminder
# is visible without waiting real minutes.
MOCK_MEAL_DURATION_SECONDS = 20

STATIC_DIR = Path(__file__).parent / 'static'

Base.metadata.create_all(bind=engine)

app = FastAPI(title='TableQ API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)

api = APIRouter(prefix='/api')


def get_store(db: Session = Depends(get_db)) -> WaitlistStore:
    return WaitlistStore(db)


async def _schedule_pending_free(table_id: str) -> None:
    await asyncio.sleep(MOCK_MEAL_DURATION_SECONDS)
    db = SessionLocal()
    try:
        WaitlistStore(db).mark_table_pending_free(table_id)
    finally:
        db.close()


@api.get('/tables', response_model=list[Table])
def list_tables(store: WaitlistStore = Depends(get_store)):
    return store.list_tables()


@api.post('/tables/{table_id}/confirm-free', response_model=Table)
def confirm_table_free(table_id: str, store: WaitlistStore = Depends(get_store)):
    try:
        return store.confirm_table_free(table_id)
    except TableNotFoundError:
        raise HTTPException(status_code=404, detail='Table not found')


@api.get('/waitlist', response_model=list[WaitlistGuest])
def list_waitlist(store: WaitlistStore = Depends(get_store)):
    return store.list_waitlist()


@api.post('/waitlist', response_model=WaitlistGuest, status_code=201)
def add_guest(request: AddGuestRequest, store: WaitlistStore = Depends(get_store)):
    return store.add_guest(
        name=request.name, party_size=request.party_size, phone=request.phone, notes=request.notes
    )


@api.post('/waitlist/{guest_id}/seat', response_model=WaitlistGuest)
async def seat_guest(guest_id: str, store: WaitlistStore = Depends(get_store)):
    try:
        guest = store.seat_guest(guest_id)
    except GuestNotFoundError:
        raise HTTPException(status_code=404, detail='Guest not found')
    except GuestNotReadyError:
        raise HTTPException(status_code=409, detail='Guest is not in table_ready status')

    if guest.assigned_table_id:
        asyncio.create_task(_schedule_pending_free(guest.assigned_table_id))

    return guest


@api.post('/waitlist/{guest_id}/cancel', response_model=WaitlistGuest)
def cancel_guest(guest_id: str, store: WaitlistStore = Depends(get_store)):
    try:
        return store.cancel_guest(guest_id)
    except GuestNotFoundError:
        raise HTTPException(status_code=404, detail='Guest not found')


@api.get('/guest/{token}', response_model=WaitlistGuest)
def get_guest_by_token(token: str, store: WaitlistStore = Depends(get_store)):
    guest = store.get_guest_by_token(token)
    if guest is None:
        raise HTTPException(status_code=404, detail='Guest not found')
    return guest


@api.get('/stats', response_model=DailyStats)
def get_stats(store: WaitlistStore = Depends(get_store)):
    return store.get_stats()


app.include_router(api)

# In the Docker image, the frontend is built into app/static and served
# from here so the backend is the single thing that needs to run. In local
# dev (no static/ directory), this is skipped and Vite serves the frontend
# on its own port instead.
if STATIC_DIR.exists():
    app.mount('/assets', StaticFiles(directory=STATIC_DIR / 'assets'), name='assets')

    @app.get('/{full_path:path}', include_in_schema=False)
    async def serve_frontend(full_path: str):
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / 'index.html')
