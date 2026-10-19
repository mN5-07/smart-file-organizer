'''
# smart-file-organizer/filecleaner/organizer.py
Purpose: 
     The point of this file is to determine the logic at which the files will be organized. The logic is as follows:
     1. The user will provide a directory path to the program. 
     2. The program will then scan the directory and identify all files within it.
     3. The program will categorize the files based on their types or other criteria assuming the folders already exist. If not, they will be created.
Example input:
    vacation.jpg → Images
    report.pdf → Documents
    archive.zip → Archives
    movie.mp4 → Videos
    song.mp3 → Audio
    program.exe → Applications
    mystery.xyz → Other

TODO:
    Your current function handles an empty string by returning "Other".
    But what happens if someone passes None instead?
    Consider these two inputs:
    Input	Meaning
    mystery.xyz	A valid filename with an unknown extension
    None	No filename was provided


    Should they produce the same result?
    For this project, I'd lean toward raising a clear exception for invalid input while continuing to return "Other" for valid filenames with unknown extensions.
    However, that's a design decision. The important thing is to make the behavior intentional and test it.
'''
import os

# Maps file extensions to their categories for faster lookups.
EXTENSION_MAPPING = {
    '.jpg': 'Images',
    '.jpeg': 'Images',
    '.png': 'Images',
    '.gif': 'Images',
    '.bmp': 'Images',
    '.svg': 'Images',
    '.webp': 'Images',
    '.heic': 'Images',

    '.pdf': 'Documents',
    '.docx': 'Documents',
    '.doc': 'Documents',
    '.txt': 'Documents',
    '.rtf': 'Documents',
    '.odt': 'Documents',
    '.md': 'Documents',
    '.markdown': 'Documents',

    '.xlsx': 'Spreadsheets',
    '.xls': 'Spreadsheets',
    '.csv': 'Spreadsheets',

    '.pptx': 'Presentations',
    '.ppt': 'Presentations',

    '.mp4': 'Videos',
    '.mov': 'Videos',
    '.avi': 'Videos',
    '.mkv': 'Videos',
    '.webm': 'Videos',

    '.mp3': 'Audio',
    '.wav': 'Audio',
    '.aac': 'Audio',
    '.flac': 'Audio',
    '.m4a': 'Audio',

    '.zip': 'Archives',
    '.rar': 'Archives',
    '.7z': 'Archives',
    '.tar': 'Archives',
    '.gz': 'Archives',

    '.exe': 'Applications',
    '.msi': 'Applications',
    '.bat': 'Applications',

    '.py': 'Code',
    '.js': 'Code',
    '.html': 'Code',
    '.css': 'Code',
    '.java': 'Code',
    '.cpp': 'Code',
    '.json': 'Code',
    '.ipynb': 'Code',
    '.ipynb_checkpoints': 'Code',
}

# Run basic unit tests to verify the functionality of the type_check function then go back and deal with edge cases and other scenarios.
def type_check(filename):
    '''
    This function takes a filename as input and returns the category of the file based on its extension as a string.
    If the extension is not recognized, it returns 'Other'.

    Preconditions:
        - The input filename is a string.
        - The filename may or may not include a path.
        - The filename may or may not have an extension.
    Postconditions:
        - The function returns a string representing the category of the file.
        - If the extension is not recognized, it returns 'Other'.
    '''

    if not isinstance(filename, str):
        raise TypeError("filename must be a string")

    if not filename:
        return "Other"

    # Handle both Windows and Unix-style paths.
    filename = os.path.basename(filename.replace("\\", "/"))

    # Handle hidden files such as .hiddenfile.txt.
    _, ext = os.path.splitext(filename)

    return EXTENSION_MAPPING.get(ext.lower(), "Other")


