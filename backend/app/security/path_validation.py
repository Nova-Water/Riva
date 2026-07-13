"""Path validation utilities that prevent directory traversal and restrict
file access to approved root folders.
"""
from __future__ import annotations

from pathlib import Path
from typing import List


class PathSecurityError(Exception):
    """Raised when a requested path is outside approved roots or otherwise unsafe."""


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def is_within_roots(candidate: Path, roots: List[Path]) -> bool:
    resolved = _resolve(candidate)
    for root in roots:
        resolved_root = _resolve(root)
        try:
            resolved.relative_to(resolved_root)
            return True
        except ValueError:
            continue
    return False


def validate_path_in_roots(raw_path: str, roots: List[Path]) -> Path:
    """Resolve `raw_path` and ensure it lives inside one of `roots`.

    Raises PathSecurityError if the path escapes every approved root,
    contains no allowed roots, or otherwise cannot be safely resolved.
    """
    if not raw_path or not raw_path.strip():
        raise PathSecurityError("No path was provided.")

    if not roots:
        raise PathSecurityError("No approved file roots are configured.")

    candidate = Path(raw_path)
    resolved = _resolve(candidate)

    if not is_within_roots(resolved, roots):
        raise PathSecurityError(
            "The requested path is outside the approved folders."
        )

    return resolved


def validate_new_file_path(raw_path: str, roots: List[Path], allowed_extensions: List[str]) -> Path:
    """Validate a path intended for a *new* file (used by create_document)."""
    resolved = validate_path_in_roots(raw_path, roots)
    if resolved.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
        raise PathSecurityError(
            f"File type '{resolved.suffix}' is not permitted for this operation."
        )
    return resolved
