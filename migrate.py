import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

from models import Base


DATABASE_URL = "postgresql+asyncpg://swapi_user:swapi_password@localhost:5432/swapi_db"


async def migrate():
    """Create database tables using SQLAlchemy async engine."""
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("Tables created successfully!")


if __name__ == "__main__":
    asyncio.run(migrate())
