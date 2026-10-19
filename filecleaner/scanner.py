# Scan directories and return file information without modifying files.

import os
from datetime import datetime
from typing import Any


def scan_directory(directory: str, recursive: bool = False) -> list[dict[str, Any]]:
    """
    Return information about files in a directory without changing them.

    Args:
        directory: Path to the directory to scan.
        recursive: If True, include files in subdirectories.

    Returns:
        A list of dictionaries containing file information:
        path, filename, size, extension, and modification_time.

    Raises:
        TypeError: If directory is not a string or recursive is not a bool.
        ValueError: If directory is empty or contains only whitespace.
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path is not a directory.
    """
    if not isinstance(directory, str):
        raise TypeError("directory must be a string")

    if not directory.strip():
        raise ValueError("directory cannot be empty")

    if not isinstance(recursive, bool):
        raise TypeError("recursive must be a boolean")

    directory = os.path.abspath(os.path.expanduser(directory))

    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    file_details = []

    def collect_error(error: OSError) -> None:
        """Ignore individual filesystem errors so scanning can continue."""
        pass

    if recursive:
        walker = os.walk(
            directory,
            followlinks=False,
            onerror=collect_error,
        )
    else:
        try:
            filenames = os.listdir(directory)
        except OSError:
            return []

        walker = [(directory, [], filenames)]

    for root, _, filenames in walker:
        for filename in filenames:
            file_path = os.path.join(root, filename)

            try:
                # Do not include directories or follow symbolic links.
                if os.path.islink(file_path) or not os.path.isfile(file_path):
                    continue

                file_stat = os.stat(file_path)

                file_info = {
                    "path": file_path,
                    "filename": filename,
                    "size": file_stat.st_size,
                    "extension": os.path.splitext(filename)[1].lower(),
                    "modification_time": datetime.fromtimestamp(
                        file_stat.st_mtime
                    ),
                }

                file_details.append(file_info)

            except (OSError, ValueError):
                # The file may have disappeared or become inaccessible.
                continue

    return file_details