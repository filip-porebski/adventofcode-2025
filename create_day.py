#!/usr/bin/env python3
"""
Helper script to create a new Advent of Code day from the template.

Usage:
    python3 create_day.py <day_number>

Example:
    python3 create_day.py 2
    python3 create_day.py 25

This will create a new Day<X> folder with all necessary files from the template.
"""

import argparse
import shutil
import sys
from pathlib import Path


def create_day_from_template(day: int, template_dir: Path, project_root: Path) -> Path:
    """
    Create a new day directory from the template.

    Args:
        day: The day number (1-25)
        template_dir: Path to the Template directory
        project_root: Path to the project root directory

    Returns:
        Path to the newly created day directory

    Raises:
        ValueError: If day is not in valid range or directory already exists
        FileNotFoundError: If template directory doesn't exist
        OSError: If directory creation or file copying fails
    """
    if not (1 <= day <= 25):
        raise ValueError(f"Day must be between 1 and 25, got: {day}")

    day_dir = project_root / f"Day{day}"

    if day_dir.exists():
        raise ValueError(
            f"Day{day} directory already exists at {day_dir.absolute()}. "
            "Delete it first if you want to recreate it."
        )

    if not template_dir.exists():
        raise FileNotFoundError(
            f"Template directory not found at {template_dir.absolute()}. "
            "Ensure the Template folder exists."
        )

    print(f"Creating Day{day} from template...")

    try:
        # Create the day directory
        day_dir.mkdir(parents=False, exist_ok=False)
        print(f"  ✓ Created directory: {day_dir}")

        # Copy and rename files
        files_to_copy = [
            ("main.py", "main.py"),
            ("day0_example.txt", f"day{day}_example.txt"),
            ("day0_input.txt", f"day{day}_input.txt"),
        ]

        for src_name, dst_name in files_to_copy:
            src_path = template_dir / src_name
            dst_path = day_dir / dst_name

            if not src_path.exists():
                print(f"  ⚠ Warning: Template file {src_name} not found, skipping")
                continue

            shutil.copy2(src_path, dst_path)
            print(f"  ✓ Copied {src_name} -> {dst_name}")

        # Update the DAY constant in main.py
        main_py_path = day_dir / "main.py"
        if main_py_path.exists():
            update_day_constant(main_py_path, day)
            print(f"  ✓ Updated DAY constant to {day} in main.py")

        print(f"\n✓ Successfully created Day{day}!")
        print("\nNext steps:")
        print(f"  1. cd Day{day}")
        print(f"  2. Add your example input to day{day}_example.txt")
        print(f"  3. Add your puzzle input to day{day}_input.txt")
        print("  4. Update the docstring in main.py with the problem description")
        print("  5. Implement solve_part_one() and solve_part_two()")
        print("  6. Run: python3 main.py")

        return day_dir

    except OSError as e:
        # Clean up on failure
        if day_dir.exists():
            try:
                shutil.rmtree(day_dir)
            except OSError:
                pass
        raise OSError(f"Failed to create Day{day}: {e}") from e


def update_day_constant(file_path: Path, day: int) -> None:
    """
    Update the DAY constant in main.py.

    Args:
        file_path: Path to the main.py file
        day: The day number to set
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace DAY: int = 0 with DAY: int = <day>
        old_line = "DAY: int = 0"
        new_line = f"DAY: int = {day}"
        content = content.replace(old_line, new_line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"  ⚠ Warning: Could not update DAY constant: {e}")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Create a new Advent of Code day from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 create_day.py 2      # Create Day2
  python3 create_day.py 25    # Create Day25
        """,
    )
    parser.add_argument(
        "day",
        type=int,
        help="Day number (1-25)",
    )
    parser.add_argument(
        "--template",
        type=str,
        default="Template",
        help="Template directory name (default: Template)",
    )

    args = parser.parse_args()

    # Get project root (parent of this script)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    template_dir = project_root / args.template

    try:
        create_day_from_template(args.day, template_dir, project_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

