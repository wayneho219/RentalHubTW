from datetime import datetime
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography
from .base import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int | None] = mapped_column(Integer)
    price_type: Mapped[str | None] = mapped_column(String(10))       # 月租 / 季租
    size_ping: Mapped[float | None] = mapped_column(Numeric(5, 1))
    room_type: Mapped[str | None] = mapped_column(String(10))        # 套房 / 雅房 / 整層
    address: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(String(20))
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7))
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7))
    location: Mapped[object | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )
    pet_allowed: Mapped[bool | None] = mapped_column(Boolean)
    parking: Mapped[bool | None] = mapped_column(Boolean)
    balcony: Mapped[bool | None] = mapped_column(Boolean)
    internet: Mapped[bool | None] = mapped_column(Boolean)
    has_elevator: Mapped[bool | None] = mapped_column(Boolean)
    floor: Mapped[int | None] = mapped_column(SmallInteger)
    total_floors: Mapped[int | None] = mapped_column(SmallInteger)
    rental_subsidy: Mapped[str | None] = mapped_column(String(10))   # yes / no / unknown
    water_billing: Mapped[str | None] = mapped_column(String(20))    # fixed / taiwan_water / unknown
    electric_billing: Mapped[str | None] = mapped_column(String(20)) # fixed / taiwan_power / unknown
    contact_name: Mapped[str | None] = mapped_column(Text)
    contact_phone: Mapped[str | None] = mapped_column(Text)
    contact_method: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_group: Mapped[str | None] = mapped_column(Text)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(10), default="active")
