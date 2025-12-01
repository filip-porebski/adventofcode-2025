"""
Advent of Code Helper Functions

This module provides utilities for fetching input data from Advent of Code
and loading local input files. It supports both automatic fetching from the
Advent of Code website (requires authentication) and manual loading from
local text files.

The module is designed to be production-ready with proper error handling,
logging, input validation, and support for both file-based and API-based
data retrieval.

Example:
    Basic usage with local files:
        >>> input_data = manually_get_input(day=1)
        >>> example_data = manually_get_example(day=1)

    Usage with API (requires secret.json):
        >>> input_data = get_input(day=1)
        >>> submit_answer(day=1, level=1, answer="12345")
"""

import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    import requests

try:
    import requests
    from requests.adapters import HTTPAdapter
    try:
        from urllib3.util.retry import Retry
    except ImportError:
        # Fallback for older requests versions
        from requests.packages.urllib3.util.retry import Retry  # type: ignore
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    Retry = None  # type: ignore
    HTTPAdapter = None  # type: ignore

# Constants
_MIN_DAY = 1
_MAX_DAY = 25
_MIN_LEVEL = 1
_MAX_LEVEL = 2
_DEFAULT_TIMEOUT = 10
_MAX_RETRIES = 3
_BACKOFF_FACTOR = 1.0
_USER_AGENT = "adventofcode-helper/1.0 (https://github.com/filip-porebski/adventofcode-2025)"
_SECRET_FILE_NAME = "secret.json"
_REQUIRED_SECRET_KEYS = ("AOC_COOKIE", "YEAR")

# Configure logging
_logger = logging.getLogger(__name__)
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    _logger.addHandler(_handler)
    _logger.setLevel(logging.WARNING)  # Default to WARNING to avoid noise

# Lazy-loaded secrets: don't try to read secret.json at import time so the module
# can be imported even when secret.json is missing (useful for manually_get_* helpers).
_secrets_cache: Optional[dict] = None


def _validate_day(day: int) -> None:
    """
    Validate that the day number is within the valid range.

    Args:
        day: The day number to validate

    Raises:
        ValueError: If day is not in the valid range [1, 25]
    """
    if not isinstance(day, int) or not (_MIN_DAY <= day <= _MAX_DAY):
        raise ValueError(
            f"Day must be an integer between {_MIN_DAY} and {_MAX_DAY}, got: {day}"
        )


def _validate_level(level: int) -> None:
    """
    Validate that the level number is within the valid range.

    Args:
        level: The level number to validate

    Raises:
        ValueError: If level is not 1 or 2
    """
    if not isinstance(level, int) or not (_MIN_LEVEL <= level <= _MAX_LEVEL):
        raise ValueError(
            f"Level must be an integer between {_MIN_LEVEL} and {_MAX_LEVEL}, got: {level}"
        )


