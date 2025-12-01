#!/usr/bin/env python3
"""
Setup script for Advent of Code secrets.

This script helps you create or update secret.json with your session cookie.
You can get the session cookie from:
1. Chrome DevTools Network tab (look for 'session=' in cookie headers)
2. Chrome DevTools Application tab > Cookies > adventofcode.com
3. The curl command in Chrome's Network tab

Usage:
    python3 setup_secrets.py
    python3 setup_secrets.py --cookie "your_session_cookie_here"
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_current_year() -> int:
    """
    Get the current year from the system.

    Returns:
        Current year as integer (e.g., 2025)
    """
    return datetime.now().year


def extract_cookie_from_curl(curl_command: str) -> Optional[str]:
    """
    Extract session cookie from a curl command string.

    Args:
        curl_command: The curl command string (may be multi-line)

    Returns:
        The session cookie value if found, None otherwise
    """
    # Look for -b 'session=...' or --cookie 'session=...'
    import re

    # Pattern to match session cookie in curl command
    patterns = [
        r"-b\s+['\"]session=([^'\"]+)['\"]",
        r"--cookie\s+['\"]session=([^'\"]+)['\"]",
        r"session=([a-zA-Z0-9]+)",  # Fallback: just look for session=value
    ]

    for pattern in patterns:
        match = re.search(pattern, curl_command)
        if match:
            return match.group(1)

    return None


def read_chrome_cookie() -> Optional[str]:
    """
    Attempt to read the session cookie from Chrome's cookie database.

    This is a best-effort attempt and may not work if Chrome is running
    or if the database is locked.

    Returns:
        The session cookie value if found, None otherwise
    """
    try:
        import sqlite3

        # Chrome cookie database locations (macOS)
        cookie_paths = [
            Path.home()
            / "Library/Application Support/Google/Chrome/Default/Cookies",
            Path.home()
            / "Library/Application Support/Google/Chrome/Profile 1/Cookies",
        ]

        for cookie_path in cookie_paths:
            if not cookie_path.exists():
                continue

            try:
                # Copy database to temp location to avoid locking issues
                import tempfile
                import shutil

                with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                    tmp_path = tmp.name

                try:
                    shutil.copy2(cookie_path, tmp_path)

                    conn = sqlite3.connect(tmp_path)
                    cursor = conn.cursor()

                    # Query for adventofcode.com session cookie
                    cursor.execute(
                        """
                        SELECT value FROM cookies
                        WHERE host_key LIKE '%adventofcode.com%'
                        AND name = 'session'
                        ORDER BY creation_utc DESC
                        LIMIT 1
                    """
                    )

                    result = cursor.fetchone()
                    conn.close()

                    if result:
                        return result[0]

                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            except (sqlite3.Error, PermissionError, OSError):
                # Database might be locked or inaccessible
                continue

    except ImportError:
        # sqlite3 might not be available
        pass
    except Exception:
        # Any other error - just continue
        pass

    return None


def get_secret_file_path() -> Path:
    """
    Get the path where secret.json should be saved.

    Returns:
        Path to secret.json in the project root
    """
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    return project_root / "secret.json"


def load_existing_secrets() -> Optional[dict]:
    """
    Load existing secrets if secret.json exists.

    Returns:
        Dictionary with existing secrets, or None if file doesn't exist
    """
    secret_path = get_secret_file_path()

    if not secret_path.exists():
        return None

    try:
        with open(secret_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_secrets(cookie: str, year: int, overwrite: bool = False) -> bool:
    """
    Save secrets to secret.json.

    Args:
        cookie: The AOC session cookie
        year: The year (e.g., 2025)
        overwrite: If True, overwrite existing file without asking

    Returns:
        True if saved successfully, False if cancelled
    """
    secret_path = get_secret_file_path()
    existing = load_existing_secrets()

    if existing and not overwrite:
        print(f"\n⚠️  secret.json already exists at: {secret_path}")
        print(f"   Current AOC_COOKIE: {existing.get('AOC_COOKIE', 'N/A')[:20]}...")
        print(f"   Current YEAR: {existing.get('YEAR', 'N/A')}")

        while True:
            response = input("\nOverwrite existing secret.json? (yes/no): ").strip().lower()
            if response in ("yes", "y"):
                break
            elif response in ("no", "n"):
                print("Cancelled. No changes made.")
                return False
            else:
                print("Please enter 'yes' or 'no'")

    secrets = {
        "AOC_COOKIE": cookie.strip(),
        "YEAR": str(year),
    }

    try:
        with open(secret_path, "w", encoding="utf-8") as f:
            json.dump(secrets, f, indent=2)

        # Set restrictive permissions (owner read/write only)
        os.chmod(secret_path, 0o600)

        print(f"\n✓ Successfully saved secret.json to: {secret_path}")
        print(f"  AOC_COOKIE: {cookie[:20]}...")
        print(f"  YEAR: {year}")
        print(f"  Permissions: 600 (owner read/write only)")

        return True

    except IOError as e:
        print(f"\n✗ Error saving secret.json: {e}", file=sys.stderr)
        return False


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Setup Advent of Code secrets (session cookie)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (will prompt for cookie)
  python3 setup_secrets.py

  # Provide cookie directly
  python3 setup_secrets.py --cookie "your_session_cookie_here"

  # Extract from curl command
  python3 setup_secrets.py --curl "curl 'https://...' -b 'session=XXX' ..."

  # Try to read from Chrome automatically
  python3 setup_secrets.py --from-chrome

Notes:
  - You can find your session cookie in Chrome DevTools:
    1. Open DevTools (F12)
    2. Go to Network tab
    3. Reload the page
    4. Click on any request
    5. Look for 'Cookie' header with 'session=...'
  - Or in Application tab > Cookies > adventofcode.com > session
        """,
    )

    parser.add_argument(
        "--cookie",
        type=str,
        help="Session cookie value directly",
    )
    parser.add_argument(
        "--curl",
        type=str,
        help="Extract cookie from curl command (paste the full curl command)",
    )
    parser.add_argument(
        "--from-chrome",
        action="store_true",
        help="Try to automatically read cookie from Chrome's cookie database",
    )
    parser.add_argument(
        "--year",
        type=int,
        help=f"Year to use (default: {get_current_year()})",
        default=get_current_year(),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing secret.json without asking",
    )

    args = parser.parse_args()

    cookie: Optional[str] = None
    year = args.year

    # Try to get cookie from various sources
    if args.cookie:
        cookie = args.cookie
        print("✓ Using cookie from --cookie argument")
    elif args.curl:
        cookie = extract_cookie_from_curl(args.curl)
        if cookie:
            print("✓ Extracted cookie from curl command")
        else:
            print("✗ Could not extract cookie from curl command", file=sys.stderr)
            print("  Make sure the curl command contains 'session=...'", file=sys.stderr)
            sys.exit(1)
    elif args.from_chrome:
        print("Attempting to read cookie from Chrome...")
        cookie = read_chrome_cookie()
        if cookie:
            print("✓ Successfully read cookie from Chrome")
        else:
            print("✗ Could not read cookie from Chrome", file=sys.stderr)
            print("  Make sure Chrome is closed, or provide cookie manually", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        print("=" * 60)
        print("Advent of Code Secret Setup")
        print("=" * 60)
        print()
        print("You can get your session cookie from:")
        print("  1. Chrome DevTools > Network tab > Request headers > Cookie")
        print("  2. Chrome DevTools > Application > Cookies > adventofcode.com")
        print("  3. Copy the 'session=...' value from a curl command")
        print()
        print("Or use one of these options:")
        print("  --cookie 'your_cookie'     : Provide cookie directly")
        print("  --curl 'curl ...'          : Extract from curl command")
        print("  --from-chrome              : Try to read from Chrome")
        print()

        cookie_input = input("Enter your session cookie (or paste curl command): ").strip()

        if not cookie_input:
            print("No cookie provided. Exiting.", file=sys.stderr)
            sys.exit(1)

        # Check if it looks like a curl command
        if cookie_input.startswith("curl") or "session=" in cookie_input:
            cookie = extract_cookie_from_curl(cookie_input)
            if not cookie:
                print("Could not extract cookie. Please provide just the cookie value.", file=sys.stderr)
                sys.exit(1)
        else:
            cookie = cookie_input

    if not cookie:
        print("Error: No cookie found", file=sys.stderr)
        sys.exit(1)

    # Validate cookie format (should be alphanumeric, typically long)
    if len(cookie) < 10:
        print("⚠️  Warning: Cookie seems unusually short", file=sys.stderr)
        response = input("Continue anyway? (yes/no): ").strip().lower()
        if response not in ("yes", "y"):
            sys.exit(1)

    # Save secrets
    if save_secrets(cookie, year, overwrite=args.overwrite):
        print("\n✓ Setup complete! You can now use API functions in your solutions.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

