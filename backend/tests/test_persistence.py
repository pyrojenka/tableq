from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.store import WaitlistStore


def test_data_survives_across_sessions_on_disk(tmp_path):
    """Guards against accidentally going back to an in-memory/mock store:
    data must actually be persisted by the database file, not just kept
    alive in a Python object."""
    db_path = tmp_path / 'tableq_test.db'
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)

    session_one = session_factory()
    store_one = WaitlistStore(session_one)
    guest = store_one.add_guest(name='Alice', party_size=2, phone='555-1', notes='')
    session_one.close()

    # brand new session/store, same underlying file
    session_two = session_factory()
    store_two = WaitlistStore(session_two)

    reloaded = store_two.get_guest_by_token(guest.token)
    assert reloaded is not None
    assert reloaded.name == 'Alice'
    assert reloaded.status == 'table_ready'

    tables = store_two.list_tables()
    assert len(tables) == 6  # seeding must not duplicate on the second store
    session_two.close()
