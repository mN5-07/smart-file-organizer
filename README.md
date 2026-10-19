
# Smart File Organizer

A Python command-line tool for organizing files by type and identifying duplicate files.

## Features

- Organize files into categories based on their extensions.
- Preview planned file movements using dry-run mode.
- Scan directories and collect file information.
- Identify duplicate files by comparing their contents.
- Report skipped and failed file operations.
- Run automated tests with pytest.

## Project Structure

```text
smart-file-organizer/
├── filecleaner/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── duplicates.py
│   ├── organizer.py
│   └── scanner.py
├── tests/
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.10 or newer
- pip
- pytest for running tests

## Setup

Clone the repository or download the project, then open a terminal in the project directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project in editable mode with development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

## Usage

### Preview file organization

Preview how files in a directory would be organized without moving them:

```powershell
python -m filecleaner.cli "$env:USERPROFILE\Downloads" --dry-run
```

### Organize files

When you are satisfied with the preview, run the organizer without `--dry-run`:

```powershell
python -m filecleaner.cli "$env:USERPROFILE\Downloads"
```

**Warning:** This command can move files. Review the dry-run results before running it without `--dry-run`.

### Scan directories

The scanner can be used from Python:

```python
from filecleaner.scanner import scan_directory

files = scan_directory(r"C:\Users\admin\Downloads")

for file_info in files:
    print(file_info)
```

By default, scanning is limited to the specified directory. To include subdirectories:

```python
files = scan_directory(
    r"C:\Users\admin\Downloads",
    recursive=True,
)
```

### Find duplicate files

The duplicate finder can be used from Python:

```python
from filecleaner.scanner import scan_directory
from filecleaner.duplicates import find_duplicates

files = scan_directory(r"C:\Users\admin\Downloads")
duplicates = find_duplicates(files)

for file_hash, paths in duplicates.items():
    print(f"Duplicate group ({file_hash}):")
    for path in paths:
        print(f"  {path}")
```

The duplicate finder reports matching files. It does not delete them.

## Running Tests

Run the complete test suite:

```powershell
python -m pytest -v
```

Run tests for a specific component:

```powershell
python -m pytest tests/test_scanner.py -v
python -m pytest tests/test_duplicates.py -v
python -m pytest tests/test_organizer.py -v
python -m pytest tests/test_cli.py -v
```

## Safety

- Use dry-run mode to preview file organization.
- Review the planned changes before performing actual moves.
- Duplicate detection is report-only; it does not remove files.
- Keep backups of important files.

## Current Status

The project includes directory scanning, duplicate detection, file organization, a command-line interface, and automated tests. CLI integration and packaging should be verified as development continues.

## License

See the `LICENSE` file for licensing terms.

```

```
