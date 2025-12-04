# C# Day Template

This console app template mirrors the Python workflow but is ready for Visual Studio or `dotnet` CLI. It pulls input from the Advent of Code site when `secret.json` or `AOC_COOKIE`/`AOC_YEAR` are available and falls back to local text files.

## How to start a new day
- Copy `TemplateCS` to `Day<X>CS` (e.g., `Day4CS`).
- Rename `DayTemplateCS.csproj` to `Day<X>CS.csproj` and update the project name inside the file if you like.
- Rename `day0_input.txt` and `day0_example.txt` to `day<X>_input.txt` / `day<X>_example.txt` and drop your data in.
- Open the folder in Visual Studio and add the project to your solution, or run `dotnet run --project Day<X>CS/Day<X>CS.csproj`.
- Set `Day` in `Program.cs` to the correct number and implement `SolvePartOne` / `SolvePartTwo`.

## Automated creation
- Run `python3 create_day.py <X> --language csharp` from the repo root to copy the template, rename files, and set the day number automatically (creates `Day<X>CS`).

## Helper reference
- `AocClient.IsApiAvailable()` detects whether API access is possible from environment variables or `secret.json`.
- `GetInputAsync(day)` / `GetExampleAsync(day, part)` fetch data from adventofcode.com with retry logic and a proper User-Agent.
- `ManuallyGetInput(day)` / `ManuallyGetExample(day)` load `day<day>_input.txt` and `day<day>_example.txt` from either the repo root `Day<day>` folder or alongside the project.
- `SubmitAnswerAsync(day, level, answer)` prompts for confirmation and posts the answer, printing a verdict.
- `LoadInputFromFile(path)` loads arbitrary text files line-by-line.

## Notes
- Inputs are searched in multiple places: the current working directory, `Day<day>` folders near the executable, and the repository root. This keeps things working when running from `bin/Debug` inside Visual Studio.
- The helper uses `secret.json` from the repo (or env vars) for the session cookie and year. Format: `{"AOC_COOKIE": "...", "YEAR": "2025"}`.
