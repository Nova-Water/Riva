"""In-memory pending confirmation store for amber/red permission tools.

Approvals expire after a fixed window so a stale confirmation cannot be
replayed later.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, Optional

CONFIRMATION_TTL_SECONDS = 120


@dataclass
class PendingConfirmation:
    confirmation_id: str
    conversation_id: str
    tool_name: str
    arguments: Dict[str, Any]
    confirmation_message: str
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > CONFIRMATION_TTL_SECONDS


class ConfirmationStore:
    def __init__(self) -> None:
        self._pending: Dict[str, PendingConfirmation] = {}
        self._lock = Lock()

    def create(
        self, conversation_id: str, tool_name: str, arguments: Dict[str, Any], message: str
    ) -> PendingConfirmation:
        with self._lock:
            self._purge_expired()
            confirmation_id = str(uuid.uuid4())
            pending = PendingConfirmation(
                confirmation_id=confirmation_id,
                conversation_id=conversation_id,
                tool_name=tool_name,
                arguments=arguments,
                confirmation_message=message,
            )
            self._pending[confirmation_id] = pending
            return pending

    def pop(self, confirmation_id: str) -> Optional[PendingConfirmation]:
        with self._lock:
            self._purge_expired()
            return self._pending.pop(confirmation_id, None)

    def peek(self, confirmation_id: str) -> Optional[PendingConfirmation]:
        with self._lock:
            self._purge_expired()
            return self._pending.get(confirmation_id)

    def _purge_expired(self) -> None:
        expired = [cid for cid, p in self._pending.items() if p.is_expired()]
        for cid in expired:
            del self._pending[cid]


confirmation_store = ConfirmationStore()
