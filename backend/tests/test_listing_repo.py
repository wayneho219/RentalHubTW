import pytest
from datetime import datetime, timezone
from repository.listing_repo import ListingRepository
from models.listing import Listing


@pytest.mark.asyncio
async def test_create_listing(db_session):
    repo = ListingRepository(db_session)
    listing = await repo.create(
        title="大安區套房近捷運",
        price=18000,
        price_type="月租",
        room_type="套房",
        address="台北市大安區復興南路一段",
        district="大安區",
        status="active",
    )
    assert listing.id is not None
    assert listing.title == "大安區套房近捷運"
    assert listing.price == 18000


@pytest.mark.asyncio
async def test_get_listing_by_id(db_session):
    repo = ListingRepository(db_session)
    created = await repo.create(title="測試房源", price=15000, status="active")
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_get_listing_by_id_not_found(db_session):
    repo = ListingRepository(db_session)
    result = await repo.get_by_id(99999)
    assert result is None
