using AdventOfCode.Common;

const int Day = 0;

static int SolvePartOne(IReadOnlyList<string> input)
{
    var result = 0;

    foreach (var line in input)
    {
        // TODO: implement part 1 logic.
    }

    return result;
}

static int SolvePartTwo(IReadOnlyList<string> input)
{
    var result = 0;

    foreach (var line in input)
    {
        // TODO: implement part 2 logic.
    }

    return result;
}

static async Task<int> Main()
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
        // await AocClient.SubmitAnswerAsync(Day, level: 1, answer: puzzlePart1);
        // await AocClient.SubmitAnswerAsync(Day, level: 2, answer: puzzlePart2);

        return 0;
    }
    catch (FileNotFoundException ex)
    {
        Console.Error.WriteLine($"Missing input file: {ex.Message}");
        return 1;
    }
    catch (ArgumentException ex)
    {
        Console.Error.WriteLine($"Invalid input: {ex.Message}");
        return 1;
    }
    catch (Exception ex)
    {
        Console.Error.WriteLine($"Unexpected error: {ex.Message}");
        return 1;
    }
}
