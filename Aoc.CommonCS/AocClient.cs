using System.Text.Json;

namespace AdventOfCode.Common;

public static class AocClient
{
    private const int MinDay = 1;
    private const int MaxDay = 25;
    private const int MinLevel = 1;
    private const int MaxLevel = 2;
    private const int MaxRetries = 3;
    private const double BackoffSeconds = 1.0;
    private const string UserAgent = "adventofcode-helper/1.0 (https://github.com/filip-porebski/adventofcode-2025)";
    private static readonly string[] RequiredSecretKeys = { "AOC_COOKIE", "YEAR" };

    private static readonly object CredentialLock = new();
    private static Credentials? _cachedCredentials;

    public static bool IsApiAvailable()
    {
        return TryLoadCredentials() is not null;
    }

    public static async Task<IReadOnlyList<string>> GetInputAsync(int day, int? part = null)
    {
        ValidateDay(day);
        var credentials = LoadCredentials();
        using var client = CreateHttpClient(credentials);

        var url = $"https://adventofcode.com/{credentials.Year}/day/{day}/input";
        var body = await SendWithRetryAsync(client, () => new HttpRequestMessage(HttpMethod.Get, url));

        var trimmed = body.TrimEnd('\n', '\r');
        return trimmed.Length == 0 ? Array.Empty<string>() : trimmed.Split('\n');
    }

    public static async Task<IReadOnlyList<string>> GetExampleAsync(int day, int part = 1)
    {
        ValidateDay(day);
        ValidateLevel(part);
        var credentials = LoadCredentials();
        using var client = CreateHttpClient(credentials);

        var url = $"https://adventofcode.com/{credentials.Year}/day/{day}";
        var body = await SendWithRetryAsync(client, () => new HttpRequestMessage(HttpMethod.Get, url));

        var split = body.Split("<pre><code>", StringSplitOptions.None);
        if (split.Length <= part)
        {
            throw new IndexOutOfRangeException(
                $"Could not find example for part {part}. Found {split.Length - 1} example block(s) in the page.");
        }

        var fragment = split[part].Split("</code></pre>", StringSplitOptions.None)[0].Trim();
        return fragment.Length == 0 ? Array.Empty<string>() : fragment.Split('\n');
    }

    public static IReadOnlyList<string> ManuallyGetInput(int day, int? part = null)
    {
        ValidateDay(day);
        var path = ResolveDayFile(day, "input");
        return ReadLines(path);
    }

    public static IReadOnlyList<string> ManuallyGetExample(int day, int part = 1)
    {
        ValidateDay(day);
        ValidateLevel(part);
        var path = ResolveDayFile(day, "example");
        return ReadLines(path);
    }

