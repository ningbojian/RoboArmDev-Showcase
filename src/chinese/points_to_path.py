"""Convert ``x,y`` point files into the path-list format used by the arm.

A ``-1,-1`` line starts a new stroke. The output is a Python literal
``[[[x, y], ...], ...]`` that the robot execution layer can read with
``ast.literal_eval``.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def points_to_path(
    point_path: Path,
    path_path: Path,
    *,
    negate_x: bool = False,
) -> list[list[list[float]]]:
    """Read a point txt and write a path txt; return the paths."""
    point_path = Path(point_path)
    path_path = Path(path_path)
    paths: list[list[list[float]]] = []
    current: list[list[float]] = []

    with point_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line == "-1,-1":
                if current:
                    paths.append(current)
                    current = []
                continue
            x_text, y_text = line.split(",", maxsplit=1)
            x = float(x_text)
            y = float(y_text)
            current.append([-x if negate_x else x, y])

    if current:
        paths.append(current)

    path_path.parent.mkdir(parents=True, exist_ok=True)
    path_path.write_text(str(paths), encoding="utf-8")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert point txt to path txt.")
    parser.add_argument("--points", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--negate-x", action="store_true", help="mirror x for the arm frame")
    args = parser.parse_args()
    paths = points_to_path(args.points, args.out, negate_x=args.negate_x)
    point_count = sum(len(path) for path in paths)
    print(f"wrote {len(paths)} strokes / {point_count} points to {args.out}")


if __name__ == "__main__":
    main()
