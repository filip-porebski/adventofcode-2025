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
    submit_answer,
)

# Constants
DAY: int = 3


def solve_part_one(instructions: List[str]) -> int:
    result = 0

    for line in instructions:
        digits = [char for char in line if char.isdigit()]

        if len(digits) < 2:
            continue

        biggest_int = max(digits)
        biggest_int_index = digits.index(biggest_int)
        digits_after_biggest = digits[biggest_int_index + 1 :]

        if digits_after_biggest:
            second_biggest_int = max(digits_after_biggest)
            formed_number = int(biggest_int + second_biggest_int)
        else:
            digits_before_biggest = digits[:biggest_int_index]
            second_biggest_int = max(digits_before_biggest)
            second_biggest_int_index = digits.index(second_biggest_int)
            digits_after_second_biggest = digits[second_biggest_int_index + 1 :]

            if digits_after_second_biggest:
                third_biggest_int = max(digits_after_second_biggest)
                formed_number = int(second_biggest_int + third_biggest_int)
            else:
                formed_number = 0

        result += formed_number
        # print(f"Line: {line} Formed number: {formed_number}")

    return result


def solve_part_two(instructions: List[str]) -> int:
    result = 0

    for line in instructions:
        # TODO: Process each line
        pass

    return result


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
        # submit_answer(DAY, part=2, answer=puzzle_part2)

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
