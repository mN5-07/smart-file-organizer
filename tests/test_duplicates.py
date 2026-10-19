from filecleaner.duplicates import find_duplicates
from filecleaner.scanner import scan_directory

def test_find_duplicates_identifies_duplicates(tmp_path):
    # Create two identical files
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    content = "Duplicate content"
    file1.write_text(content, encoding="utf-8")
    file2.write_text(content, encoding="utf-8")

    # Create a unique file
    unique_file = tmp_path / "unique.txt"
    unique_file.write_text("Unique content", encoding="utf-8")

    # Scan the directory to get file details
    file_list = scan_directory(str(tmp_path))

    # Find duplicates
    duplicates = find_duplicates(file_list)

    # There should be one entry in duplicates with two files
    assert len(duplicates) == 1
    duplicate_files = list(duplicates.values())[0]
    assert set(duplicate_files) == {str(file1), str(file2)}