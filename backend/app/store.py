import secrets
from datetime import UTC, datetime

from app.models import DailyStats, GuestStatus, Table, TableStatus, WaitlistGuest


class GuestNotFoundError(Exception):
    pass


class TableNotFoundError(Exception):
    pass


class GuestNotReadyError(Exception):
    pass


def _default_tables() -> list[Table]:
    return [
        Table(id='t1', name='Table 1', capacity=2, status=TableStatus.FREE),
        Table(id='t2', name='Table 2', capacity=2, status=TableStatus.FREE),
        Table(id='t3', name='Table 3', capacity=4, status=TableStatus.FREE),
        Table(id='t4', name='Table 4', capacity=4, status=TableStatus.FREE),
        Table(id='t5', name='Table 5', capacity=6, status=TableStatus.FREE),
        Table(id='t6', name='Table 6', capacity=8, status=TableStatus.FREE),
    ]


class WaitlistStore:
    """In-memory mock database. Swap this out for a real one later; the
    router layer only talks to the methods below."""

    def __init__(self) -> None:
        self.tables: dict[str, Table] = {t.id: t for t in _default_tables()}
        self.guests: dict[str, WaitlistGuest] = {}
        self._next_guest_id = 1
        self.average_wait_minutes = 15
        self.total_seated = 0
        self.total_no_show = 0

    def _waiting_guests_by_priority(self) -> list[WaitlistGuest]:
        # Largest party first: fills the biggest free tables efficiently and
        # avoids stranding a big party behind several small ones.
        waiting = [g for g in self.guests.values() if g.status == GuestStatus.WAITING]
        return sorted(waiting, key=lambda g: (-g.party_size, g.created_at))

    def _recalc_estimated_waits(self) -> None:
        for index, guest in enumerate(self._waiting_guests_by_priority()):
            guest.estimated_wait_minutes = max(5, (index + 1) * self.average_wait_minutes)

    def _recalc_assignments(self) -> None:
        free_tables = sorted(
            (t for t in self.tables.values() if t.status == TableStatus.FREE),
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
            table.occupied_by_guest_id = guest.id
            guest.status = GuestStatus.TABLE_READY
            guest.assigned_table_id = table.id

        self._recalc_estimated_waits()

    def list_tables(self) -> list[Table]:
        return sorted(self.tables.values(), key=lambda t: t.id)

    def list_waitlist(self) -> list[WaitlistGuest]:
        return sorted(self.guests.values(), key=lambda g: g.created_at)

    def get_stats(self) -> DailyStats:
        return DailyStats(
            total_seated=self.total_seated,
            total_no_show=self.total_no_show,
            average_wait_minutes=self.average_wait_minutes,
        )

    def add_guest(self, *, name: str, party_size: int, phone: str, notes: str) -> WaitlistGuest:
        guest = WaitlistGuest(
            id=str(self._next_guest_id),
            token=secrets.token_urlsafe(6),
            name=name,
            party_size=party_size,
            phone=phone,
            notes=notes,
            status=GuestStatus.WAITING,
            created_at=datetime.now(UTC),
            estimated_wait_minutes=self.average_wait_minutes,
        )
        self._next_guest_id += 1
        self.guests[guest.id] = guest
        self._recalc_assignments()
        return guest

    def seat_guest(self, guest_id: str) -> WaitlistGuest:
        guest = self.guests.get(guest_id)
        if guest is None:
            raise GuestNotFoundError(guest_id)
        if guest.status != GuestStatus.TABLE_READY:
            raise GuestNotReadyError(guest_id)

        actual_minutes = (datetime.now(UTC) - guest.created_at).total_seconds() / 60
        self.average_wait_minutes = round(
            (self.average_wait_minutes * self.total_seated + actual_minutes) / (self.total_seated + 1)
        )
        self.total_seated += 1
        guest.status = GuestStatus.SEATED
        return guest

    def mark_table_pending_free(self, table_id: str) -> None:
        table = self.tables.get(table_id)
        if table is not None and table.status == TableStatus.OCCUPIED:
            table.status = TableStatus.PENDING_FREE

    def cancel_guest(self, guest_id: str) -> WaitlistGuest:
        guest = self.guests.get(guest_id)
        if guest is None:
            raise GuestNotFoundError(guest_id)

        was_table_ready = guest.status == GuestStatus.TABLE_READY
        guest.status = GuestStatus.CANCELLED_NO_SHOW
        self.total_no_show += 1

        if was_table_ready and guest.assigned_table_id:
            table = self.tables.get(guest.assigned_table_id)
            if table is not None:
                table.status = TableStatus.FREE
                table.occupied_by_guest_id = None
            guest.assigned_table_id = None
            self._recalc_assignments()

        return guest

    def confirm_table_free(self, table_id: str) -> Table:
        table = self.tables.get(table_id)
        if table is None:
            raise TableNotFoundError(table_id)

        table.status = TableStatus.FREE
        table.occupied_by_guest_id = None
        self._recalc_assignments()
        return table

    def get_guest_by_token(self, token: str) -> WaitlistGuest | None:
        return next((g for g in self.guests.values() if g.token == token), None)


store = WaitlistStore()


def get_store() -> WaitlistStore:
    return store