    public static async Task SubmitAnswerAsync(int day, int level, string answer)
    {
        ValidateDay(day);
        ValidateLevel(level);

        var trimmedAnswer = (answer ?? string.Empty).Trim();
        if (string.IsNullOrEmpty(trimmedAnswer))
        {
            throw new ArgumentException("Answer cannot be empty", nameof(answer));
        }

        Console.WriteLine("You are about to submit the following answer:");
        Console.WriteLine($"  Day {day}, Level {level}: {trimmedAnswer}");
        Console.WriteLine("Warning: Advent of Code enforces a 60-second cooldown between submissions.");
        Console.Write("Press Enter to continue or Ctrl+C to abort... ");
        Console.ReadLine();

        var credentials = LoadCredentials();
        using var client = CreateHttpClient(credentials);

        var url = $"https://adventofcode.com/{credentials.Year}/day/{day}/answer";
        var content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["level"] = level.ToString(),
            ["answer"] = trimmedAnswer,
        });

        var responseBody = await SendWithRetryAsync(client, () => new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = content,
        });

        PrintSubmissionVerdict(responseBody, day, level);
    }

    public static IReadOnlyList<string> LoadInputFromFile(string fileName = "input.txt")
    {
        if (string.IsNullOrWhiteSpace(fileName))
        {
            throw new ArgumentException("File name cannot be empty", nameof(fileName));
        }

        var candidate = fileName == "input.txt"
            ? Path.Combine(Directory.GetCurrentDirectory(), fileName)
            : fileName;

        if (!File.Exists(candidate))
        {
            throw new FileNotFoundException($"Input file not found: {Path.GetFullPath(candidate)}");
        }

        if (Directory.Exists(candidate))
        {
            throw new ArgumentException($"Expected a file but found a directory: {candidate}", nameof(fileName));
        }

        return ReadLines(candidate);
    }

    private static HttpClient CreateHttpClient(Credentials credentials)
    {
        var handler = new HttpClientHandler
        {
            AutomaticDecompression = System.Net.DecompressionMethods.All,
        };

        var client = new HttpClient(handler)
        {
            Timeout = TimeSpan.FromSeconds(10),
        };

        client.DefaultRequestHeaders.Add("User-Agent", UserAgent);
        client.DefaultRequestHeaders.Add("Cookie", $"session={credentials.Cookie}");
        return client;
    }

    private static async Task<string> SendWithRetryAsync(HttpClient client, Func<HttpRequestMessage> requestFactory)
    {
        Exception? lastError = null;

        for (var attempt = 1; attempt <= MaxRetries; attempt++)
        {
            try
            {
                using var request = requestFactory();
                using var response = await client.SendAsync(request);

                if ((int)response.StatusCode == 429 || ((int)response.StatusCode >= 500 && (int)response.StatusCode < 600))
                {
                    lastError = new HttpRequestException(
                        $"Transient error {(int)response.StatusCode} when calling {request.RequestUri}");
                }
                else
                {
                    response.EnsureSuccessStatusCode();
                    return await response.Content.ReadAsStringAsync();
                }
            }
            catch (Exception ex) when (ex is HttpRequestException || ex is TaskCanceledException)
            {
                lastError = ex;
            }

            if (attempt < MaxRetries)
            {
                var delay = TimeSpan.FromSeconds(BackoffSeconds * attempt);
                await Task.Delay(delay);
            }
        }

        throw lastError ?? new InvalidOperationException("Request failed without a specific error.");
    }

    private static Credentials LoadCredentials()
    {
        return TryLoadCredentials() ?? throw new FileNotFoundException(
            "secret.json not found and AOC_COOKIE/AOC_YEAR environment variables are not set.");
    }

    private static Credentials? TryLoadCredentials()
    {
        lock (CredentialLock)
        {
            if (_cachedCredentials is not null)
            {
                return _cachedCredentials;
            }

            var envCredentials = LoadFromEnvironment();
            if (envCredentials is not null)
            {
                _cachedCredentials = envCredentials;
                return envCredentials;
            }

            var fileCredentials = LoadFromSecretFile();
            if (fileCredentials is not null)
            {
                _cachedCredentials = fileCredentials;
                return fileCredentials;
            }

            return null;
        }
    }

    private static Credentials? LoadFromEnvironment()
    {
        var cookie = Environment.GetEnvironmentVariable("AOC_COOKIE");
        var year = Environment.GetEnvironmentVariable("AOC_YEAR");

        if (string.IsNullOrWhiteSpace(cookie) || string.IsNullOrWhiteSpace(year))
        {
            return null;
        }

        ValidateYear(year);
        return new Credentials(cookie.Trim(), year.Trim());
    }

    private static Credentials? LoadFromSecretFile()
    {
        var secretPath = FindFileUpwards("secret.json");
        if (secretPath is null)
        {
            return null;
        }

        using var stream = File.OpenRead(secretPath.FullName);
        var payload = JsonDocument.Parse(stream).RootElement;

        foreach (var key in RequiredSecretKeys)
        {
            if (!payload.TryGetProperty(key, out _))
            {
                throw new KeyNotFoundException($"Missing required key '{key}' in {secretPath.FullName}");
            }
        }

        var cookie = payload.GetProperty("AOC_COOKIE").GetString();
        var year = payload.GetProperty("YEAR").ToString();

        if (string.IsNullOrWhiteSpace(cookie))
        {
            throw new InvalidOperationException("AOC_COOKIE must be non-empty.");
        }

        ValidateYear(year);
        return new Credentials(cookie.Trim(), year.Trim());
    }

    private static IReadOnlyList<string> ReadLines(string path)
    {
        var lines = File.ReadAllLines(path)
            .Select(line => line.TrimEnd('\r'))
            .ToArray();
        return lines;
    }

    private static string ResolveDayFile(int day, string suffix)
    {
        var fileName = $"day{day}_{suffix}.txt";
        var candidates = GetDayFileCandidates(day, fileName).ToList();

        var match = candidates.FirstOrDefault(File.Exists);
        if (match is not null)
        {
            return match;
        }

        throw new FileNotFoundException(
            $"Could not find {suffix} file for day {day}. Checked: {string.Join("; ", candidates)}");
    }

    private static IEnumerable<string> GetDayFileCandidates(int day, string fileName)
    {
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        var repoRoot = FindRepositoryRoot();
        if (repoRoot is not null)
        {
            foreach (var folder in new[] { $"Day{day}", $"Day{day}CS" })
            {
                var path = Path.Combine(repoRoot.FullName, folder, fileName);
                if (seen.Add(path))
                {
                    yield return path;
                }
            }
        }

        var cwd = new DirectoryInfo(Directory.GetCurrentDirectory());
        var candidates = new[]
        {
            Path.Combine(cwd.FullName, fileName),
            Path.Combine(cwd.FullName, $"Day{day}", fileName),
            Path.Combine(cwd.FullName, $"Day{day}CS", fileName),
            Path.Combine(AppContext.BaseDirectory, fileName),
            Path.Combine(AppContext.BaseDirectory, $"Day{day}", fileName),
            Path.Combine(AppContext.BaseDirectory, $"Day{day}CS", fileName),
        };

        foreach (var path in candidates)
        {
            if (seen.Add(path))
            {
                yield return path;
            }
        }

        var dayDir = FindDirectoryUpwards($"Day{day}", AppContext.BaseDirectory) ??
                     FindDirectoryUpwards($"Day{day}CS", AppContext.BaseDirectory);
        if (dayDir is not null)
        {
            var path = Path.Combine(dayDir.FullName, fileName);
            if (seen.Add(path))
            {
                yield return path;
            }
        }
    }

    private static void ValidateDay(int day)
    {
        if (day < MinDay || day > MaxDay)
        {
            throw new ArgumentOutOfRangeException(nameof(day), $"Day must be between {MinDay} and {MaxDay}.");
        }
    }

    private static void ValidateLevel(int level)
    {
        if (level < MinLevel || level > MaxLevel)
        {
            throw new ArgumentOutOfRangeException(nameof(level), $"Level must be between {MinLevel} and {MaxLevel}.");
        }
    }

    private static void ValidateYear(string year)
    {
        if (!int.TryParse(year, out var parsedYear) || parsedYear < 2000 || parsedYear > 2100)
        {
            throw new ArgumentException("YEAR must be a four digit value between 2000 and 2100.", nameof(year));
        }
    }

    private static FileInfo? FindFileUpwards(string fileName)
    {
        var current = new DirectoryInfo(AppContext.BaseDirectory);
        while (current is not null)
        {
            var candidate = new FileInfo(Path.Combine(current.FullName, fileName));
            if (candidate.Exists)
            {
                return candidate;
            }

            current = current.Parent;
        }

        return null;
    }

    private static DirectoryInfo? FindRepositoryRoot()
    {
        var current = new DirectoryInfo(AppContext.BaseDirectory);
        while (current is not null)
        {
            var hasSecret = File.Exists(Path.Combine(current.FullName, "secret.json"));
            var hasGitIgnore = File.Exists(Path.Combine(current.FullName, ".gitignore"));
            if (hasSecret || hasGitIgnore)
            {
                return current;
            }

            current = current.Parent;
        }

        return null;
    }

    private static DirectoryInfo? FindDirectoryUpwards(string directoryName, string startAt)
    {
        var current = new DirectoryInfo(startAt);
        while (current is not null)
        {
            var candidate = current.GetDirectories()
                .FirstOrDefault(d => string.Equals(d.Name, directoryName, StringComparison.OrdinalIgnoreCase));
            if (candidate is not null)
            {
                return candidate;
            }

            current = current.Parent;
        }

        return null;
    }

    private static void PrintSubmissionVerdict(string responseBody, int day, int level)
    {
        if (responseBody.Contains("You gave an answer too recently", StringComparison.OrdinalIgnoreCase))
        {
            Console.WriteLine("VERDICT: TOO MANY REQUESTS");
            Console.WriteLine("Wait at least 60 seconds between submissions.");
            return;
        }

        if (responseBody.Contains("That's the right answer", StringComparison.OrdinalIgnoreCase) ||
            responseBody.Contains("You have completed", StringComparison.OrdinalIgnoreCase))
        {
            Console.WriteLine("VERDICT: OK!");
            Console.WriteLine("Answer accepted.");
            return;
        }

        if (responseBody.Contains("not the right answer", StringComparison.OrdinalIgnoreCase))
        {
            if (responseBody.Contains("too low", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("VERDICT: WRONG (TOO LOW)");
            }
            else if (responseBody.Contains("too high", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("VERDICT: WRONG (TOO HIGH)");
            }
            else
            {
                Console.WriteLine("VERDICT: WRONG (UNKNOWN)");
            }

            return;
        }

        if (responseBody.Contains("seem to be solving the right level", StringComparison.OrdinalIgnoreCase) ||
            responseBody.Contains("already complete", StringComparison.OrdinalIgnoreCase))
        {
            Console.WriteLine("VERDICT: ALREADY SOLVED");
            Console.WriteLine($"Day {day}, level {level} has already been completed.");
            return;
        }

        Console.WriteLine("VERDICT: UNKNOWN");
        Console.WriteLine("Received an unexpected response from the server. Check the site to confirm status.");
    }

    private readonly record struct Credentials(string Cookie, string Year);
}
