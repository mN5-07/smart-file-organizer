# Identify files with identical contents and report which files are duplicates.
def find_duplicates(file_list):
    """
    Identify duplicate files based on their contents.

    Args:
        file_list (list): A list of dictionaries containing file details.

    Returns:
        dict: A dictionary where keys are file hashes and values are lists of file paths that are duplicates.
    """
    import hashlib
    from collections import defaultdict

    def hash_file(file_path):
        """Generate a hash for the given file."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            # Read the file in chunks to avoid memory issues with large files
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    duplicates = defaultdict(list)

    for file_info in file_list:
        file_path = file_info['path']
        file_hash = hash_file(file_path)
        duplicates[file_hash].append(file_path)

    # Filter out entries that have only one file (not duplicates)
    duplicates = {hash_value: paths for hash_value, paths in duplicates.items() if len(paths) > 1}

    return duplicates