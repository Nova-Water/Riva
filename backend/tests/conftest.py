"""Test bootstrap: isolate RIVA's data directory before any app module is imported."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

_TEST_DATA_DIR = tempfile.mkdtemp(prefix="riva-test-")
os.environ["RIVA_DATA_DIRECTORY"] = _TEST_DATA_DIR
os.environ.setdefault("APP_NAME", "RIVA AI")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("RIVA_ALLOWED_FILE_ROOTS", "")
os.environ.setdefault("RIVA_ALLOWED_APPLICATIONS", "")
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("LLM_MODEL", "")
os.environ.setdefault("VOICE_API_KEY", "")
os.environ.setdefault("VOICE_ID", "")

import pytest  # noqa: E402

from app.database.db import init_database  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _init_test_database():
    init_database()
    yield
