"""Tool package. Importing this module registers every MVP tool into the registry."""
from __future__ import annotations

from app.tools.registry import registry  # noqa: F401

from app.tools import (  # noqa: F401,E402
    browser_read_page,
    create_document,
    draft_email,
    generate_social_post,
    knowledgebase,
    myska,
    novacore,
    open_application,
    open_website,
    pc_status,
    read_text_file,
    search_files,
)

__all__ = ["registry"]
