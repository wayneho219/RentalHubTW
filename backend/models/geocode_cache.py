from datetime import datetime
from sqlalchemy import String, Numeric, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class GeocodeCache(Base):
    __tablename__ = "geocode_cache"

    address_text: Mapped[str] = mapped_column(Text, primary_key=True)
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    confidence: Mapped[float | None] = mapped_column(Numeric(3, 2))
    source: Mapped[str | None] = mapped_column(String(20))  # google / ntpc_open_data
    cached_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
