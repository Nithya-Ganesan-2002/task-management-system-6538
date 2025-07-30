"""Database utilities for engine/session creation."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import os

# Use environment variables for database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# PUBLIC_INTERFACE
async def get_db():
    """Yields a database session."""
    async with AsyncSessionLocal() as session:
        yield session
