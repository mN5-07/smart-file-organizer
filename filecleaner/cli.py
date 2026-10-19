"""Command-line interface for Smart File Organizer."""

import argparse

from filecleaner.duplicates import find_duplicates
from filecleaner.organizer import placement, move_files
from filecleaner.scanner import scan_directory


def main():
    parser = argparse.ArgumentParser(
        description="Organize files, scan directories, and find duplicates."
    )

    subparsers = parser.add_subparsers(dest="command")

    # Organize files
    organize_parser = subparsers.add_parser(
        "organize",
        help="Organize files by type.",
    )
    organize_parser.add_argument("directory", help="Directory to organize.")
    organize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview file movements without changing files.",
    )

    # Scan files
    scan_parser = subparsers.add_parser(
        "scan",
        help="List files and their details.",
    )
    scan_parser.add_argument("directory", help="Directory to scan.")
    scan_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Include files in subdirectories.",
    )

    # Find duplicates
    duplicates_parser = subparsers.add_parser(
        "duplicates",
        help="Find files with identical contents.",
    )
    duplicates_parser.add_argument("directory", help="Directory to scan.")
    duplicates_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Include files in subdirectories.",
    )

    # Preserve the original syntax:
    # smart-file-organizer PATH --dry-run
    parser.add_argument(
        "legacy_directory",
        nargs="?",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--dry-run",
        dest="legacy_dry_run",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    args = parser.parse_args()

    try:
        if args.command == "scan":
            files = scan_directory(args.directory, recursive=args.recursive)

            for file_info in files:
                print(f"Name:      {file_info['filename']}")
                print(f"Path:      {file_info['path']}")
                print(f"Size:      {file_info['size']} bytes")
                print(f"Extension: {file_info['extension'] or '(none)'}")
                print(f"Modified:  {file_info['modification_time']}")
                print()

            print(f"Total files scanned: {len(files)}")

        elif args.command == "duplicates":
            files = scan_directory(args.directory, recursive=args.recursive)
            duplicates = find_duplicates(files)

            if not duplicates:
                print("No duplicate files found.")
                return

            for file_hash, paths in duplicates.items():
                print(f"\nDuplicate group (SHA/MD5 hash: {file_hash}):")
                for path in paths:
                    print(f"  {path}")

            print(f"\nDuplicate groups found: {len(duplicates)}")

        else:
            directory = (
                args.directory
                if args.command == "organize"
                else args.legacy_directory
            )

            if not directory:
                parser.error("Provide a directory or choose a command.")

            dry_run = (
                args.dry_run
                if args.command == "organize"
                else args.legacy_dry_run
            )

            file_plans = placement(directory)
            results = move_files(file_plans, dry_run=dry_run)

            print("\nOrganization summary:")
            print(f"Moved:   {len(results['moved'])}")
            print(f"Skipped: {len(results['skipped'])}")
            print(f"Failed:  {len(results['failed'])}")

            if dry_run:
                print(f"Planned: {len(results['planned'])}")
                print("Dry run complete. No files were moved.")

            if results["failed"]:
                print("\nFailed operations:")
                for failure in results["failed"]:
                    print(f"- {failure['source']}: {failure['error']}")

    except (TypeError, ValueError, NotADirectoryError, FileNotFoundError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()