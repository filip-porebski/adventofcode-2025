# Advent of Code 2025

This repository contains my solutions for the [Advent of Code 2025](https://adventofcode.com/) programming challenges.

## Project Structure

```
adventofcode-2025/
├── Day1/                   # Day 1 Python solution
│   ├── day1_example.txt
│   ├── day1_input.txt
│   └── main.py
├── Day1CS/                 # Day 1 C# solution (if created)
│   ├── day1_example.txt
│   ├── day1_input.txt
│   ├── Day1CS.csproj
│   └── Program.cs
├── Template/               # Python template for new days
│   ├── main.py
│   └── README.md
├── TemplateCS/             # C# template for new days
│   ├── Program.cs
│   ├── DayTemplateCS.csproj
│   ├── day0_example.txt
│   ├── day0_input.txt
│   └── README.md
├── Aoc.CommonCS/           # C# helper library (project + AocClient)
│   ├── AocClient.cs
│   └── Aoc.CommonCS.csproj
├── create_day.py           # Script to create new day from Python template
├── helper.py               # Python utilities for fetching input and submitting answers
└── README.md
```

## Setup

### Prerequisites

- Python 3.7 or higher
- (Optional) `requests` library for automatic input fetching:
  ```bash
  pip install requests
  ```
- (Optional) .NET 8 SDK for the C# template

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

# Create CSharp Day4 from template (creates Day4CS)
python3 create_day.py 4 --language csharp

# Create both Python and CSharp for Day5
python3 create_day.py 5 --language both

# This will:
# - Create Day<X>/ (Python) when language includes python
# - Create Day<X>CS/ (C#) when language includes csharp
# - Copy template files
# - Set the Day constant automatically
# - Provide next steps
```

Then:
1. Add your example input to `Day2/day2_example.txt` (or `Day2CS/day2_example.txt` for C#).
2. Add your puzzle input to `Day2/day2_input.txt` (or `Day2CS/day2_input.txt` for C#).
3. Update the docstring in `Day2/main.py` (Python) or adjust comments in `Day2CS/Program.cs` (C#).
4. Implement `solve_part_one()` / `solve_part_two()` (Python) or `SolvePartOne` / `SolvePartTwo` (C#).

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

## C# Template (Visual Studio friendly)

A C# version of the helper (`Aoc.CommonCS/AocClient.cs`) and a ready-to-copy day template live under `TemplateCS`.

1. Copy `TemplateCS` to `Day<X>CS` (e.g., `Day4CS`).
2. Rename `DayTemplateCS.csproj` to `Day<X>CS.csproj` if desired.
3. Rename `day0_example.txt` / `day0_input.txt` to `day<X>_example.txt` / `day<X>_input.txt` and add your data.
4. Set `Day` in `Program.cs` and implement `SolvePartOne` / `SolvePartTwo`.
5. Run with `dotnet run --project Day<X>CS/Day<X>CS.csproj` or add the project to a Visual Studio solution.

The `AocClient` helper mirrors the Python utilities: it prefers API calls when `secret.json` or `AOC_COOKIE`/`AOC_YEAR` environment variables are available and falls back to local files, searching both the repo root `Day<day>` / `Day<day>CS` folders and paths beside the executable.

## Code Style

This project follows Python best practices:

- Type hints for all function parameters and return values
- Comprehensive docstrings following Google/NumPy style
- Clear variable naming and code organization
- Proper error handling and validation
- Consistent formatting

## License

This repository is for personal use and educational purposes. Advent of Code problems are created by [Eric Wastl](https://github.com/topaz).
