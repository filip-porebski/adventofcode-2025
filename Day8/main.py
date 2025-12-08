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
DAY: int = 8


def _parse_points(lines: List[str]) -> List[tuple[int, int, int]]:
    points: List[tuple[int, int, int]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        x, y, z = map(int, line.split(","))
        points.append((x, y, z))

    if not points:
        raise ValueError("No junction box coordinates found in the input.")

    return points


def _sorted_edges(points: List[tuple[int, int, int]]) -> List[tuple[int, int, int]]:
    edges: List[tuple[int, int, int]] = []
    for i, (x1, y1, z1) in enumerate(points):
        for j in range(i + 1, len(points)):
            x2, y2, z2 = points[j]
            dist_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2
            edges.append((dist_sq, i, j))
    edges.sort(key=lambda e: e[0])
    return edges


def _component_sizes_after_k_edges(points: List[tuple[int, int, int]], k: int) -> List[int]:
    """
    Connect the k closest pairs (by Euclidean distance) and return component sizes.
    """
    n = len(points)
    edges = _sorted_edges(points)

    parents = list(range(n))
    sizes = [1] * n

    def find(a: int) -> int:
        while parents[a] != a:
            parents[a] = parents[parents[a]]
            a = parents[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if sizes[ra] < sizes[rb]:
            ra, rb = rb, ra
        parents[rb] = ra
        sizes[ra] += sizes[rb]

    for _, a, b in edges[:k]:
        union(a, b)

    comp_sizes: List[int] = []
    for idx in range(n):
        root = find(idx)
        if root == idx:
            comp_sizes.append(sizes[root])

    comp_sizes.sort(reverse=True)
    return comp_sizes


def _final_connection_product(points: List[tuple[int, int, int]]) -> int:
    """
    Connect closest pairs until all points are in one component.
    Return the product of the X coordinates of the last pair merged.
    """
    n = len(points)
    edges = _sorted_edges(points)

    parents = list(range(n))
    sizes = [1] * n
    components = n

    def find(a: int) -> int:
        while parents[a] != a:
            parents[a] = parents[parents[a]]
            a = parents[a]
        return a

    def union(a: int, b: int) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if sizes[ra] < sizes[rb]:
            ra, rb = rb, ra
        parents[rb] = ra
        sizes[ra] += sizes[rb]
        return True

    for _, a, b in edges:
        if union(a, b):
            components -= 1
            if components == 1:
                return points[a][0] * points[b][0]

    raise ValueError("Graph did not become fully connected")


def solve_part_one(instructions: List[str], *, connections: int = 1000) -> int:
    if not instructions:
        return 0

    points = _parse_points(instructions)
    comp_sizes = _component_sizes_after_k_edges(points, k=connections)

    result = 1
    for size in comp_sizes[:3]:
        result *= size
    return result


def solve_part_two(instructions: List[str]) -> int:
    if not instructions:
        return 0

    points = _parse_points(instructions)
    return _final_connection_product(points)


def main() -> None:
    try:
        # Use API if available, otherwise use manual file loading
        if is_api_available():
            print("Using API to fetch input data...")
            example_data = get_example(DAY, part=1)
            puzzle_data = get_input(DAY)
        else:
            print("Using local files for input data...")
            example_data = manually_get_example(DAY)
            puzzle_data = manually_get_input(DAY)

        # Solve Part 1
        example_part1 = solve_part_one(example_data, connections=10)
        puzzle_part1 = solve_part_one(puzzle_data, connections=1000)

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
