import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.db_models import TableRow
from app.main import app
from app.models import TableStatus
from app.store import WaitlistStore


@pytest.fixture
def db_session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def store(db_session: Session) -> WaitlistStore:
    return WaitlistStore(db_session)


@pytest.fixture
def client(store: WaitlistStore):
    app.dependency_overrides[get_db] = lambda: store.session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def occupy_table(store: WaitlistStore):
    def _occupy(table_id: str, occupied_by_guest_id: str | None = None) -> None:
        table = store.session.get(TableRow, table_id)
        assert table is not None
        table.status = TableStatus.OCCUPIED
        table.occupied_by_guest_id = occupied_by_guest_id
        store.session.commit()

    return _occupy


ALL_TABLE_IDS = ('t1', 't2', 't3', 't4', 't5', 't6')


@pytest.fixture
def occupy_all_tables(occupy_table):
    def _occupy_all(except_ids: tuple[str, ...] = ()) -> None:
        for table_id in ALL_TABLE_IDS:
            if table_id not in except_ids:
                occupy_table(table_id, occupied_by_guest_id='someone-else')

    return _occupy_all
