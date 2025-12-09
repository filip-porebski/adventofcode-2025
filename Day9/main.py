from pathlib import Path
import sys
from typing import List

# Add parent directory to path for helper imports
parent_directory = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_directory))

from helper import (  # noqa: E402
    get_example,
    get_input,
    is_api_available,
    manually_get_example,
    manually_get_input,
)

# Constants
DAY: int = 9


def solve_part_one(instructions: List[str]) -> int:
    points = []

    for line in instructions:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            x_str, y_str = stripped.split(",")
            x, y = int(x_str), int(y_str)
        except ValueError as exc:
            raise ValueError(f"Invalid coordinate line: {line!r}") from exc
        points.append((x, y))

    max_area = 0
    total = len(points)
    if total < 2:
        return 0

    # Check every pair of points as opposite rectangle corners
    for i in range(total):
        x1, y1 = points[i]
        for j in range(i + 1, total):
            x2, y2 = points[j]
            width = abs(x1 - x2) + 1
            height = abs(y1 - y2) + 1
            area = width * height
            if area > max_area:
                max_area = area

    return max_area


def solve_part_two(instructions: List[str]) -> int:
    points = []

    for line in instructions:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            x_str, y_str = stripped.split(",")
            x, y = int(x_str), int(y_str)
        except ValueError as exc:
            raise ValueError(f"Invalid coordinate line: {line!r}") from exc
        points.append((x, y))

    if len(points) < 2:
        return 0

    n = len(points)

    # Coordinate compression to keep the grid tiny even when coordinates are huge.
    min_x = min(x for x, _ in points)
    max_x = max(x for x, _ in points)
    min_y = min(y for _, y in points)
    max_y = max(y for _, y in points)

    xs_set = {min_x - 1, max_x + 2}
    ys_set = {min_y - 1, max_y + 2}
    for x, y in points:
        xs_set.update([x, x + 1])
        ys_set.update([y, y + 1])

    xs = sorted(xs_set)
    ys = sorted(ys_set)
    x_index = {v: i for i, v in enumerate(xs)}
    y_index = {v: i for i, v in enumerate(ys)}

    widths = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    heights = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]

    width_n = len(widths)
    height_n = len(heights)

    allowed = [[False] * height_n for _ in range(width_n)]

    # Mark polygon boundary (reds and the green edges between them).
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        if x1 != x2 and y1 != y2:
            raise ValueError("Edges must be axis-aligned")
        if x1 == x2:
            ix = x_index[x1]
            y_start, y_end = sorted((y1, y2))
            y_start_idx = y_index[y_start]
            y_end_idx = y_index[y_end + 1]
            for iy in range(y_start_idx, y_end_idx):
                allowed[ix][iy] = True
        else:
            iy = y_index[y1]
            x_start, x_end = sorted((x1, x2))
            x_start_idx = x_index[x_start]
            x_end_idx = x_index[x_end + 1]
            for ix in range(x_start_idx, x_end_idx):
                allowed[ix][iy] = True

    # Flood-fill in compressed space to find exterior, then mark interior as allowed.
    from collections import deque

    visited = [[False] * height_n for _ in range(width_n)]
    q: deque[tuple[int, int]] = deque()

    def enqueue(x: int, y: int) -> None:
        if 0 <= x < width_n and 0 <= y < height_n and not visited[x][y] and not allowed[x][y]:
            visited[x][y] = True
            q.append((x, y))

    for x in range(width_n):
        enqueue(x, 0)
        enqueue(x, height_n - 1)
    for y in range(height_n):
        enqueue(0, y)
        enqueue(width_n - 1, y)

    while q:
        cx, cy = q.popleft()
        enqueue(cx + 1, cy)
        enqueue(cx - 1, cy)
        enqueue(cx, cy + 1)
        enqueue(cx, cy - 1)

    for x in range(width_n):
        for y in range(height_n):
            if not visited[x][y]:
                allowed[x][y] = True

    # Weighted prefix sums (compressed areas)
    prefix = [[0] * (height_n + 1) for _ in range(width_n + 1)]
    for x in range(1, width_n + 1):
        row_sum = 0
        for y in range(1, height_n + 1):
            area = widths[x - 1] * heights[y - 1] if allowed[x - 1][y - 1] else 0
            row_sum += area
            prefix[x][y] = prefix[x - 1][y] + row_sum

    def rect_area_sum(x0: int, x1: int, y0: int, y1: int) -> int:
        """Sum of allowed area for rectangle spanning tiles x0..x1, y0..y1 inclusive."""
        lx = x_index[x0]
        rx = x_index[x1 + 1]
        ly = y_index[y0]
        ry = y_index[y1 + 1]
        return prefix[rx][ry] - prefix[lx][ry] - prefix[rx][ly] + prefix[lx][ly]

    max_area = 0
    for i in range(n):
        x1, y1 = points[i]
        for j in range(i + 1, n):
            x2, y2 = points[j]
            width_tiles = abs(x1 - x2) + 1
            height_tiles = abs(y1 - y2) + 1
            area_tiles = width_tiles * height_tiles
            if area_tiles <= max_area:
                continue
            if rect_area_sum(min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)) == area_tiles:
                max_area = area_tiles

    return max_area


def main() -> None:
    try:
        # Use API if available, otherwise use manual file loading
        if is_api_available():
            print("Using API to fetch input data...")
            try:
                example_data = get_example(DAY, part=1)
                puzzle_data = get_input(DAY)
            except Exception:
                print("API fetch failed, falling back to local files...")
                example_data = manually_get_example(DAY)
                puzzle_data = manually_get_input(DAY)
        else:
            print("Using local files for input data...")
            example_data = manually_get_example(DAY)
            puzzle_data = manually_get_input(DAY)

        # Solve Part 1
        example_part1 = solve_part_one(example_data)
        puzzle_part1 = solve_part_one(puzzle_data)

        print(f"Part 1 - Example: {example_part1}")
        print(f"Part 1 - Puzzle: {puzzle_part1}")
        print()

        # Solve Part 2
        example_part2 = solve_part_two(example_data)
        puzzle_part2 = solve_part_two(puzzle_data)

        print(f"Part 2 - Example: {example_part2}")
        print(f"Part 2 - Puzzle: {puzzle_part2}")

    except FileNotFoundError as e:
        print(f"Error: Could not find input file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid input format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
