import os

import pytest

from filecleaner.organizer import move_files, type_check, placement


# -------------------------
# type_check tests
# -------------------------

@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        # Images
        ("vacation.jpg", "Images"),
        ("photo.jpeg", "Images"),
        ("photo.png", "Images"),
        ("animation.gif", "Images"),
        ("graphic.svg", "Images"),
        # Documents
        ("report.pdf", "Documents"),
        ("document.docx", "Documents"),
        ("notes.txt", "Documents"),
        # Spreadsheets
        ("data.xlsx", "Spreadsheets"),
        ("data.csv", "Spreadsheets"),
        # Presentations
        ("presentation.pptx", "Presentations"),
        ("presentation.ppt", "Presentations"),
        # Videos
        ("movie.mp4", "Videos"),
        ("movie.mov", "Videos"),
        # Audio
        ("song.mp3", "Audio"),
        ("sound.wav", "Audio"),
        # Archives
        ("archive.zip", "Archives"),
        ("archive.7z", "Archives"),
        # Applications
        ("program.exe", "Applications"),
        ("installer.msi", "Applications"),
        ("script.bat", "Applications"),
        # Code
        ("script.py", "Code"),
        ("app.js", "Code"),
        ("program.cpp", "Code"),
        ("config.json", "Code"),
        # Unknown extensions
        ("mystery.xyz", "Other"),
        ("database.db", "Other"),
    ],
)
def test_type_check_categories(filename, expected):
    assert type_check(filename) == expected


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("PHOTO.PNG", "Images"),
        ("DOCUMENT.PDF", "Documents"),
        ("ARCHIVE.ZIP", "Archives"),
        ("MOVIE.MP4", "Videos"),
        ("SONG.MP3", "Audio"),
        ("SCRIPT.PY", "Code"),
    ],
)
def test_type_check_uppercase_extensions(filename, expected):
    assert type_check(filename) == expected


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("/path/to/vacation.jpg", "Images"),
        ("/another/path/report.pdf", "Documents"),
        ("folder/subfolder/script.py", "Code"),
        (r"C:\Users\Example\photo.png", "Images"),
    ],
)
def test_type_check_paths(filename, expected):
    assert type_check(filename) == expected


@pytest.mark.parametrize(
    "filename",
    ["README", "LICENSE", "Makefile"],
)
def test_type_check_without_extension(filename):
    assert type_check(filename) == "Other"


def test_type_check_hidden_files():
    assert type_check(".hiddenfile.txt") == "Documents"
    assert type_check(".photo.jpg") == "Images"


def test_type_check_hidden_file_without_extension():
    assert type_check(".gitignore") == "Other"


def test_type_check_empty_string():
    assert type_check("") == "Other"


def test_type_check_none_raises_type_error():
    with pytest.raises(TypeError):
        type_check(None)


# -------------------------
# placement tests
# -------------------------

def create_sample_files(directory):
    filenames = [
        "vacation.jpg",
        "resort.png",
        "report.pdf",
        "document.docx",
        "archive.7z",
        "archive.zip",
        "movie.mp4",
        "movie.mov",
        "song.mp3",
        "sound.wav",
        "program.exe",
        "automate.bat",
        "script.py",
        "program.cpp",
        "data.csv",
        "hospital.xlsx",
        "presentation.pptx",
        "mystery.xyz",
    ]

    for filename in filenames:
        (directory / filename).touch()

    return filenames


def test_placement_returns_expected_categories(tmp_path):
    create_sample_files(tmp_path)

    result = placement(str(tmp_path))

    expected_categories = {
        "Images",
        "Documents",
        "Archives",
        "Videos",
        "Audio",
        "Applications",
        "Code",
        "Spreadsheets",
        "Presentations",
        "Other",
    }

    assert set(result) == expected_categories


def test_placement_returns_correct_source_paths(tmp_path):
    create_sample_files(tmp_path)

    result = placement(str(tmp_path))

    for category, files in result.items():
        for file_info in files:
            source = file_info["source"]

            assert os.path.isfile(source)
            assert os.path.dirname(source) == str(tmp_path)
            assert type_check(os.path.basename(source)) == category


