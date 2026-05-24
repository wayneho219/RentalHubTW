from sqlalchemy.ext.asyncio import AsyncEngine
from models.base import engine
from models.listing import Listing

def test_engine_is_created():
    assert isinstance(engine, AsyncEngine)

def test_listing_tablename():
    assert Listing.__tablename__ == "listings"

def test_listing_has_location_column():
    assert hasattr(Listing, "location")

def test_listing_has_required_billing_columns():
    assert hasattr(Listing, "water_billing")
    assert hasattr(Listing, "electric_billing")
    assert hasattr(Listing, "rental_subsidy")
