"""Database engine/session setup and SQLite FTS5 knowledgebase index."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.database.models import Base

_engine = None
_SessionLocal: sessionmaker | None = None


def init_database() -> None:
    global _engine, _SessionLocal
    settings = get_settings()
    db_path = settings.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    _engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    _ensure_fts_table(db_path)


def _ensure_fts_table(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5("
            "content, title, category, file_path, tokenize='porter unicode61')"
        )
        conn.commit()
    finally:
        conn.close()


def get_engine():
    if _engine is None:
        init_database()
    return _engine


@contextmanager
def session_scope() -> Iterator[Session]:
    if _SessionLocal is None:
        init_database()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_raw_connection() -> sqlite3.Connection:
    settings = get_settings()
    if not settings.database_path.exists():
        init_database()
    return sqlite3.connect(settings.database_path)
