from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.listing import Listing


class ListingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Listing:
        listing = Listing(**kwargs)
        self.session.add(listing)
        await self.session.commit()
        await self.session.refresh(listing)
        return listing

    async def get_by_id(self, listing_id: int) -> Listing | None:
        result = await self.session.execute(
            select(Listing).where(Listing.id == listing_id)
        )
        return result.scalar_one_or_none()

    async def upsert_by_source(self, post_id: str, **kwargs) -> tuple[Listing, bool]:
        """依 source_url 找已有房源，有則更新，無則新增。回傳 (listing, created)。"""
        result = await self.session.execute(
            select(Listing).where(Listing.source_url == kwargs.get("source_url"))
        )
        existing = result.scalar_one_or_none()
        if existing:
            for key, value in kwargs.items():
                setattr(existing, key, value)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing, False
        return await self.create(**kwargs), True
