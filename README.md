# Advent of Code 2025

This repository contains my solutions for the [Advent of Code 2025](https://adventofcode.com/) programming challenges.

## Project Structure

```
adventofcode-2025/
├── Day1/              # Day 1 solutions
│   ├── day1_example.txt
│   ├── day1_input.txt
│   └── main.py
├── Template/          # Template for creating new day solutions
│   ├── main.py
│   ├── day0_example.txt
│   ├── day0_input.txt
│   └── README.md
├── create_day.py      # Script to create new day from template
├── helper.py          # Utility functions for fetching input and submitting answers
└── README.md          # This file
```

## Setup

### Prerequisites

- Python 3.7 or higher
- (Optional) `requests` library for automatic input fetching:
  ```bash
  pip install requests
  ```

### Configuration (Optional)

To enable automatic input fetching from the Advent of Code website, create a `secret.json` file in the project root with your session cookie:

```json
{
  "AOC_COOKIE": "your_session_cookie_here",
  "YEAR": "2025"
}
```

**Note:** You can find your session cookie in your browser's developer tools after logging into Advent of Code.

## Usage

### Creating a New Day

The fastest way to start a new day is using the template:

```bash
# Create Day2 from template
python3 create_day.py 2

# This will:
# - Create Day2/ directory
# - Copy template files
# - Set the DAY constant automatically
# - Provide next steps
```

Then:
1. Add your example input to `Day2/day2_example.txt`
2. Add your puzzle input to `Day2/day2_input.txt`
3. Update the docstring in `Day2/main.py` with the problem description
4. Implement `solve_part_one()` and `solve_part_two()`

Alternatively, you can manually copy the `Template/` folder and rename it.

### Running Solutions

Navigate to a day's directory and run the solution:

```bash
cd Day1
python3 main.py
```

### Helper Functions

The `helper.py` module provides several utility functions:

- **`manually_get_input(day)`**: Load input from local file (`Day<day>/day<day>_input.txt`)
- **`manually_get_example(day)`**: Load example from local file (`Day<day>/day<day>_example.txt`)
- **`get_input(day)`**: Fetch input from Advent of Code website (requires `secret.json`)
- **`get_example(day, part)`**: Fetch example from Advent of Code website (requires `secret.json`)
- **`submit_answer(day, level, answer)`**: Submit an answer to Advent of Code (requires `secret.json`)
- **`load_input_from_file(file_name)`**: Load input from a custom file path

## Code Style

This project follows Python best practices:

- Type hints for all function parameters and return values
- Comprehensive docstrings following Google/NumPy style
- Clear variable naming and code organization
- Proper error handling and validation
- Consistent formatting

## License

This repository is for personal use and educational purposes. Advent of Code problems are created by [Eric Wastl](https://github.com/topaz).
