"""Database connection setup (SQLAlchemy)."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Parent class for all database tables (models)."""


_url = get_settings().database_url
# connect_timeout: if the DB is down, fail in 3s instead of hanging (keeps /ready fast for Kubernetes probes)
_connect_args = {"connect_timeout": 3} if _url.startswith("postgresql") else {}

# pool_pre_ping: test connections before use, so a DB restart doesn't break the app
engine = create_engine(_url, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Give each API request its own DB session, and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