def test_placement_returns_correct_destination_paths(tmp_path):
    create_sample_files(tmp_path)

    result = placement(str(tmp_path))

    for category, files in result.items():
        for file_info in files:
            expected_destination = os.path.join(
                str(tmp_path),
                category,
                os.path.basename(file_info["source"]),
            )

            assert file_info["destination"] == expected_destination


def test_placement_multiple_files_share_category(tmp_path):
    (tmp_path / "vacation.jpg").touch()
    (tmp_path / "resort.png").touch()
    (tmp_path / "report.pdf").touch()

    result = placement(str(tmp_path))

    images = result["Images"]

    assert len(images) == 2
    assert {item["source"] for item in images} == {
        str(tmp_path / "vacation.jpg"),
        str(tmp_path / "resort.png"),
    }

    assert {
        item["destination"] for item in images
    } == {
        os.path.join(str(tmp_path), "Images", "vacation.jpg"),
        os.path.join(str(tmp_path), "Images", "resort.png"),
    }


def test_placement_unknown_extension_goes_to_other(tmp_path):
    unknown = tmp_path / "mystery.xyz"
    unknown.touch()

    result = placement(str(tmp_path))

    assert result["Other"] == [
        {
            "source": str(unknown),
            "destination": os.path.join(
                str(tmp_path), "Other", "mystery.xyz"
            ),
        }
    ]


