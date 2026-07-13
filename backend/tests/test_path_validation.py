import pytest

from app.security.path_validation import PathSecurityError, validate_new_file_path, validate_path_in_roots


def test_validate_path_inside_root_succeeds(tmp_path):
    inside_file = tmp_path / "notes.txt"
    inside_file.write_text("hello")
    resolved = validate_path_in_roots(str(inside_file), [tmp_path])
    assert resolved == inside_file.resolve()


def test_validate_path_rejects_traversal_outside_root(tmp_path):
    outside_dir = tmp_path.parent / "outside-secret"
    outside_dir.mkdir(exist_ok=True)
    traversal_path = tmp_path / ".." / "outside-secret" / "secret.txt"
    with pytest.raises(PathSecurityError):
        validate_path_in_roots(str(traversal_path), [tmp_path])


def test_validate_path_rejects_when_no_roots_configured(tmp_path):
    with pytest.raises(PathSecurityError):
        validate_path_in_roots(str(tmp_path / "file.txt"), [])


def test_validate_new_file_path_rejects_disallowed_extension(tmp_path):
    with pytest.raises(PathSecurityError):
        validate_new_file_path(str(tmp_path / "script.exe"), [tmp_path], [".txt", ".md"])


def test_validate_new_file_path_accepts_allowed_extension(tmp_path):
    resolved = validate_new_file_path(str(tmp_path / "doc.md"), [tmp_path], [".txt", ".md"])
    assert resolved.suffix == ".md"
