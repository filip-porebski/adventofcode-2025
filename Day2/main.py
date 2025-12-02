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
DAY: int = 2


def solve_part_one(instructions: List[str]) -> int:
    range_parts = []
    for line in instructions:
        range_parts.extend([p.strip() for p in line.split(",") if p.strip()])

    total_sum = 0
    matching_ids = []
    for part in range_parts:
        start_str, end_str = (x.strip() for x in part.split("-"))
        start = int(start_str)
        end = int(end_str)
        for id_num in range(start, end + 1):
            id_str = str(id_num)
            if len(id_str) % 2 == 0:
                half = len(id_str) // 2
                if id_str[:half] == id_str[half:]:
                    matching_ids.append(id_num)
                    total_sum += id_num

    return total_sum


def solve_part_two(instructions: List[str]) -> int:
    range_parts = []
    for line in instructions:
        range_parts.extend([p.strip() for p in line.split(",") if p.strip()])

    total_sum = 0
    matching_ids = []
    for part in range_parts:
        start_str, end_str = (x.strip() for x in part.split("-"))
        start = int(start_str)
        end = int(end_str)
        for id_num in range(start, end + 1):
            id_str = str(id_num)
            length = len(id_str)
            is_repeated = False
            for pattern_len in range(1, length // 2 + 1):
                if length % pattern_len != 0:
                    continue
                repeat_count = length // pattern_len
                if repeat_count >= 2 and id_str[:pattern_len] * repeat_count == id_str:
                    is_repeated = True
                    break
            if is_repeated:
                matching_ids.append(id_num)
                total_sum += id_num

    return total_sum


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
