"""URL validation: only http/https URLs are allowed, dangerous schemes are blocked."""
from __future__ import annotations

from urllib.parse import urlparse

_BLOCKED_SCHEMES = {"file", "javascript", "data", "vbscript", "about", "chrome", "ms-appx"}
_ALLOWED_SCHEMES = {"http", "https"}


class UrlSecurityError(Exception):
    pass


def validate_url(raw_url: str, trusted_domains: list[str] | None = None) -> str:
    if not raw_url or not raw_url.strip():
        raise UrlSecurityError("No URL was provided.")

    raw_url = raw_url.strip()
    parsed = urlparse(raw_url)

    scheme = (parsed.scheme or "").lower()
    if scheme in _BLOCKED_SCHEMES:
        raise UrlSecurityError(f"The '{scheme}' scheme is not permitted.")
    if scheme not in _ALLOWED_SCHEMES:
        raise UrlSecurityError("Only http:// and https:// links are permitted.")
    if not parsed.netloc:
        raise UrlSecurityError("The URL is missing a valid host.")
    if raw_url.lower().endswith((".exe", ".bat", ".cmd", ".ps1", ".msi", ".scr")):
        raise UrlSecurityError("Links to executable files are not permitted.")

    if trusted_domains:
        host = parsed.hostname or ""
        if not any(host == d or host.endswith(f".{d}") for d in trusted_domains):
            raise UrlSecurityError(
                f"'{host}' is not in the trusted domain list. Ask an administrator to approve it."
            )

    return raw_url
