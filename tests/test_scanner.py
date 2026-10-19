import os
from datetime import datetime

import pytest

from filecleaner.scanner import scan_directory


def test_scan_directory_returns_file_details(tmp_path):
    file_path = tmp_path / "report.txt"
    file_path.write_text("Hello world", encoding="utf-8")

    results = scan_directory(str(tmp_path))

    assert len(results) == 1

    result = results[0]

    assert result["path"] == str(file_path)
    assert result["filename"] == "report.txt"
    assert result["size"] == len("Hello world")
    assert result["extension"] == ".txt"
    assert isinstance(result["modification_time"], datetime)


def test_scan_directory_returns_empty_list_for_empty_directory(tmp_path):
    assert scan_directory(str(tmp_path)) == []


def test_scan_directory_does_not_recurse_by_default(tmp_path):
    subdirectory = tmp_path / "subfolder"
    subdirectory.mkdir()
    (subdirectory / "nested.txt").write_text("Nested", encoding="utf-8")
    (tmp_path / "top.txt").write_text("Top", encoding="utf-8")

    results = scan_directory(str(tmp_path))

    assert [item["filename"] for item in results] == ["top.txt"]


def test_scan_directory_can_recurse(tmp_path):
    subdirectory = tmp_path / "subfolder"
    subdirectory.mkdir()
    nested_file = subdirectory / "nested.txt"
    nested_file.write_text("Nested", encoding="utf-8")

    results = scan_directory(str(tmp_path), recursive=True)

    assert len(results) == 1
    assert results[0]["filename"] == "nested.txt"
    assert results[0]["path"] == str(nested_file)


def test_scan_directory_normalizes_extension_to_lowercase(tmp_path):
    (tmp_path / "REPORT.PDF").write_text("PDF", encoding="utf-8")

    results = scan_directory(str(tmp_path))

    assert results[0]["extension"] == ".pdf"


def test_scan_directory_ignores_subdirectories(tmp_path):
    (tmp_path / "folder").mkdir()

    results = scan_directory(str(tmp_path))

    assert results == []


def test_scan_directory_rejects_empty_path():
    with pytest.raises(ValueError, match="cannot be empty"):
        scan_directory("")


def test_scan_directory_rejects_non_string_path():
    with pytest.raises(TypeError, match="must be a string"):
        scan_directory(None)


def test_scan_directory_rejects_non_boolean_recursive_option(tmp_path):
    with pytest.raises(TypeError, match="recursive must be a boolean"):
        scan_directory(str(tmp_path), recursive="yes")


def test_scan_directory_rejects_missing_directory(tmp_path):
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError, match="Directory does not exist"):
        scan_directory(str(missing))


def test_scan_directory_rejects_file_path(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")

    with pytest.raises(NotADirectoryError, match="Path is not a directory"):
        scan_directory(str(file_path))


def test_scan_directory_does_not_modify_files(tmp_path):
    file_path = tmp_path / "important.txt"
    original_content = "Do not change this file"
    file_path.write_text(original_content, encoding="utf-8")

    scan_directory(str(tmp_path))

    assert file_path.read_text(encoding="utf-8") == original_content
    assert file_path.exists()