from pathlib import Path
import sys

parent_directory = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_directory))

from helper import manually_get_example, manually_get_input

DAY = 1

DIAL_STARTS = ["", 50]
DIAL_LIMITS = [0, 99]

def first_part(input):
    # print("Input:", input)


    my_dial_position = DIAL_STARTS[1]
    zeroes = int(0)

    for line in input:
        line = line.strip()
        line = [str(line[0]), int(line[1:])]

        span = DIAL_LIMITS[1] - DIAL_LIMITS[0] + 1
        if line[0] == "R":
            my_dial_position = (
                my_dial_position + line[1] - DIAL_LIMITS[0]
            ) % span + DIAL_LIMITS[0]
        elif line[0] == "L":
            my_dial_position = (
                my_dial_position - line[1] - DIAL_LIMITS[0]
            ) % span + DIAL_LIMITS[0]

        if my_dial_position == 0:
            zeroes += 1

    return zeroes

def second_part(input):
    my_dial_position = DIAL_STARTS[1]
    zeroes = int(0)
    span = DIAL_LIMITS[1] - DIAL_LIMITS[0] + 1
    for line in input:
        line = line.strip()
        line = [str(line[0]), int(line[1:])]

        if line[0] == "R":
            for _ in range(line[1]):
                my_dial_position = (my_dial_position + 1 - DIAL_LIMITS[0]) % span + DIAL_LIMITS[0]
                if my_dial_position == 0:
                    zeroes += 1
        elif line[0] == "L":
            for _ in range(line[1]):
                my_dial_position = (my_dial_position - 1 - DIAL_LIMITS[0]) % span + DIAL_LIMITS[0]
                if my_dial_position == 0:
                    zeroes += 1
    return zeroes
    

def main():
    example = manually_get_example(DAY)
    input = manually_get_input(DAY)
        
    print("Example Part 1:", first_part(example))
    print("Input Part 1:", first_part(input))
    
    print("Example Part 2:", second_part(example))
    print("Input Part 2:", second_part(input))

if __name__ == "__main__":
    main()
