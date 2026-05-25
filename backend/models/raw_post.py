from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class RawPost(Base):
    __tablename__ = "raw_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[str | None] = mapped_column(Text)
    post_id: Mapped[str | None] = mapped_column(Text, unique=True)
    raw_text: Mapped[str | None] = mapped_column(Text)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    parsed_listing_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("listings.id"), nullable=True
    )
    parse_status: Mapped[str | None] = mapped_column(String(20))
    # parse_status 可能的值:
    # success / geocode_failed / duplicate / rejected
