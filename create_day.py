#!/usr/bin/env python3
"""
Helper script to create a new Advent of Code day from the template (Python or C#).

Usage:
    python3 create_day.py <day_number> [--language python|csharp|both]

Example:
    python3 create_day.py 2
    python3 create_day.py 25
    python3 create_day.py 4 --language csharp

This will create a new Day<X> folder with all necessary files from the chosen template(s).
"""

import argparse
import shutil
import sys
from pathlib import Path


def create_day_from_template(day: int, template_dir: Path, project_root: Path) -> Path:
    """
    Create a new Python day directory from the template.
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

    print(f"Creating Day{day} from Python template...")

    try:
        day_dir.mkdir(parents=False, exist_ok=False)
        print(f"  [*] Created directory: {day_dir}")

        files_to_copy = [
            ("main.py", "main.py"),
            ("day0_example.txt", f"day{day}_example.txt"),
            ("day0_input.txt", f"day{day}_input.txt"),
        ]

        for src_name, dst_name in files_to_copy:
            src_path = template_dir / src_name
            dst_path = day_dir / dst_name

            if not src_path.exists():
                print(f"  ? Warning: Template file {src_name} not found, skipping")
                continue

            shutil.copy2(src_path, dst_path)
            print(f"  [*] Copied {src_name} -> {dst_name}")

        main_py_path = day_dir / "main.py"
        if main_py_path.exists():
            update_day_constant(main_py_path, day)
            print(f"  [*] Updated DAY constant to {day} in main.py")

        print(f"\n[*] Successfully created Day{day} (Python)!")
        print("\nNext steps:")
        print(f"  1. cd Day{day}")
        print(f"  2. Add your example input to day{day}_example.txt")
        print(f"  3. Add your puzzle input to day{day}_input.txt")
        print("  4. Update the docstring in main.py with the problem description")
        print("  5. Implement solve_part_one() and solve_part_two()")
        print("  6. Run: python3 main.py")

        return day_dir

    except OSError as e:
        if day_dir.exists():
            try:
                shutil.rmtree(day_dir)
            except OSError:
                pass
        raise OSError(f"Failed to create Day{day}: {e}") from e


def create_csharp_day_from_template(
    day: int, template_dir: Path, project_root: Path
) -> Path:
    """Create a new C# day directory from the CS template."""
    if not (1 <= day <= 25):
        raise ValueError(f"Day must be between 1 and 25, got: {day}")

    day_dir = project_root / f"Day{day}CS"

    if day_dir.exists():
        raise ValueError(
            f"CSharp Day{day} directory already exists at {day_dir.absolute()}. "
            "Delete it first if you want to recreate it."
        )

    if not template_dir.exists():
        raise FileNotFoundError(
            f"C# template directory not found at {template_dir.absolute()}. "
            "Ensure TemplateCS exists."
        )

    print(f"Creating CSharp Day{day} from template...")

    try:
        shutil.copytree(template_dir, day_dir)
        print(f"  [*] Copied template to {day_dir}")

        rename_pairs = [
            ("day0_example.txt", f"day{day}_example.txt"),
            ("day0_input.txt", f"day{day}_input.txt"),
            ("DayTemplateCS.csproj", f"Day{day}CS.csproj"),
        ]
        for src_name, dst_name in rename_pairs:
            src = day_dir / src_name
            dst = day_dir / dst_name
            if src.exists():
                src.rename(dst)
                print(f"  [*] Renamed {src_name} -> {dst_name}")

        program_path = day_dir / "Program.cs"
        if program_path.exists():
            update_csharp_day_constant(program_path, day)
            print(f"  [*] Updated Day constant to {day} in Program.cs")

        print(f"\n[*] Successfully created CSharp Day{day}!")
        print("\nNext steps:")
        print(f"  1. cd Day{day}CS")
        print(f"  2. Add your example input to day{day}_example.txt")
        print(f"  3. Add your puzzle input to day{day}_input.txt")
        print("  4. Implement SolvePartOne and SolvePartTwo in Program.cs")
        print(f"  5. Run: dotnet run --project Day{day}CS.csproj")

        return day_dir
    except OSError as e:
        if day_dir.exists():
            try:
                shutil.rmtree(day_dir)
            except OSError:
                pass
        raise OSError(f"Failed to create CSharp Day{day}: {e}") from e


def update_day_constant(file_path: Path, day: int) -> None:
    """Update the DAY constant in main.py."""
    try:
        content = file_path.read_text(encoding="utf-8")
        old_line = "DAY: int = 0"
        new_line = f"DAY: int = {day}"
        content = content.replace(old_line, new_line)
        file_path.write_text(content, encoding="utf-8")
    except Exception as exc:  # pragma: no cover - best-effort logging only
        print(f"  ? Warning: Could not update DAY constant: {exc}")


def update_csharp_day_constant(file_path: Path, day: int) -> None:
    """Update the Day constant in Program.cs (C# template)."""
    try:
        content = file_path.read_text(encoding="utf-8")
        old = "const int Day = 0;"
        new = f"const int Day = {day};"
        if old not in content:
            print("  ? Warning: Could not find Day constant to update in Program.cs")
            return
        file_path.write_text(content.replace(old, new), encoding="utf-8")
    except Exception as exc:  # pragma: no cover - best-effort logging only
        print(f"  ? Warning: Could not update Day constant in Program.cs: {exc}")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Create a new Advent of Code day from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 create_day.py 2                     # Create Day2 (Python)
  python3 create_day.py 25                    # Create Day25 (Python)
  python3 create_day.py 4 --language csharp   # Create CSharp Day4
  python3 create_day.py 5 --language both     # Create both
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
        help="Python template directory name (default: Template)",
    )
    parser.add_argument(
        "--language",
        choices=["python", "csharp", "both"],
        default="python",
        help="Which template to create (default: python)",
    )
    parser.add_argument(
        "--csharp-template",
        type=str,
        default="TemplateCS",
        help="C# template directory (default: TemplateCS)",
    )

    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    template_dir = project_root / args.template
    csharp_template_dir = project_root / args.csharp_template

    try:
        if args.language in ("python", "both"):
            create_day_from_template(args.day, template_dir, project_root)
        if args.language in ("csharp", "both"):
            create_csharp_day_from_template(args.day, csharp_template_dir, project_root)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
