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
DAY: int = 6


def solve_part_one(instructions: List[str]) -> int:
    # If there are no lines, return 0
    if not instructions:
        return 0
    
    # The last line contains the operations
    operations_line = instructions[-1]
    
    # Remove the operations line from the list, leaving only numbers
    number_lines = instructions[:-1]
    
    # Find the columns that separate problems (full column of spaces)
    # First, determine the maximum length of any line
    max_length = max(len(line) for line in instructions)
    
    # Pad all lines to the same length
    padded_lines = [line.ljust(max_length) for line in instructions]
    
    # Find columns that are all spaces in all lines
    separator_columns = []
    for col in range(max_length):
        if all(line[col] == ' ' for line in padded_lines):
            separator_columns.append(col)
    
    # Group columns into problems
    problem_columns = []
    current_problem = []
    
    for col in range(max_length):
        if col in separator_columns:
            if current_problem:  # If we have a problem in progress, save it
                problem_columns.append(current_problem)
                current_problem = []
        else:
            current_problem.append(col)
    
    # Add the last problem if there is one
    if current_problem:
        problem_columns.append(current_problem)
    
    # For each problem, extract numbers and operation
    results = []
    for cols in problem_columns:
        # Extract numbers from each line for this problem
        numbers = []
        for line in number_lines:
            num_str = ''.join(line[col] for col in cols if col < len(line) and line[col] != ' ')
            if num_str:  # Only add non-empty strings
                numbers.append(int(num_str))
        
        # Extract the operation for this problem
        op_char = operations_line[cols[0]]  # First column of the problem should have the operation
        
        # Calculate the result
        result = numbers[0]
        for num in numbers[1:]:
            if op_char == '+':
                result += num
            elif op_char == '*':
                result *= num
        
        results.append(result)
    
    # Return the sum of all results
    return sum(results)


def solve_part_two(instructions: List[str]) -> int:
    if not instructions:
        return 0

    # Pad all lines so column indexing is consistent.
    max_len = max(len(line) for line in instructions)
    padded = [line.ljust(max_len) for line in instructions]
    operator_row = padded[-1]
    number_rows = padded[:-1]

    # Identify separator columns (all spaces) that split problems.
    separators = {col for col in range(max_len) if all(line[col] == " " for line in padded)}

    # Group contiguous non-separator columns into individual problems.
    problem_columns: List[List[int]] = []
    current: List[int] = []
    for col in range(max_len):
        if col in separators:
            if current:
                problem_columns.append(current)
                current = []
        else:
            current.append(col)
    if current:
        problem_columns.append(current)

    grand_total = 0

    for cols in problem_columns:
        # Right-to-left: read columns from the right edge of the problem toward the left.
        numbers: List[int] = []
        for c in reversed(cols):
            num_str = "".join(row[c] for row in number_rows if row[c].isdigit())
            if num_str:
                numbers.append(int(num_str))

        if not numbers:
            continue

        op = operator_row[cols[0]]  # Operator sits at the bottom of the leftmost column.

        result = numbers[0]
        for num in numbers[1:]:
            if op == "+":
                result += num
            elif op == "*":
                result *= num

        grand_total += result

    return grand_total


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
