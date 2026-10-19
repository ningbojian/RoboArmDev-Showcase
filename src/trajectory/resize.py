"""Fit a trajectory into a compact arm workspace.

The original ``resizeCoordinates/main.py`` scaled every stroke so that the
longest side of the bounding box was at most 20 units, then translated the
trajectory so its maximum x/y landed at the configured workspace anchor
(10, 30). This module keeps the same behaviour but accepts paths explicitly.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

PathList = list[list[list[float]]]


def resize_position(
    paths: PathList,
    *,
    size: float = 20.0,
    x_anchor: float = 10.0,
    y_anchor: float = 30.0,
) -> PathList:
    """Scale and translate ``paths`` into the configured workspace."""
    if not paths:
        return paths

    xs = [point[0] for path in paths for point in path]
    ys = [point[1] for path in paths for point in path]
    if not xs or not ys:
        return paths

    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    if width > size or height > size:
        ratio = max(width / size, height / size)
        for path in paths:
            for point in path:
                point[0] /= ratio
                point[1] /= ratio

    x_max = max(point[0] for path in paths for point in path)
    y_max = max(point[1] for path in paths for point in path)
    x_move = x_anchor - x_max
    y_move = y_anchor - y_max
    for path in paths:
        for point in path:
            point[0] += x_move
            point[1] += y_move
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalise a trajectory path file.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="optional output path txt")
    args = parser.parse_args()
    paths = ast.literal_eval(args.input.read_text(encoding="utf-8"))
    result = resize_position(paths)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(str(result), encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(result)


if __name__ == "__main__":
    main()
