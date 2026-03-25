"""
Duomenų bazės konfigūracija ir sesijos valdymas.
Palaiko SQLite (dev) ir PostgreSQL (produkcija).
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from config import settings


_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Engine konfigūracija priklausomai nuo DB tipo
if _is_sqlite:
    from sqlalchemy import event

    # SQLite WAL mode for concurrent reads/writes
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )
    event.listen(engine.sync_engine, "connect", _set_sqlite_pragma)

else:
    # PostgreSQL — su connection pool
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )


# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# Base class for models
class Base(DeclarativeBase):
    """Bazinė klasė visiems modeliams."""


async def init_db() -> None:
    """
    Inicializuoti duomenų bazę.
    Sukuria visas lenteles jei neegzistuoja.
    """
    async with engine.begin() as conn:
        # Import all models to register them
        from models import problem_bank  # BP 2022 uždavinių bankas
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection duomenų bazės sesijai.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
