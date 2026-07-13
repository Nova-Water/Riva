import pytest

from app.security.url_validation import UrlSecurityError, validate_url


def test_validate_url_allows_https():
    assert validate_url("https://novatech.example.com/services") == "https://novatech.example.com/services"


def test_validate_url_rejects_file_scheme():
    with pytest.raises(UrlSecurityError):
        validate_url("file:///etc/passwd")


def test_validate_url_rejects_javascript_scheme():
    with pytest.raises(UrlSecurityError):
        validate_url("javascript:alert(1)")


def test_validate_url_rejects_data_scheme():
    with pytest.raises(UrlSecurityError):
        validate_url("data:text/html,<script>alert(1)</script>")


def test_validate_url_rejects_executable_link():
    with pytest.raises(UrlSecurityError):
        validate_url("https://example.com/download/setup.exe")


def test_validate_url_enforces_trusted_domains():
    with pytest.raises(UrlSecurityError):
        validate_url("https://untrusted.example.com", trusted_domains=["novatech.example.com"])
    assert validate_url("https://novatech.example.com", trusted_domains=["novatech.example.com"])
