from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TableRow(Base):
    __tablename__ = 'tables'

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    capacity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default='free')
    occupied_by_guest_id: Mapped[str | None] = mapped_column(String, nullable=True)


class GuestRow(Base):
    __tablename__ = 'guests'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    party_size: Mapped[int] = mapped_column(Integer)
    phone: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String, default='')
    status: Mapped[str] = mapped_column(String, default='waiting')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estimated_wait_minutes: Mapped[int] = mapped_column(Integer)
    assigned_table_id: Mapped[str | None] = mapped_column(String, nullable=True)


class StatsRow(Base):
    __tablename__ = 'stats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    average_wait_minutes: Mapped[int] = mapped_column(Integer, default=15)
    total_seated: Mapped[int] = mapped_column(Integer, default=0)
    total_no_show: Mapped[int] = mapped_column(Integer, default=0)
