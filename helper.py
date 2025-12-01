import requests
import json
import os

# Lazy-loaded secrets: don't try to read secret.json at import time so the module
# can be imported even when secret.json is missing (useful for manually_get_* helpers).
_secrets_cache = None

def _load_secrets():
    """Load and cache secrets from secret.json.

    Search order:
    1. current working directory (useful when running a script from project root)
    2. this module's directory (useful when running as a module)

    Raises FileNotFoundError only when called and no secret file is found.
    """
    global _secrets_cache
    if _secrets_cache is not None:
        return _secrets_cache

    candidates = [
        os.path.join(os.getcwd(), "secret.json"),
        os.path.join(os.path.dirname(__file__), "secret.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path) as file:
                _secrets_cache = json.load(file)
                return _secrets_cache

    raise FileNotFoundError(
        "secret.json not found in current working directory or module directory. "
        "Place a secret.json with keys 'AOC_COOKIE' and 'YEAR', or use the manual input helpers."
    )


def _get_aoc_creds():
    """Return (AOC_COOKIE, YEAR) from secrets.

    Centralises extraction and gives a clearer error when keys are missing.
    """
    secrets = _load_secrets()
    try:
        return secrets["AOC_COOKIE"], secrets["YEAR"]
    except KeyError as e:
        raise KeyError(f"secret.json missing required key: {e}")


def get_input(day: int, part=None):
    AOC_COOKIE, YEAR = _get_aoc_creds()

    req = requests.get(
        f"https://adventofcode.com/{YEAR}/day/{day}/input",
        headers={"cookie": "session=" + AOC_COOKIE},
    )

    if req.text[-1] == "\n":
        return req.text[:-1].strip().split("\n")
    else:
        return req.text.strip().split("\n")


def get_example(day: int, part: int = 1):
    AOC_COOKIE, YEAR = _get_aoc_creds()
    req = requests.get(
        f"https://adventofcode.com/{YEAR}/day/{day}",
        headers={"cookie": "session=" + AOC_COOKIE},
    )
    return (
        req.text.split("<pre><code>")[part]
        .split("</code></pre>")[0]
        .strip()
        .split("\n")
    )

def manually_get_input(day: int, part=None):
    # Get it manually from the text file that's in the program using this helper function folder
    # Look for the per-day folder (e.g. Day1/day1_input.txt) adjacent to the repo root
    day_dir = os.path.join(os.path.dirname(__file__), f"Day{day}")
    file_path = os.path.join(day_dir, f"day{day}_input.txt")
    with open(file_path) as file:
        return file.read().strip().split("\n")
    
def manually_get_example(day: int, part: int = 1):
    # Get it manually from the text file that's in the program using this helper function folder
    # Look for the per-day folder (e.g. Day1/day1_example.txt) adjacent to the repo root
    day_dir = os.path.join(os.path.dirname(__file__), f"Day{day}")
    file_path = os.path.join(day_dir, f"day{day}_example.txt")
    with open(file_path) as file:
        return file.read().strip().split("\n")


def submit_answer(day: int, level: int, answer: str):
    print("You are about to submit the following answer:")
    print(answer)
    input("Press enter to continue or Ctrl+C to abort. \n")
    data = {"level": str(level), "answer": str(answer)}
    AOC_COOKIE, YEAR = _get_aoc_creds()

    response = requests.post(
        f"https://adventofcode.com/{YEAR}/day/{day}/answer",
        headers={"cookie": "session=" + AOC_COOKIE},
        data=data,
    )
    if "You gave an answer too recently" in response.text:
        # You will get this if you submitted a wrong answer less than 60s ago.
        print("VERDICT : TOO MANY REQUESTS")
    elif "not the right answer" in response.text:
        if "too low" in response.text:
            print("VERDICT : WRONG (TOO LOW)")
        elif "too high" in response.text:
            print("VERDICT : WRONG (TOO HIGH)")
        else:
            print("VERDICT : WRONG (UNKNOWN)")
    elif "seem to be solving the right level." in response.text:
        # You will get this if you submit on a level you already solved.
        # Usually happens when you forget to switch from `PART = 1` to `PART = 2`
        print("VERDICT : ALREADY SOLVED")
    else:
        print("VERDICT : OK !")


def load_input_from_file(file_name: str = "input.txt"):
    if file_name == "input.txt":
        file_path = os.path.join(os.getcwd(), file_name)
    else:
        file_path = file_name

    with open(file_path) as file:
        return file.read().splitlines()
