"""Structured, rotating file + console logging.

Never log secrets: API keys, tokens, passwords, or raw audio bytes.
Callers should pass already-sanitised messages.
"""
from __future__ import annotations

import logging
import re
from logging.handlers import RotatingFileHandler

from app.config import get_settings

_SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key\s*[:=]\s*)([^\s'\"]+)", re.IGNORECASE),
    re.compile(r"(voice[_-]?id\s*[:=]\s*)([^\s'\"]+)", re.IGNORECASE),
    re.compile(r"(authorization:\s*bearer\s+)([^\s'\"]+)", re.IGNORECASE),
    re.compile(r"(password\s*[:=]\s*)([^\s'\"]+)", re.IGNORECASE),
]


def redact(message: str) -> str:
    redacted = message
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub(lambda m: m.group(1) + "***REDACTED***", redacted)
    return redacted


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = redact(str(record.getMessage()))
            record.args = ()
        except Exception:
            pass
        return True


_configured = False


def configure_logging() -> logging.Logger:
    global _configured
    logger = logging.getLogger("riva")
    if _configured:
        return logger

    settings = get_settings()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.addFilter(RedactingFilter())
    logger.addHandler(console)

    log_file = settings.logs_directory / "riva.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RedactingFilter())
    logger.addHandler(file_handler)

    _configured = True
    return logger


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(f"riva.{name}")
