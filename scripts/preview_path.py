"""Render a path txt (Python list of strokes) as a PNG preview.

This works without HALCON or TensorFlow:
    python scripts/preview_path.py \
        --input examples/flower/path.txt \
        --out docs/images/flower-path-preview.png
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview a trajectory path file.")
    parser.add_argument("--input", type=Path, default=Path("examples/flower/path.txt"))
    parser.add_argument("--out", type=Path, default=Path("docs/images/flower-path-preview.png"))
    parser.add_argument("--title", default="")
    args = parser.parse_args()

    paths = ast.literal_eval(args.input.read_text(encoding="utf-8"))
    figure, axis = plt.subplots(figsize=(6, 6))
    for path in paths:
        if not path:
            continue
        xs, ys = zip(*[(point[0], point[1]) for point in path])
        axis.plot(xs, ys, linewidth=0.9)
    axis.invert_yaxis()
    axis.set_aspect("equal")
    axis.axis("off")
    if args.title:
        axis.set_title(args.title)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.out, dpi=150, bbox_inches="tight", pad_inches=0.04)
    plt.close(figure)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
