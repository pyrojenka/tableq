from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class GuestStatus(StrEnum):
    WAITING = 'waiting'
    TABLE_READY = 'table_ready'
    SEATED = 'seated'
    CANCELLED_NO_SHOW = 'cancelled_no_show'


class TableStatus(StrEnum):
    FREE = 'free'
    OCCUPIED = 'occupied'
    PENDING_FREE = 'pending_free'


class Table(BaseModel):
    id: str
    name: str
    capacity: int
    status: TableStatus
    occupied_by_guest_id: str | None = None


class WaitlistGuest(BaseModel):
    id: str
    token: str
    name: str
    party_size: int = Field(ge=1)
    phone: str
    notes: str = ''
    status: GuestStatus
    created_at: datetime
    estimated_wait_minutes: int
    assigned_table_id: str | None = None


class AddGuestRequest(BaseModel):
    name: str
    party_size: int = Field(ge=1)
    phone: str
    notes: str = ''


class DailyStats(BaseModel):
    total_seated: int
    total_no_show: int
    average_wait_minutes: int
