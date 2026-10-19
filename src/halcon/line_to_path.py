"""Extract line-art contours with HALCON and export drawing trajectories.

This is a cleaned version of the original ``drawPics/drawPic.py``. HALCON is
proprietary software; install HALCON 23.05 Progress (or a compatible release)
and its Python interface separately. No HALCON DLLs or licence files are
included in this repository.

The module can also render a preview of an existing path file without HALCON
using ``scripts/preview_path.py``.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def mirror_image(input_path: Path, output_path: Path, stretch_x: float = 1.5) -> Path:
    """Stretch, transpose and mirror the line art for the arm frame."""
    image = cv2.imread(str(input_path))
    if image is None:
        raise FileNotFoundError(f"cannot read image: {input_path}")
    image = cv2.resize(image, None, fx=stretch_x, fy=1, interpolation=cv2.INTER_LINEAR)
    image = cv2.flip(cv2.transpose(image), 1)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path


def _import_halcon():
    try:
        import halcon as ha  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "HALCON Python interface is not installed. Install HALCON 23.05 Progress "
            "and its Python package, or use scripts/preview_path.py with an existing path file."
        ) from exc
    return ha


def contours_to_paths(
    mirror_path: Path,
    *,
    sigma: float = 5.0,
    low: float = 0.0,
    high: float = 3.0,
) -> list[list[list[float]]]:
    """Run HALCON lines_gauss and convert every XLD contour to a point path."""
    ha = _import_halcon()
    image = ha.read_image(str(mirror_path))
    image = ha.rgb1_to_gray(image)
    lines = ha.lines_gauss(
        image,
        sigma,
        low,
        high,
        "dark",
        "true",
        "parabolic",
        "true",
    )
    count = ha.count_obj(lines)
    if isinstance(count, (tuple, list)):
        count = count[0]
    count = int(count)

    paths: list[list[list[float]]] = []
    for index in range(1, count + 1):
        contour = ha.select_obj(lines, index)
        rows, cols = ha.get_contour_xld(contour)
        paths.append([[float(col), float(row)] for row, col in zip(rows, cols)])
    return paths


def plot_paths(paths: list[list[list[float]]], output_path: Path) -> Path | None:
    """Render a path preview when matplotlib is available."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping preview")
        return None

    figure, axis = plt.subplots(figsize=(6, 6))
    for path in paths:
        if not path:
            continue
        xs, ys = zip(*[(point[0], point[1]) for point in path])
        axis.plot(xs, ys, linewidth=0.8)
    axis.invert_yaxis()
    axis.set_aspect("equal")
    axis.axis("off")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(figure)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="HALCON line art -> trajectory.")
    parser.add_argument("--input", type=Path, default=Path("examples/flower/lineart.png"))
    parser.add_argument("--mirror", type=Path, default=Path("examples/flower/mirror_halcon.png"))
    parser.add_argument("--out", type=Path, default=Path("examples/flower/path_halcon.txt"))
    parser.add_argument("--preview", type=Path, default=Path("docs/images/flower-path-preview.png"))
    parser.add_argument("--sigma", type=float, default=5.0)
    parser.add_argument("--low", type=float, default=0.0)
    parser.add_argument("--high", type=float, default=3.0)
    args = parser.parse_args()

    mirror_image(args.input, args.mirror)
    paths = contours_to_paths(args.mirror, sigma=args.sigma, low=args.low, high=args.high)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(str(paths), encoding="utf-8")
    print(f"wrote {len(paths)} contours to {args.out}")
    if args.preview:
        plot_paths(paths, args.preview)


if __name__ == "__main__":
    main()