def _create_session_with_retries() -> requests.Session:
    """
    Create a requests session with retry strategy for production reliability.

    Returns:
        A configured requests.Session object with retry logic

    Raises:
        ImportError: If requests library is not available
    """
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests library is required")

    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=_MAX_RETRIES,
        backoff_factor=_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
        allowed_methods=["GET", "POST"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set default headers
    session.headers.update({"User-Agent": _USER_AGENT})

    return session


def _load_secrets() -> dict:
    """
    Load and cache secrets from secret.json or environment variables.

    Search order:
    1. Environment variables (AOC_COOKIE, AOC_YEAR)
    2. Current working directory (secret.json)
    3. This module's directory (secret.json)

    Returns:
        A dictionary containing the secrets (typically 'AOC_COOKIE' and 'YEAR')

    Raises:
        FileNotFoundError: If no secret file is found and env vars are not set
        ValueError: If the secret file contains invalid JSON or missing required keys
        PermissionError: If the secret file cannot be read due to permissions

    Note:
        Environment variables take precedence over secret.json files.
        This allows for secure deployment in containerized environments.
    """
    global _secrets_cache
    if _secrets_cache is not None:
        return _secrets_cache

    # Check environment variables first (for production deployments)
    env_cookie = os.getenv("AOC_COOKIE")
    env_year = os.getenv("AOC_YEAR")

    if env_cookie and env_year:
        _logger.info("Loading credentials from environment variables")
        _secrets_cache = {
            "AOC_COOKIE": env_cookie,
            "YEAR": env_year,
        }
        return _secrets_cache

    # Fall back to secret.json files
    candidates = [
        Path(os.getcwd()) / _SECRET_FILE_NAME,
        Path(__file__).parent / _SECRET_FILE_NAME,
    ]

    for path in candidates:
        if path.exists():
            try:
                # Check file permissions (should not be world-readable)
                stat_info = path.stat()
                if stat_info.st_mode & 0o077:  # Check if others/group can read
                    _logger.warning(
                        f"Secret file '{path}' has overly permissive permissions. "
                        "Consider using chmod 600 for security."
                    )

                with open(path, "r", encoding="utf-8") as file:
                    _secrets_cache = json.load(file)
                    _logger.info(f"Loaded secrets from {path}")
                    return _secrets_cache
            except PermissionError as e:
                raise PermissionError(
                    f"Cannot read secret file '{path}' due to permissions: {e}"
                ) from e
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in secret file '{path}': {e}. "
                    "Expected format: {{\"AOC_COOKIE\": \"...\", \"YEAR\": \"...\"}}"
                ) from e
            except Exception as e:
                _logger.error(f"Unexpected error loading secrets from {path}: {e}")
                raise

    raise FileNotFoundError(
        f"{_SECRET_FILE_NAME} not found in current working directory or module directory, "
        f"and environment variables (AOC_COOKIE, AOC_YEAR) are not set. "
        f"Place a {_SECRET_FILE_NAME} with keys {_REQUIRED_SECRET_KEYS}, "
        "or set the environment variables, or use the manual input helpers."
    )


def _get_aoc_creds() -> Tuple[str, str]:
    """
    Extract and validate Advent of Code credentials from secrets.

    Returns:
        A tuple containing (AOC_COOKIE, YEAR) as strings

    Raises:
        KeyError: If required keys are missing from secrets
        ValueError: If credentials are empty or invalid
        FileNotFoundError: If secrets cannot be loaded
    """
    secrets = _load_secrets()

    missing_keys = [key for key in _REQUIRED_SECRET_KEYS if key not in secrets]
    if missing_keys:
        raise KeyError(
            f"Missing required secret keys: {missing_keys}. "
            f"Required keys: {_REQUIRED_SECRET_KEYS}"
        )

    cookie = secrets["AOC_COOKIE"]
    year = str(secrets["YEAR"]).strip()

    if not cookie or not cookie.strip():
        raise ValueError("AOC_COOKIE must be non-empty")
    if not year:
        raise ValueError("YEAR must be non-empty")

    # Validate year format (should be a 4-digit year)
    try:
        year_int = int(year)
        if not (2000 <= year_int <= 2100):
            _logger.warning(f"Year {year_int} seems unusual, but proceeding anyway")
    except ValueError:
        raise ValueError(f"YEAR must be a valid integer, got: {year}")

    return cookie.strip(), year


