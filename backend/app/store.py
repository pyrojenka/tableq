import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import GuestRow, StatsRow, TableRow
from app.models import DailyStats, GuestStatus, Table, TableStatus, WaitlistGuest


class GuestNotFoundError(Exception):
    pass


class TableNotFoundError(Exception):
    pass


class GuestNotReadyError(Exception):
    pass


DEFAULT_TABLES = [
    ('t1', 'Table 1', 2),
    ('t2', 'Table 2', 2),
    ('t3', 'Table 3', 4),
    ('t4', 'Table 4', 4),
    ('t5', 'Table 5', 6),
    ('t6', 'Table 6', 8),
]


def _ensure_seeded(session: Session) -> None:
    if session.get(StatsRow, 1) is None:
        session.add(StatsRow(id=1, average_wait_minutes=15, total_seated=0, total_no_show=0))

    if session.scalar(select(TableRow.id).limit(1)) is None:
        for table_id, name, capacity in DEFAULT_TABLES:
            session.add(TableRow(id=table_id, name=name, capacity=capacity, status=TableStatus.FREE))

    session.commit()


def _utcnow() -> datetime:
    # Stored naive (SQLite drops tzinfo on read-back); reattached as UTC
    # only when handed out through the Pydantic model below.
    return datetime.now(UTC).replace(tzinfo=None)


def _table_to_model(row: TableRow) -> Table:
    return Table(
        id=row.id,
        name=row.name,
        capacity=row.capacity,
        status=TableStatus(row.status),
        occupied_by_guest_id=row.occupied_by_guest_id,
    )


def _guest_to_model(row: GuestRow) -> WaitlistGuest:
    return WaitlistGuest(
        id=str(row.id),
        token=row.token,
        name=row.name,
        party_size=row.party_size,
        phone=row.phone,
        notes=row.notes,
        status=GuestStatus(row.status),
        created_at=row.created_at.replace(tzinfo=UTC),
        estimated_wait_minutes=row.estimated_wait_minutes,
        assigned_table_id=row.assigned_table_id,
    )


def _get_guest_row(session: Session, guest_id: str) -> GuestRow | None:
    if not guest_id.isdigit():
        return None
    return session.get(GuestRow, int(guest_id))


class WaitlistStore:
    """Talks to the real database via SQLAlchemy. Swap DATABASE_URL in
    app/db.py to point at a different database; this layer doesn't change."""

    def __init__(self, session: Session) -> None:
        self.session = session
        _ensure_seeded(session)

    def _stats_row(self) -> StatsRow:
        stats = self.session.get(StatsRow, 1)
        assert stats is not None
        return stats

    def _waiting_guests_by_priority(self) -> list[GuestRow]:
        # Largest party first: fills the biggest free tables efficiently and
        # avoids stranding a big party behind several small ones.
        waiting = self.session.scalars(select(GuestRow).where(GuestRow.status == GuestStatus.WAITING)).all()
        return sorted(waiting, key=lambda g: (-g.party_size, g.created_at))

    def _recalc_estimated_waits(self) -> None:
        average_wait_minutes = self._stats_row().average_wait_minutes
        for index, guest in enumerate(self._waiting_guests_by_priority()):
            guest.estimated_wait_minutes = max(5, (index + 1) * average_wait_minutes)

    def _recalc_assignments(self) -> None:
        free_tables = sorted(
            self.session.scalars(select(TableRow).where(TableRow.status == TableStatus.FREE)).all(),
            key=lambda t: t.capacity,
        )

        for guest in self._waiting_guests_by_priority():
            table = next(
                (t for t in free_tables if t.status == TableStatus.FREE and t.capacity >= guest.party_size),
                None,
            )
            if table is None:
                continue

            table.status = TableStatus.OCCUPIED
            table.occupied_by_guest_id = str(guest.id)
            guest.status = GuestStatus.TABLE_READY
            guest.assigned_table_id = table.id

        self._recalc_estimated_waits()
        self.session.commit()

    def list_tables(self) -> list[Table]:
        rows = self.session.scalars(select(TableRow).order_by(TableRow.id)).all()
        return [_table_to_model(r) for r in rows]

    def list_waitlist(self) -> list[WaitlistGuest]:
        rows = self.session.scalars(select(GuestRow).order_by(GuestRow.created_at)).all()
        return [_guest_to_model(r) for r in rows]

    def get_stats(self) -> DailyStats:
        stats = self._stats_row()
        return DailyStats(
            total_seated=stats.total_seated,
            total_no_show=stats.total_no_show,
            average_wait_minutes=stats.average_wait_minutes,
        )

    def add_guest(self, *, name: str, party_size: int, phone: str, notes: str) -> WaitlistGuest:
        guest = GuestRow(
            token=secrets.token_urlsafe(6),
            name=name,
            party_size=party_size,
            phone=phone,
            notes=notes,
            status=GuestStatus.WAITING,
            created_at=_utcnow(),
            estimated_wait_minutes=self._stats_row().average_wait_minutes,
        )
        self.session.add(guest)
        self.session.flush()
        self._recalc_assignments()
        self.session.refresh(guest)
        return _guest_to_model(guest)

    def seat_guest(self, guest_id: str) -> WaitlistGuest:
        guest = _get_guest_row(self.session, guest_id)
        if guest is None:
            raise GuestNotFoundError(guest_id)
        if guest.status != GuestStatus.TABLE_READY:
            raise GuestNotReadyError(guest_id)

        stats = self._stats_row()
        actual_minutes = (_utcnow() - guest.created_at).total_seconds() / 60
        stats.average_wait_minutes = round(
            (stats.average_wait_minutes * stats.total_seated + actual_minutes) / (stats.total_seated + 1)
        )
        stats.total_seated += 1
        guest.status = GuestStatus.SEATED
        self.session.commit()
        self.session.refresh(guest)
        return _guest_to_model(guest)

    def mark_table_pending_free(self, table_id: str) -> None:
        table = self.session.get(TableRow, table_id)
        if table is not None and table.status == TableStatus.OCCUPIED:
            table.status = TableStatus.PENDING_FREE
            self.session.commit()

    def cancel_guest(self, guest_id: str) -> WaitlistGuest:
        guest = _get_guest_row(self.session, guest_id)
        if guest is None:
            raise GuestNotFoundError(guest_id)

        was_table_ready = guest.status == GuestStatus.TABLE_READY
        guest.status = GuestStatus.CANCELLED_NO_SHOW
        self._stats_row().total_no_show += 1

        if was_table_ready and guest.assigned_table_id:
            table = self.session.get(TableRow, guest.assigned_table_id)
            if table is not None:
                table.status = TableStatus.FREE
                table.occupied_by_guest_id = None
            guest.assigned_table_id = None
            self._recalc_assignments()
        else:
            self.session.commit()

        self.session.refresh(guest)
        return _guest_to_model(guest)

    def confirm_table_free(self, table_id: str) -> Table:
        table = self.session.get(TableRow, table_id)
        if table is None:
            raise TableNotFoundError(table_id)

        table.status = TableStatus.FREE
        table.occupied_by_guest_id = None
        self._recalc_assignments()
        self.session.refresh(table)
        return _table_to_model(table)

    def get_guest_by_token(self, token: str) -> WaitlistGuest | None:
        guest = self.session.scalar(select(GuestRow).where(GuestRow.token == token))
        return _guest_to_model(guest) if guest else None