def test_placement_empty_directory(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    assert placement(str(empty_dir)) == {}


def test_placement_nonexistent_directory_raises(tmp_path):
    missing_dir = tmp_path / "does_not_exist"

    with pytest.raises(NotADirectoryError):
        placement(str(missing_dir))


def test_placement_file_instead_of_directory_raises(tmp_path):
    file_path = tmp_path / "report.pdf"
    file_path.touch()

    with pytest.raises(NotADirectoryError):
        placement(str(file_path))


@pytest.mark.parametrize("filepath", ["", "   "])
def test_placement_empty_path_raises(filepath):
    with pytest.raises(ValueError):
        placement(filepath)


@pytest.mark.parametrize("filepath", [None, 123, 1.5])
def test_placement_non_string_path_raises(filepath):
    with pytest.raises(TypeError):
        placement(filepath)


def test_placement_ignores_subdirectories(tmp_path):
    top_level = tmp_path / "top_level.jpg"
    top_level.touch()

    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()

    nested_file = nested_dir / "nested.pdf"
    nested_file.touch()

    result = placement(str(tmp_path))

    all_sources = {
        item["source"]
        for files in result.values()
        for item in files
    }

    assert str(top_level) in all_sources
    assert str(nested_file) not in all_sources


def test_placement_does_not_move_files(tmp_path):
    filenames = create_sample_files(tmp_path)
    original_paths = {
        tmp_path / filename for filename in filenames
    }

    placement(str(tmp_path))

    for path in original_paths:
        assert path.is_file()


def test_placement_does_not_create_destination_directories(tmp_path):
    create_sample_files(tmp_path)

    original_entries = set(tmp_path.iterdir())

    placement(str(tmp_path))

    assert set(tmp_path.iterdir()) == original_entries


def test_placement_source_and_destination_are_distinct(tmp_path):
    (tmp_path / "vacation.jpg").touch()

    result = placement(str(tmp_path))
    file_info = result["Images"][0]

    assert file_info["source"] != file_info["destination"]
    assert os.path.isfile(file_info["source"])
    assert not os.path.exists(file_info["destination"])


# -------------------------
# move_files tests
# -------------------------

from unittest.mock import patch


def test_move_files_moves_file_successfully(tmp_path):
    source = tmp_path / "vacation.jpg"
    destination = tmp_path / "Images" / "vacation.jpg"
    source.write_text("dummy content")

    plans = {
        "Images": [{
            "source": str(source),
            "destination": str(destination),
        }]
    }

    results = move_files(plans)

    assert not source.exists()
    assert destination.is_file()
    assert destination.read_text() == "dummy content"

    assert len(results["moved"]) == 1
    assert results["moved"][0]["source"] == str(source)
    assert results["moved"][0]["destination"] == str(destination)

    assert results["skipped"] == []
    assert results["failed"] == []
    assert results["dry_run"] is False

def test_move_files_source_equals_destination(tmp_path):
    source = tmp_path / "photo.jpg"
    source.write_text("image content")

    plans = {
        "Images": [{
            "source": str(source),
            "destination": str(source),
        }]
    }

    results = move_files(plans)

    assert source.is_file()
    assert results["moved"] == []
    assert len(results["skipped"]) == 1

def test_move_files_existing_destination_directory(tmp_path):
    source = tmp_path / "photo.jpg"
    destination_dir = tmp_path / "Images"
    destination_dir.mkdir()

    destination = destination_dir / "photo.jpg"
    source.write_text("image content")

    plans = {
        "Images": [{
            "source": str(source),
            "destination": str(destination),
        }]
    }

    results = move_files(plans)

    assert not source.exists()
    assert destination.read_text() == "image content"
    assert len(results["moved"]) == 1
    assert results["failed"] == []

def test_move_files_dry_run_does_not_change_filesystem(tmp_path):
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"

    source.write_text("Test content")

    plans = {
        "Documents": [
            {
                "source": str(source),
                "destination": str(destination),
            }
        ]
    }

    results = move_files(plans, dry_run=True)

    # The source remains untouched.
    assert source.is_file()
    assert source.read_text() == "Test content"

    # No destination file or directory is created.
    assert not destination.exists()
    assert not destination.parent.exists()

    # The result correctly identifies this as a dry run.
    assert results["dry_run"] is True
    assert results["moved"] == []
    assert results["skipped"] == []
    assert results["failed"] == []

    # The planned move is reported.
    assert len(results["planned"]) == 1
    assert results["planned"][0]["source"] == str(source)
    assert results["planned"][0]["destination"] == str(destination)


def test_move_files_source_disappears_after_planning(tmp_path):
    # Arrange: create two files to organize.
    report = tmp_path / "report.pdf"
    photo = tmp_path / "vacation.jpg"

    report.write_text("Report content")
    photo.write_text("Photo content")

    # Create the plan while both files exist.
    plans = placement(str(tmp_path))

    # Simulate the user deleting the report after planning.
    report.unlink()

    # Act: execute the now-outdated plan.
    results = move_files(plans)

    # Assert: the missing report is skipped.
    assert len(results["skipped"]) == 1
    assert results["skipped"][0]["source"] == str(report)
    assert results["skipped"][0]["reason"] == "Source file does not exist"

    # Assert: the photo is still moved successfully.
    photo_destination = tmp_path / "Images" / "vacation.jpg"

    assert len(results["moved"]) == 1
    assert results["moved"][0]["source"] == str(photo)
    assert results["moved"][0]["destination"] == str(photo_destination)
    assert photo_destination.read_text() == "Photo content"

    # Confirm the final filesystem state.
    assert not report.exists()
    assert not photo.exists()
    assert results["failed"] == []

def test_move_files_missing_source_is_skipped(tmp_path):
    source = tmp_path / "missing.txt"
    destination = tmp_path / "Documents" / "missing.txt"

    plans = {
        "Documents": [{
            "source": str(source),
            "destination": str(destination),
        }]
    }

    results = move_files(plans)

    assert len(results["skipped"]) == 1
    assert results["skipped"][0]["source"] == str(source)
    assert results["skipped"][0]["reason"] == (
        "Source file does not exist"
    )

    assert results["moved"] == []
    assert results["failed"] == []
    assert not destination.exists()


def test_move_files_existing_destination_is_skipped(tmp_path):
    source = tmp_path / "report.pdf"
    destination_dir = tmp_path / "Documents"
    destination_dir.mkdir()

    destination = destination_dir / "report.pdf"

    source.write_text("New report")
    destination.write_text("Existing report")

    plans = {
        "Documents": [{
            "source": str(source),
            "destination": str(destination),
        }]
    }

    results = move_files(plans)

    assert len(results["skipped"]) == 1
    assert results["skipped"][0]["reason"] == (
        "Destination already exists"
    )

    assert source.read_text() == "New report"
    assert destination.read_text() == "Existing report"

    assert results["moved"] == []
    assert results["failed"] == []


def test_move_files_permission_error_is_recorded(tmp_path):
    source = tmp_path / "report.pdf"
    destination = tmp_path / "Documents" / "report.pdf"
    source.write_text("Test content")

    plans = {
        "Documents": [{
            "source": str(source),
            "destination": str(destination),
        }]
    }

    with patch(
        "filecleaner.organizer.os.rename",
        side_effect=PermissionError("Permission denied"),
    ):
        results = move_files(plans)

    assert len(results["failed"]) == 1
    assert results["failed"][0]["source"] == str(source)
    assert results["failed"][0]["error_type"] == "PermissionError"
    assert "Permission denied" in results["failed"][0]["error"]

    assert results["moved"] == []
    assert results["skipped"] == []

    assert source.is_file()
    assert not destination.exists()


def test_move_files_continues_after_one_file_fails(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"

    first.write_text("First file")
    second.write_text("Second file")

    first_destination = tmp_path / "Documents" / "first.txt"
    second_destination = tmp_path / "Documents" / "second.txt"

    plans = {
        "Documents": [
            {
                "source": str(first),
                "destination": str(first_destination),
            },
            {
                "source": str(second),
                "destination": str(second_destination),
            },
        ]
    }

    real_rename = os.rename

    def rename_with_one_failure(src, dst):
        if src == str(first):
            raise PermissionError("Permission denied")

        return real_rename(src, dst)

    with patch(
        "filecleaner.organizer.os.rename",
        side_effect=rename_with_one_failure,
    ):
        results = move_files(plans)

    assert len(results["failed"]) == 1
    assert results["failed"][0]["source"] == str(first)

    assert len(results["moved"]) == 1
    assert results["moved"][0]["source"] == str(second)
    assert second_destination.is_file()

    assert first.is_file()
    assert not second.exists()
    assert results["skipped"] == []


# Add a test for destination-directory creation failures to ensure your error-handling requirements are covered.
def test_move_files_destination_creation_failure(tmp_path):
    source = tmp_path / "report.pdf"
    destination_dir = tmp_path / "Documents"
    destination = destination_dir / "report.pdf"

    source.write_text("Test content")

    plans = {
        "Documents": [{
            "source": str(source),
            "destination": str(destination),
        }]
    }

    with patch(
        "filecleaner.organizer.os.makedirs",
        side_effect=PermissionError("Permission denied"),
    ):
        results = move_files(plans)

    assert len(results["failed"]) == 1
    assert results["failed"][0]["source"] == str(source)
    assert results["failed"][0]["error_type"] == "PermissionError"
    assert "Permission denied" in results["failed"][0]["error"]

    assert results["moved"] == []
    assert results["skipped"] == []

    assert source.is_file()
    assert not destination.exists()


def test_placement_excludes_desktop_ini_and_includes_regular_files(
    tmp_path,
):
    # Create desktop.ini with different capitalization.
    desktop_ini = tmp_path / "desktop.ini"
    desktop_ini.touch()

    uppercase_desktop_ini = tmp_path / "DESKTOP.INI"
    uppercase_desktop_ini.touch()

    # Create a regular file that should be included.
    photo = tmp_path / "vacation.jpg"
    photo.touch()

    result = placement(str(tmp_path))

    all_sources = {
        item["source"]
        for files in result.values()
        for item in files
    }

    # Neither version of desktop.ini should be planned for movement.
    assert str(desktop_ini) not in all_sources
    assert str(uppercase_desktop_ini) not in all_sources

    # Regular files should still be included.
    assert str(photo) in all_sources
    assert type_check("vacation.jpg") == "Images"