def placement(filepath):
    # Python's pathlib.Path is designed specifically for working with filesystem paths. It can make path manipulation more expressive and reduce the need to manually combine path strings
    '''
    Purpose: accepts a directory path and determines where its files should go
    Preconditions:
        - The input filepath is a string representing a valid directory path.
        - The directory may contain files of various types.
    Postconditions:
        - The function returns a dictionary where keys are file categories and values are lists of file paths that belong to those categories.
        - If the directory is empty or contains no files, it returns an empty dictionary.
    '''
    # Easy edge cases
    if not isinstance(filepath, str):
        raise TypeError("The provided filepath must be a string.")
    if not filepath.strip():
        raise ValueError("The provided filepath cannot be empty or whitespace.")
    if not os.path.isdir(filepath):
        raise NotADirectoryError(f"The provided path '{filepath}' is not a valid directory.")

    file_categories = {}
    directory_path = filepath

    # Identify files in the directory (don't recurse into subdirectories for now)
    directory_contents = os.listdir(directory_path)
    for item in directory_contents:
        if item.lower() == "desktop.ini":
            continue
        item_path = os.path.join(directory_path, item) # example C:\Users\user\Documents\vacation.jpg
        if os.path.isfile(item_path):
            category = type_check(item)
            # Categorize each file
            # TODO: Should the planner include files already inside category folders?
            # TODO: Should it move a file if its source is already in its intended destination?
            # TODO: How should it handle a destination filename that already exists?
            destination_folder = os.path.join(directory_path, category)
            destination_path = os.path.join(destination_folder, item)
            if category not in file_categories:
                file_categories[category] = []
            file_categories[category].append({
                "source": item_path,
                "destination": destination_path
            })
    # Calculate the proposed destination paths
    return file_categories


def move_files(file_plans, dry_run=False):
    """
    Move planned files to their destinations and report the results.

    Returns:
        A dictionary containing:
        - moved: files successfully moved
        - skipped: files intentionally not moved
        - failed: files that encountered errors
        - planned: files that would be moved during a dry run
        - dry_run: whether this was a dry run
    """
    results = {
        "moved": [],
        "skipped": [],
        "failed": [],
        "planned": [],
        "dry_run": dry_run,
    }

    for category, files in file_plans.items():
        for file_info in files:
            source = file_info["source"]
            destination = file_info["destination"]

            # Handle the dry run without changing the filesystem.
            if dry_run:
                results["planned"].append({
                    "source": source,
                    "destination": destination,
                })
                print(f"[DRY RUN] Would move: {source} -> {destination}")
                continue

            try:
                # The source might have disappeared since planning.
                if not os.path.isfile(source):
                    results["skipped"].append({
                        "source": source,
                        "destination": destination,
                        "reason": "Source file does not exist",
                    })
                    continue

                # Never intentionally overwrite an existing destination.
                if os.path.exists(destination):
                    results["skipped"].append({
                        "source": source,
                        "destination": destination,
                        "reason": "Destination already exists",
                    })
                    continue

                # Create the destination folder if necessary.
                os.makedirs(
                    os.path.dirname(destination),
                    exist_ok=True,
                )

                # Move the file.
                os.rename(source, destination)

                results["moved"].append({
                    "source": source,
                    "destination": destination,
                })
                print(f"Moved: {source} -> {destination}")

            except OSError as error:
                # Handle filesystem errors without stopping other files.
                results["failed"].append({
                    "source": source,
                    "destination": destination,
                    "error": str(error),
                    "error_type": type(error).__name__,
                })
                print(f"Failed to move {source}: {error}")

    return results


'''
Requirement 4: Handle errors
Consider what should happen if:
- A source file disappears after planning.
- A file cannot be moved because of permissions.
- A destination directory cannot be created.
- A destination already exists.
Your function should handle foreseeable filesystem errors without unnecessarily crashing the entire operation.
Requirement 5: Report results
The caller should be able to determine:
- Which files were moved.
- Which files were skipped.
- Which operations failed.
- Whether the run was a dry run.
'''