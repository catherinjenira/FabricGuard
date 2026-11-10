"""
Database connection and session management for FabricGuard-AI.
Configured with MySQL async engine, connection pooling, and automated schema creation.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

db_url = settings.get_database_url()

# Connection pooling configurations for MySQL
engine_kwargs = {
    "echo": False,
    "future": True,
}

if "mysql" in db_url:
    engine_kwargs.update({
        "pool_recycle": 3600,
        "pool_size": 10,
        "max_overflow": 20,
    })

engine = create_async_engine(
    db_url,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initializes database tables in MySQL."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(f"[✓] MySQL Database schema verified & tables ready in {settings.MYSQL_DB}")
    except Exception as e:
        print(f"[!] Warning: Could not initialize database tables ({e}). Verify MySQL connection credentials.")
