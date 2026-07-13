"""search_knowledgebase: full-text search over approved Nova Tech knowledge documents.

Uses SQLite FTS5. The index is built from files under knowledge/<category>/
and can be rebuilt on demand via reindex_knowledge_base() (exposed through
POST /knowledge/reindex and the settings page).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from pydantic import BaseModel, Field

from app.database.db import get_raw_connection
from app.logging_config import get_logger
from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolResult

logger = get_logger("knowledgebase")

INDEXABLE_EXTENSIONS = {".txt", ".md"}
KNOWLEDGE_CATEGORIES = ["nova-tech", "myska-pay", "novacore", "procedures"]


def reindex_knowledge_base(knowledge_root: Path) -> int:
    conn = get_raw_connection()
    indexed = 0
    try:
        conn.execute("DELETE FROM knowledge_fts")
        for category in KNOWLEDGE_CATEGORIES:
            category_dir = knowledge_root / category
            if not category_dir.exists():
                continue
            for path in category_dir.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in INDEXABLE_EXTENSIONS:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                title = path.stem.replace("-", " ").replace("_", " ").title()
                conn.execute(
                    "INSERT INTO knowledge_fts (content, title, category, file_path) VALUES (?, ?, ?, ?)",
                    (text, title, category, str(path)),
                )
                indexed += 1
        conn.commit()
    finally:
        conn.close()
    logger.info("Knowledgebase reindexed: %s documents", indexed)
    return indexed


def search_knowledge_base(query: str, limit: int = 8) -> list[dict]:
    conn = get_raw_connection()
    try:
        cursor = conn.execute(
            "SELECT title, category, file_path, snippet(knowledge_fts, 0, '[', ']', '...', 24) "
            "FROM knowledge_fts WHERE knowledge_fts MATCH ? LIMIT ?",
            (_fts_query(query), limit),
        )
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()

    return [
        {"title": r[0], "category": r[1], "file_path": r[2], "excerpt": r[3]}
        for r in rows
    ]


def _fts_query(query: str) -> str:
    # Wrap each term for a permissive prefix match, avoiding FTS5 syntax errors.
    terms = [t.strip().replace('"', "") for t in query.split() if t.strip()]
    if not terms:
        return '""'
    return " OR ".join(f'"{t}"*' for t in terms)


class SearchKnowledgebaseInput(BaseModel):
    query: str = Field(..., description="Search text for Nova Tech's approved knowledge documents.")


async def handle_search_knowledgebase(args: SearchKnowledgebaseInput, ctx: ToolContext) -> ToolResult:
    results = search_knowledge_base(args.query)
    if not results:
        return ToolResult(success=True, data={"results": []}, message="No knowledgebase matches found.")
    return ToolResult(
        success=True, data={"results": results}, message=f"Found {len(results)} knowledgebase match(es)."
    )


registry.register(
    ToolDefinition(
        name="search_knowledgebase",
        description=(
            "Search Nova Tech's approved knowledgebase (company info, MYSKA Pay, NovaCore, procedures)."
        ),
        input_model=SearchKnowledgebaseInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_search_knowledgebase,
    )
)
