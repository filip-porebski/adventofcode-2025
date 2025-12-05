from pathlib import Path
import sys
from typing import List

# Add parent directory to path for helper imports
parent_directory = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_directory))

from helper import (  # noqa: E402
    get_example,
    get_input,
    is_api_available,
    manually_get_example,
    manually_get_input,
)

# Constants
DAY: int = 5


def solve_part_one(instructions: List[str]) -> int:
    ranges = []
    ingridients_id = []
    for line in instructions:
        line = line.strip()
        if not line:
            continue
        if "-" in line:
            ranges.append(line)
        else:
            ingridients_id.append(line)

    parsed_ranges: List[tuple[int, int]] = []
    for r in ranges:
        try:
            a_str, b_str = (p.strip() for p in r.split("-", 1))
            a = int(a_str)
            b = int(b_str)
            start, end = (a, b) if a <= b else (b, a)
            parsed_ranges.append((start, end))
        except Exception:
            continue

    ingredient_ids: List[int] = []
    for line in ingridients_id:
        parts = [p.strip() for p in line.split(",") if p.strip()]
        for part in parts:
            try:
                ingredient_ids.append(int(part))
            except Exception:
                continue

    count_in_ranges = 0
    for iid in ingredient_ids:
        for (start, end) in parsed_ranges:
            if start <= iid <= end:
                count_in_ranges += 1
                break

    return count_in_ranges


def solve_part_two(instructions: List[str]) -> int:
    ranges: List[str] = []
    for line in instructions:
        line = line.strip()
        if not line:
            continue
        if "-" in line:
            ranges.append(line)

    parsed_ranges: List[tuple[int, int]] = []
    for r in ranges:
        try:
            a_str, b_str = (p.strip() for p in r.split("-", 1))
            a = int(a_str)
            b = int(b_str)
            start, end = (a, b) if a <= b else (b, a)
            parsed_ranges.append((start, end))
        except Exception:
            continue

    if not parsed_ranges:
        return 0

    parsed_ranges.sort(key=lambda x: x[0])

    merged_ranges: List[list[int]] = []
    for start, end in parsed_ranges:
        if not merged_ranges or start > merged_ranges[-1][1] + 1:
            merged_ranges.append([start, end])
        else:
            merged_ranges[-1][1] = max(merged_ranges[-1][1], end)

    return sum(end - start + 1 for start, end in merged_ranges)


def main() -> None:
    try:
        # Use API if available, otherwise use manual file loading
        if is_api_available():
            print("Using API to fetch input data...")
            example_data = get_example(DAY, part=1)
            puzzle_data = get_input(DAY)
        else:
            print("Using local files for input data...")
            example_data = manually_get_example(DAY)
            puzzle_data = manually_get_input(DAY)

        # Solve Part 1
        example_part1 = solve_part_one(example_data)
        puzzle_part1 = solve_part_one(puzzle_data)

        print(f"Part 1 - Example: {example_part1}")
        print(f"Part 1 - Puzzle: {puzzle_part1}")
        print()

        # Solve Part 2
        example_part2 = solve_part_two(example_data)
        puzzle_part2 = solve_part_two(puzzle_data)

        print(f"Part 2 - Example: {example_part2}")
        print(f"Part 2 - Puzzle: {puzzle_part2}")

    except FileNotFoundError as e:
        print(f"Error: Could not find input file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid input format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

