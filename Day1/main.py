from pathlib import Path
import sys

parent_directory = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_directory))

from helper import (  # noqa: E402
    get_example,
    get_input,
    is_api_available,
    manually_get_example,
    manually_get_input,
)

DAY = 1

DIAL_START = 50
DIAL_LIMITS = [0, 99]
SPAN = DIAL_LIMITS[1] - DIAL_LIMITS[0] + 1


def first_part(puzzle_input):
    my_dial_position = DIAL_START
    zeroes = 0
    for line in puzzle_input:
        line = line.strip()
        line = [line[0], int(line[1:])]

        if line[0] == "R":
            my_dial_position = (
                my_dial_position + line[1] - DIAL_LIMITS[0]
            ) % SPAN + DIAL_LIMITS[0]
        elif line[0] == "L":
            my_dial_position = (
                my_dial_position - line[1] - DIAL_LIMITS[0]
            ) % SPAN + DIAL_LIMITS[0]

        if my_dial_position == 0:
            zeroes += 1

    return zeroes


def second_part(puzzle_input):
    my_dial_position = DIAL_START
    zeroes = 0
    for line in puzzle_input:
        line = line.strip()
        line = [line[0], int(line[1:])]

        if line[0] == "R":
            for _ in range(line[1]):
                my_dial_position = (
                    my_dial_position + 1 - DIAL_LIMITS[0]
                ) % SPAN + DIAL_LIMITS[0]
                if my_dial_position == 0:
                    zeroes += 1
        elif line[0] == "L":
            for _ in range(line[1]):
                my_dial_position = (
                    my_dial_position - 1 - DIAL_LIMITS[0]
                ) % SPAN + DIAL_LIMITS[0]
                if my_dial_position == 0:
                    zeroes += 1
    return zeroes


def main():
    # Use API if available, otherwise use manual file loading
    if is_api_available():
        print("Using API to fetch input data...")
        example = get_example(DAY, part=1)
        puzzle_input = get_input(DAY)
    else:
        print("Using local files for input data...")
        example = manually_get_example(DAY)
        puzzle_input = manually_get_input(DAY)

    print(f"Example Part 1: {first_part(example)}")
    print(f"puzzle_input Part 1: {first_part(puzzle_input)}")

    print(f"Example Part 2: {second_part(example)}")
    print(f"puzzle_input Part 2: {second_part(puzzle_input)}")


if __name__ == "__main__":
    main()
