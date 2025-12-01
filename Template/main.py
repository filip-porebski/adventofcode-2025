"""
Advent of Code 2025 - Day {DAY}: {PROBLEM_TITLE}

{PROBLEM_DESCRIPTION}

Replace the placeholders above with:
- {DAY}: The day number (e.g., 1, 2, 3, ...)
- {PROBLEM_TITLE}: A brief title for the problem
- {PROBLEM_DESCRIPTION}: A description of what the problem is about
"""

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
DAY: int = 0  # TODO: Set the day number (1-25)


def solve_part_one(instructions: List[str]) -> int:
    """
    Solve Part 1 of the problem.

    Args:
        instructions: List of input strings (one per line)

    Returns:
        The solution for Part 1

    TODO: Implement the solution logic for Part 1
    """
    # TODO: Implement Part 1 solution
    result = 0

    for line in instructions:
        # TODO: Process each line
        pass

    return result


def solve_part_two(instructions: List[str]) -> int:
    """
    Solve Part 2 of the problem.

    Args:
        instructions: List of input strings (one per line)

    Returns:
        The solution for Part 2

    TODO: Implement the solution logic for Part 2
    """
    # TODO: Implement Part 2 solution
    result = 0

    for line in instructions:
        # TODO: Process each line
        pass

    return result


def main() -> None:
    """
    Main execution function that loads input data and solves both parts.

    Automatically uses API functions if secret.json is available and valid,
    otherwise falls back to manual file loading.

    Prints the results for both the example and puzzle input.
    """
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

