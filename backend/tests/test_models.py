from sqlalchemy.ext.asyncio import AsyncEngine
from models.base import engine

def test_engine_is_created():
    assert isinstance(engine, AsyncEngine)
