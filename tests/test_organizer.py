import os

import pytest

from filecleaner.organizer import type_check, placement


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