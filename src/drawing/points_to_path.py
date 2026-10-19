"""Convert mouse-drawing points to an arm path (x is mirrored)."""
from __future__ import annotations

import argparse
from pathlib import Path


def points_to_path(point_path: Path, path_path: Path) -> list[list[list[float]]]:
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
            current.append([-float(x_text), float(y_text)])

    if current:
        paths.append(current)
    path_path.parent.mkdir(parents=True, exist_ok=True)
    path_path.write_text(str(paths), encoding="utf-8")
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert drawing points to a path.")
    parser.add_argument("--points", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    paths = points_to_path(args.points, args.out)
    print(f"wrote {len(paths)} strokes to {args.out}")


if __name__ == "__main__":
    main()
