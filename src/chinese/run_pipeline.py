"""End-to-end Chinese writing pipeline (GIF -> mirrored GIF -> points -> path).

The original project downloaded stroke-order GIFs from a public dictionary
page. That crawler is intentionally not included because it depended on a
hard-coded session cookie and a third-party HTML layout. Supply a local GIF
that you are allowed to use instead.

Example:
    python -m src.chinese.run_pipeline \
        --gif examples/strokes/yong.gif --word yong --out-dir examples/strokes
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .gif_to_points import gif_to_points
from .points_to_path import points_to_path
from .reverse_gif import mirror_gif


def run(gif_path: Path, word: str, out_dir: Path) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    mirrored = out_dir / f"{word}_mirror.gif"
    points = out_dir / f"{word}_points.txt"
    path = out_dir / f"{word}_path.txt"

    mirror_gif(gif_path, mirrored)
    gif_to_points(mirrored, points)
    paths = points_to_path(points, path)
    strokes = len(paths)
    point_count = sum(len(item) for item in paths)
    print(f"{word}: {strokes} strokes / {point_count} points -> {path}")
    return points, path


def main() -> None:
    parser = argparse.ArgumentParser(description="Chinese stroke-order GIF to trajectory.")
    parser.add_argument("--gif", required=True, type=Path)
    parser.add_argument("--word", required=True, help="label used in output file names")
    parser.add_argument("--out-dir", type=Path, default=Path("examples/strokes"))
    args = parser.parse_args()
    run(args.gif, args.word, args.out_dir)


if __name__ == "__main__":
    main()
