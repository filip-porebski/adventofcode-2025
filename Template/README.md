# Day Template

This template folder provides a starting point for each new Advent of Code day solution.

## Quick Start

1. **Copy the template folder:**
   ```bash
   cp -r Template Day<X>
   ```
   Replace `<X>` with the day number (e.g., `Day2`, `Day3`, etc.)

2. **Update the day number:**
   - Open `main.py` and change `DAY: int = 0` to the correct day number
   - Update the docstring with the problem title and description

3. **Add input files:**
   - Rename `day0_example.txt` to `day<X>_example.txt` and add the example input
   - Rename `day0_input.txt` to `day<X>_input.txt` and add the puzzle input

4. **Implement the solution:**
   - Fill in `solve_part_one()` with your Part 1 solution
   - Fill in `solve_part_two()` with your Part 2 solution
   - Add any helper functions or constants as needed

5. **Test and run:**
   ```bash
   cd Day<X>
   python3 main.py
   ```

## Template Structure

```
Template/
├── main.py              # Main solution file with template code
├── day0_example.txt     # Template for example input (rename to day<X>_example.txt)
├── day0_input.txt       # Template for puzzle input (rename to day<X>_input.txt)
└── README.md           # This file
```

## Tips

- The template includes proper error handling and type hints
- All helper functions from `helper.py` are already imported
- The structure follows the same pattern as Day1 for consistency
- Remember to update the docstring with the problem description
- Add any day-specific constants at the top of `main.py`

## Automatic API Detection

The template automatically detects if `secret.json` is available and valid:
- **If `secret.json` exists and is valid** (has `AOC_COOKIE` and `YEAR` with reasonable values):
  - Automatically uses `get_input()` and `get_example()` to fetch from the API
  - No need to manually download input files!
- **If `secret.json` is missing or invalid**:
  - Falls back to `manually_get_input()` and `manually_get_example()`
  - Requires local input files

The template will print which method it's using when you run it.

## Helper Functions Available

- `is_api_available()`: Check if API can be used (returns True/False)
- `get_example(day, part)`: Fetch example from API (requires secret.json)
- `get_input(day)`: Fetch input from API (requires secret.json)
- `manually_get_example(day)`: Load example from local file
- `manually_get_input(day)`: Load input from local file
- `submit_answer(day, level, answer)`: Submit answer to Advent of Code

See `helper.py` for full documentation of all available functions.

