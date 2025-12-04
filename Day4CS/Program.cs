using AdventOfCode.Common;

namespace AdventOfCode.Day4CS;

internal static class Program
{
    private const int Day = 4;

    private static int SolvePartOne(IReadOnlyList<string> input)
    {
        if (input is null || input.Count == 0)
        {
            return 0;
        }

        var result = 0;
        var rows = input.Count;

        for (var r = 0; r < rows; r++)
        {
            var line = input[r];
            if (string.IsNullOrEmpty(line))
            {
                continue;
            }

            for (var c = 0; c < line.Length; c++)
            {
                if (line[c] != '@')
                {
                    continue;
                }

                var neighbors = 0;

                for (var dr = -1; dr <= 1; dr++)
                {
                    for (var dc = -1; dc <= 1; dc++)
                    {
                        if (dr == 0 && dc == 0)
                        {
                            continue;
                        }

                        var nr = r + dr;
                        var nc = c + dc;

                        if (nr < 0 || nr >= rows)
                        {
                            continue;
                        }

                        var neighborLine = input[nr];
                        if (string.IsNullOrEmpty(neighborLine))
                        {
                            continue;
                        }

                        if (nc < 0 || nc >= neighborLine.Length)
                        {
                            continue;
                        }

                        if (neighborLine[nc] == '@')
                        {
                            neighbors++;
                            if (neighbors >= 4)
                            {
                                break;
                            }
                        }
                    }

                    if (neighbors >= 4)
                    {
                        break;
                    }
                }

                if (neighbors < 4)
                {
                    result++;
                }
            }
        }

        return result;
    }

    private static int SolvePartTwo(IReadOnlyList<string> input)
    {
        if (input is null || input.Count == 0)
        {
            return 0;
        }

        // Create a mutable copy of the grid preserving row lengths.
        var grid = new List<char[]>();
        foreach (var line in input)
        {
            grid.Add(string.IsNullOrEmpty(line) ? Array.Empty<char>() : line.ToCharArray());
        }

        var rows = grid.Count;
        var removedTotal = 0;

        while (true)
        {
            var toRemove = new List<(int r, int c)>();

            for (var r = 0; r < rows; r++)
            {
                var row = grid[r];
                if (row.Length == 0)
                {
                    continue;
                }

                for (var c = 0; c < row.Length; c++)
                {
                    if (row[c] != '@')
                    {
                        continue;
                    }

                    var neighbors = 0;
                    for (var dr = -1; dr <= 1; dr++)
                    {
                        for (var dc = -1; dc <= 1; dc++)
                        {
                            if (dr == 0 && dc == 0)
                            {
                                continue;
                            }

                            var nr = r + dr;
                            var nc = c + dc;

                            if (nr < 0 || nr >= rows)
                            {
                                continue;
                            }

                            var neighborRow = grid[nr];
                            if (neighborRow.Length == 0)
                            {
                                continue;
                            }

                            if (nc < 0 || nc >= neighborRow.Length)
                            {
                                continue;
                            }

                            if (neighborRow[nc] == '@')
                            {
                                neighbors++;
                                if (neighbors >= 4)
                                {
                                    break;
                                }
                            }
                        }

                        if (neighbors >= 4)
                        {
                            break;
                        }
                    }

                    if (neighbors < 4)
                    {
                        toRemove.Add((r, c));
                    }
                }
            }

            if (toRemove.Count == 0)
            {
                break;
            }

            foreach (var (r, c) in toRemove)
            {
                grid[r][c] = '.';
            }

            removedTotal += toRemove.Count;
        }

        return removedTotal;
    }

    public static async Task Main(string[] args)
    {
        try
        {
            var useApi = AocClient.IsApiAvailable();

            IReadOnlyList<string> exampleData;
            IReadOnlyList<string> puzzleData;

            if (useApi)
            {
                Console.WriteLine("Using API to fetch input data...");
                exampleData = await AocClient.GetExampleAsync(Day, part: 1);
                puzzleData = await AocClient.GetInputAsync(Day);
            }
            else
            {
                Console.WriteLine("Using local files for input data...");
                exampleData = AocClient.ManuallyGetExample(Day);
                puzzleData = AocClient.ManuallyGetInput(Day);
            }

            var examplePart1 = SolvePartOne(exampleData);
            var puzzlePart1 = SolvePartOne(puzzleData);

            Console.WriteLine($"Part 1 - Example: {examplePart1}");
            Console.WriteLine($"Part 1 - Puzzle:  {puzzlePart1}");
            Console.WriteLine();

            var examplePart2 = SolvePartTwo(exampleData);
            var puzzlePart2 = SolvePartTwo(puzzleData);

            Console.WriteLine($"Part 2 - Example: {examplePart2}");
            Console.WriteLine($"Part 2 - Puzzle:  {puzzlePart2}");

            // Uncomment to submit an answer once ready:
            // await AocClient.SubmitAnswerAsync(Day, level: 1, answer: puzzlePart1.ToString());
            // await AocClient.SubmitAnswerAsync(Day, level: 2, answer: puzzlePart2.ToString());
        }
        catch (FileNotFoundException ex)
        {
            Console.Error.WriteLine($"Missing input file: {ex.Message}");
            Environment.Exit(1);
        }
        catch (ArgumentException ex)
        {
            Console.Error.WriteLine($"Invalid input: {ex.Message}");
            Environment.Exit(1);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Unexpected error: {ex.Message}");
            Environment.Exit(1);
        }
    }
}