def get_input(day: int, part: Optional[int] = None) -> List[str]:
    """
    Fetch input data from Advent of Code website for a specific day.

    Args:
        day: The day number (1-25)
        part: Optional part number (unused, kept for API compatibility)

    Returns:
        A list of strings, one per line of input (trailing newlines removed).
        Returns empty list if input is empty.

    Raises:
        ValueError: If day is not in valid range [1, 25]
        ImportError: If requests library is not installed
        FileNotFoundError: If secret.json cannot be found
        KeyError: If required keys are missing from secret.json
        requests.RequestException: If the HTTP request fails after retries

    Example:
        >>> input_data = get_input(day=1)
        >>> print(f"Loaded {len(input_data)} lines of input")
    """
    _validate_day(day)

    if not REQUESTS_AVAILABLE:
        raise ImportError(
            "requests library is required for get_input(). "
            "Install it with: pip install requests"
        )

    cookie, year = _get_aoc_creds()
    session = _create_session_with_retries()

    url = f"https://adventofcode.com/{year}/day/{day}/input"
    _logger.info(f"Fetching input for day {day}")

    try:
        response = session.get(
            url,
            headers={"cookie": f"session={cookie}"},
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()

        # Validate response content
        if not response.text:
            _logger.warning(f"Received empty input for day {day}")
            return []

        # Remove trailing newline if present and split into lines
        text = response.text.rstrip("\n")
        lines = text.split("\n") if text else []
        _logger.info(f"Successfully fetched {len(lines)} lines for day {day}")
        return lines

    except requests.HTTPError as e:
        if e.response and e.response.status_code == 404:
            raise FileNotFoundError(
                f"Day {day} input not found. "
                f"Day may not be available yet or URL may be incorrect."
            ) from e
        elif e.response and e.response.status_code == 401:
            raise PermissionError(
                f"Authentication failed for day {day}. "
                "Check that your AOC_COOKIE is valid and not expired."
            ) from e
        else:
            raise requests.RequestException(
                f"HTTP error {e.response.status_code if e.response else 'unknown'} "
                f"while fetching input for day {day}: {e}"
            ) from e
    except requests.RequestException as e:
        _logger.error(f"Request failed for day {day}: {e}")
        raise requests.RequestException(
            f"Failed to fetch input for day {day} after {_MAX_RETRIES} retries: {e}"
        ) from e
    finally:
        session.close()


def get_example(day: int, part: int = 1) -> List[str]:
    """
    Fetch example data from Advent of Code website for a specific day and part.

    Args:
        day: The day number (1-25)
        part: The part number (1 or 2) to get the example for

    Returns:
        A list of strings, one per line of example input.
        Returns empty list if example is empty.

    Raises:
        ValueError: If day or part is not in valid range
        ImportError: If requests library is not installed
        FileNotFoundError: If secret.json cannot be found
        KeyError: If required keys are missing from secret.json
        requests.RequestException: If the HTTP request fails after retries
        IndexError: If the specified part's example cannot be found in the HTML

    Example:
        >>> example_data = get_example(day=1, part=1)
        >>> print(f"Loaded {len(example_data)} lines of example")
    """
    _validate_day(day)
    _validate_level(part)

    if not REQUESTS_AVAILABLE:
        raise ImportError(
            "requests library is required for get_example(). "
            "Install it with: pip install requests"
        )

    cookie, year = _get_aoc_creds()
    session = _create_session_with_retries()

    url = f"https://adventofcode.com/{year}/day/{day}"
    _logger.info(f"Fetching example for day {day}, part {part}")

    try:
        response = session.get(
            url,
            headers={"cookie": f"session={cookie}"},
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response and e.response.status_code == 404:
            raise FileNotFoundError(
                f"Day {day} not found. "
                f"Day may not be available yet or URL may be incorrect."
            ) from e
        elif e.response and e.response.status_code == 401:
            raise PermissionError(
                f"Authentication failed for day {day}. "
                "Check that your AOC_COOKIE is valid and not expired."
            ) from e
        else:
            raise requests.RequestException(
                f"HTTP error {e.response.status_code if e.response else 'unknown'} "
                f"while fetching example for day {day}: {e}"
            ) from e
    except requests.RequestException as e:
        _logger.error(f"Request failed for day {day}, part {part}: {e}")
        raise requests.RequestException(
            f"Failed to fetch example for day {day}, part {part} "
            f"after {_MAX_RETRIES} retries: {e}"
        ) from e

    try:
        # Extract example from HTML between <pre><code> tags
        # Note: Part 1 example is at index 1, part 2 at index 2, etc.
        parts = response.text.split("<pre><code>")
        if len(parts) <= part:
            raise IndexError(
                f"Could not find example for part {part} in day {day}'s HTML. "
                f"Found {len(parts) - 1} example(s) in the page. "
                f"Part numbers are 1-indexed."
            )

        example_text = parts[part].split("</code></pre>")[0].strip()
        lines = example_text.split("\n") if example_text else []
        _logger.info(
            f"Successfully fetched {len(lines)} lines of example for day {day}, part {part}"
        )
        return lines
    except IndexError as e:
        _logger.error(f"Failed to parse example HTML for day {day}, part {part}: {e}")
        raise IndexError(
            f"Failed to parse example HTML for day {day}, part {part}: {e}"
        ) from e
    finally:
        session.close()


def manually_get_input(day: int, part: Optional[int] = None) -> List[str]:
    """
    Load input data from a local text file.

    Looks for the file in the day-specific directory:
    <project_root>/Day<day>/day<day>_input.txt

    Args:
        day: The day number (1-25)
        part: Optional part number (unused, kept for API compatibility)

    Returns:
        A list of strings, one per line of input (trailing newlines removed).
        Returns empty list if file is empty.

    Raises:
        ValueError: If day is not in valid range [1, 25]
        FileNotFoundError: If the input file cannot be found
        IOError: If the file cannot be read
        PermissionError: If the file cannot be read due to permissions

    Example:
        >>> input_data = manually_get_input(day=1)
        >>> print(f"Loaded {len(input_data)} lines from local file")
    """
    _validate_day(day)

    day_dir = Path(__file__).parent / f"Day{day}"
    file_path = day_dir / f"day{day}_input.txt"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}. "
            f"Expected location: {file_path.absolute()}. "
            f"Ensure the file exists in the Day{day} directory."
        )

    if not file_path.is_file():
        raise ValueError(f"Path exists but is not a file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            lines = content.split("\n") if content else []
            _logger.debug(f"Loaded {len(lines)} lines from {file_path}")
            return lines
    except PermissionError as e:
        raise PermissionError(
            f"Cannot read input file '{file_path}' due to permissions: {e}"
        ) from e
    except IOError as e:
        raise IOError(
            f"Failed to read input file '{file_path}': {e}. "
            "Check that the file is readable and not corrupted."
        ) from e


def manually_get_example(day: int, part: int = 1) -> List[str]:
    """
    Load example data from a local text file.

    Looks for the file in the day-specific directory:
    <project_root>/Day<day>/day<day>_example.txt

    Args:
        day: The day number (1-25)
        part: Optional part number (unused, kept for API compatibility)

    Returns:
        A list of strings, one per line of example input (trailing newlines removed).
        Returns empty list if file is empty.

    Raises:
        ValueError: If day is not in valid range [1, 25]
        FileNotFoundError: If the example file cannot be found
        IOError: If the file cannot be read
        PermissionError: If the file cannot be read due to permissions

    Example:
        >>> example_data = manually_get_example(day=1)
        >>> print(f"Loaded {len(example_data)} lines from local file")
    """
    _validate_day(day)

    day_dir = Path(__file__).parent / f"Day{day}"
    file_path = day_dir / f"day{day}_example.txt"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Example file not found: {file_path}. "
            f"Expected location: {file_path.absolute()}. "
            f"Ensure the file exists in the Day{day} directory."
        )

    if not file_path.is_file():
        raise ValueError(f"Path exists but is not a file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            lines = content.split("\n") if content else []
            _logger.debug(f"Loaded {len(lines)} lines from {file_path}")
            return lines
    except PermissionError as e:
        raise PermissionError(
            f"Cannot read example file '{file_path}' due to permissions: {e}"
        ) from e
    except IOError as e:
        raise IOError(
            f"Failed to read example file '{file_path}': {e}. "
            "Check that the file is readable and not corrupted."
        ) from e


def submit_answer(day: int, level: int, answer: str) -> None:
    """
    Submit an answer to Advent of Code.

    Prompts the user for confirmation before submitting. This function includes
    rate limiting awareness and proper error handling for production use.

    Args:
        day: The day number (1-25)
        level: The part/level number (1 or 2)
        answer: The answer to submit (will be converted to string)

    Raises:
        ValueError: If day or level is not in valid range
        ImportError: If requests library is not installed
        FileNotFoundError: If secret.json cannot be found
        KeyError: If required keys are missing from secret.json
        requests.RequestException: If the HTTP request fails after retries
        PermissionError: If authentication fails

    Example:
        >>> submit_answer(day=1, level=1, answer="12345")
        You are about to submit the following answer:
          Day 1, Level 1: 12345
        Press Enter to continue or Ctrl+C to abort.
        VERDICT: OK!
        Answer accepted!

    Note:
        Advent of Code enforces a rate limit: you must wait at least 60 seconds
        between submissions. This function will detect and report rate limit errors.
    """
    _validate_day(day)
    _validate_level(level)

    if not REQUESTS_AVAILABLE:
        raise ImportError(
            "requests library is required for submit_answer(). "
            "Install it with: pip install requests"
        )

    # Convert answer to string and validate
    answer_str = str(answer).strip()
    if not answer_str:
        raise ValueError("Answer cannot be empty")

    print("You are about to submit the following answer:")
    print(f"  Day {day}, Level {level}: {answer_str}")
    print("⚠️  Warning: Advent of Code enforces a 60-second cooldown between submissions.")
    try:
        input("Press Enter to continue or Ctrl+C to abort.\n")
    except KeyboardInterrupt:
        print("\nSubmission cancelled by user.")
        _logger.info(f"Submission cancelled for day {day}, level {level}")
        return

    cookie, year = _get_aoc_creds()
    session = _create_session_with_retries()

    url = f"https://adventofcode.com/{year}/day/{day}/answer"
    data = {"level": str(level), "answer": answer_str}

    _logger.info(f"Submitting answer for day {day}, level {level}")

    try:
        response = session.post(
            url,
            headers={"cookie": f"session={cookie}"},
            data=data,
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response and e.response.status_code == 401:
            raise PermissionError(
                f"Authentication failed for day {day}. "
                "Check that your AOC_COOKIE is valid and not expired."
            ) from e
        elif e.response and e.response.status_code == 404:
            raise FileNotFoundError(
                f"Day {day} not found. Day may not be available yet."
            ) from e
        else:
            _logger.error(
                f"HTTP error {e.response.status_code if e.response else 'unknown'} "
                f"while submitting answer for day {day}, level {level}: {e}"
            )
            print(f"Error submitting answer: HTTP {e.response.status_code if e.response else 'unknown'}")
            return
    except requests.RequestException as e:
        _logger.error(f"Request failed for day {day}, level {level}: {e}")
        print(f"Error submitting answer: {e}")
        return
    finally:
        session.close()

    # Parse response with improved error detection
    response_text = response.text
    verdict_printed = False

    if "You gave an answer too recently" in response_text:
        print("VERDICT: TOO MANY REQUESTS")
        print("You must wait at least 60 seconds between submissions.")
        print("Please wait before trying again.")
        verdict_printed = True
        _logger.warning(f"Rate limited for day {day}, level {level}")
    elif "not the right answer" in response_text:
        if "too low" in response_text:
            print("VERDICT: WRONG (TOO LOW)")
            _logger.info(f"Answer too low for day {day}, level {level}")
        elif "too high" in response_text:
            print("VERDICT: WRONG (TOO HIGH)")
            _logger.info(f"Answer too high for day {day}, level {level}")
        else:
            print("VERDICT: WRONG (UNKNOWN)")
            _logger.warning(f"Wrong answer (unknown reason) for day {day}, level {level}")
        verdict_printed = True
    elif "seem to be solving the right level" in response_text or "already complete" in response_text.lower():
        print("VERDICT: ALREADY SOLVED")
        print("This level has already been completed.")
        verdict_printed = True
        _logger.info(f"Day {day}, level {level} already solved")
    elif "That's the right answer" in response_text or "You have completed" in response_text:
        print("VERDICT: OK!")
        print("Answer accepted! ✓")
        verdict_printed = True
        _logger.info(f"Correct answer submitted for day {day}, level {level}")

    if not verdict_printed:
        # Unknown response - log for debugging
        _logger.warning(
            f"Unexpected response format for day {day}, level {level}. "
            "Response may have changed or be unrecognized."
        )
        print("VERDICT: UNKNOWN")
        print("Received an unexpected response from the server.")
        print("Check the Advent of Code website to verify submission status.")


def is_api_available() -> bool:
    """
    Check if the API is available and configured correctly.

    Returns True if:
    - requests library is installed
    - secret.json exists and is valid (has AOC_COOKIE and YEAR)
    - YEAR is a reasonable value (2000-2100)

    Returns:
        True if API can be used, False otherwise

    Example:
        >>> if is_api_available():
        ...     data = get_input(day=1)
        ... else:
        ...     data = manually_get_input(day=1)
    """
    # Check if requests is available
    if not REQUESTS_AVAILABLE:
        return False

    # Try to load and validate secrets
    try:
        # Check environment variables first
        env_cookie = os.getenv("AOC_COOKIE")
        env_year = os.getenv("AOC_YEAR")

        if env_cookie and env_year:
            try:
                year_int = int(env_year)
                # Validate year is reasonable (2000-2100)
                if 2000 <= year_int <= 2100:
                    return True
            except ValueError:
                return False

        # Check secret.json files
        candidates = [
            Path(os.getcwd()) / _SECRET_FILE_NAME,
            Path(__file__).parent / _SECRET_FILE_NAME,
        ]

        for path in candidates:
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        secrets = json.load(file)

                    # Check required keys exist
                    if not all(key in secrets for key in _REQUIRED_SECRET_KEYS):
                        return False

                    # Validate cookie is not empty
                    cookie = secrets.get("AOC_COOKIE", "").strip()
                    if not cookie:
                        return False

                    # Validate year is reasonable
                    year_str = str(secrets.get("YEAR", "")).strip()
                    if not year_str:
                        return False

                    try:
                        year_int = int(year_str)
                        # Year should be between 2000 and 2100
                        if 2000 <= year_int <= 2100:
                            return True
                    except ValueError:
                        return False

                except (json.JSONDecodeError, PermissionError, IOError):
                    # Invalid JSON or can't read file
                    return False

        return False

    except Exception:
        # Any other error means API is not available
        return False


def load_input_from_file(file_name: str = "input.txt") -> List[str]:
    """
    Load input data from a specified file.

    If file_name is "input.txt", looks in the current working directory.
    Otherwise, treats file_name as a path (relative or absolute).

    Args:
        file_name: Name or path of the file to load (default: "input.txt")

    Returns:
        A list of strings, one per line of input (preserves empty lines).
        Returns empty list if file is empty.

    Raises:
        ValueError: If file_name is empty
        FileNotFoundError: If the file cannot be found
        IOError: If the file cannot be read
        PermissionError: If the file cannot be read due to permissions

    Example:
        >>> data = load_input_from_file("input.txt")
        >>> data = load_input_from_file("/path/to/custom_input.txt")
    """
    if not file_name or not file_name.strip():
        raise ValueError("file_name cannot be empty")

    if file_name == "input.txt":
        file_path = Path(os.getcwd()) / file_name
    else:
        file_path = Path(file_name)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path.absolute()}. "
            "Check that the path is correct and the file exists."
        )

    if not file_path.is_file():
        raise ValueError(f"Path exists but is not a file: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
            _logger.debug(f"Loaded {len(lines)} lines from {file_path}")
            return lines
    except PermissionError as e:
        raise PermissionError(
            f"Cannot read file '{file_path}' due to permissions: {e}"
        ) from e
    except IOError as e:
        raise IOError(
            f"Failed to read file '{file_path}': {e}. "
            "Check that the file is readable and not corrupted."
        ) from e
