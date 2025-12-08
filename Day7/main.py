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
DAY: int = 7


def _find_start(instructions: List[str]) -> tuple[int, int, int]:
    """
    Return (start_row, start_col, width) for the grid.

    Raises ValueError if rows differ in length or S is missing.
    """
    if not instructions:
        raise ValueError("Input is empty")

    width = len(instructions[0])
    if any(len(row) != width for row in instructions):
        raise ValueError("All rows must have equal length")

    for r, row in enumerate(instructions):
        c = row.find("S")
        if c != -1:
            return r, c, width

    raise ValueError("Start position 'S' not found in grid")


def _simulate_beams(instructions: List[str]) -> tuple[int, set[int]]:
    """
    Simulate downward-moving beams and return (split_count, active_columns_at_bottom).
    """
    start_row, start_col, width = _find_start(instructions)

    active_columns: set[int] = {start_col}
    split_count = 0

    for row_idx in range(start_row, len(instructions)):
        next_columns: set[int] = set()
        for col in active_columns:
            cell = instructions[row_idx][col]
            if cell == "^":
                split_count += 1
                if col - 1 >= 0:
                    next_columns.add(col - 1)
                if col + 1 < width:
                    next_columns.add(col + 1)
            else:
                next_columns.add(col)

        active_columns = next_columns
        if not active_columns:
            break

    return split_count, active_columns


def solve_part_one(instructions: List[str]) -> int:
    if not instructions:
        return 0

    split_count, _ = _simulate_beams(instructions)
    return split_count


def _count_timelines(instructions: List[str]) -> int:
    """
    Count the number of distinct timelines a single particle can take.
    """
    start_row, start_col, width = _find_start(instructions)

    active: dict[int, int] = {start_col: 1}
    finished = 0

    for row_idx in range(start_row, len(instructions)):
        next_active: dict[int, int] = {}
        for col, count in active.items():
            cell = instructions[row_idx][col]
            if cell == "^":
                for new_col in (col - 1, col + 1):
                    if 0 <= new_col < width:
                        next_active[new_col] = next_active.get(new_col, 0) + count
                    else:
                        finished += count  # Beam exits the manifold sideways.
            else:
                next_active[col] = next_active.get(col, 0) + count

        active = next_active
        if not active:
            break

    return finished + sum(active.values())


def solve_part_two(instructions: List[str]) -> int:
    if not instructions:
        return 0

    return _count_timelines(instructions)


def main() -> None:
    try:
        if is_api_available():
            print("Using API to fetch input data...")
            example_data = get_example(DAY, part=1)
            puzzle_data = get_input(DAY)
        else:
            print("Using local files for input data...")
            example_data = manually_get_example(DAY)
            puzzle_data = manually_get_input(DAY)

        example_part1 = solve_part_one(example_data)
        puzzle_part1 = solve_part_one(puzzle_data)

        print(f"Part 1 - Example: {example_part1}")
        print(f"Part 1 - Puzzle: {puzzle_part1}")
        print()

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

