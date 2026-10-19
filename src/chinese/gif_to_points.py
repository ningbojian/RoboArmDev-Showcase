"""Convert a stroke-order GIF into ordered pen points.

The original team pipeline split GIF frames, diffed consecutive frames,
removed noise with morphology, extracted contour centres, and interpolated
points so the trajectory is dense enough for a six-axis arm.

This is a cleaned, path-parameterised version of the original
``writeChinese/gif2Point.py``. It does not download GIFs and contains no
cookies or credentials.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def read_gif_frames(gif_path: Path, size: tuple[int, int] = (256, 256)) -> list[np.ndarray]:
    """Return every GIF frame as a 256x256 grayscale image."""
    frames: list[np.ndarray] = []
    with Image.open(gif_path) as image:
        for index in range(getattr(image, "n_frames", 1)):
            image.seek(index)
            frame = image.convert("RGB").resize(size)
            frames.append(cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2GRAY))
    return frames


def _contour_centres(previous: np.ndarray, current: np.ndarray, min_area: int = 20):
    """Find centres of newly painted regions between two frames."""
    diff = cv2.absdiff(current, previous)
    diff = cv2.medianBlur(diff, 3)
    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    kernel5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel5)
    diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel3)
    _, threshold = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    found = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # OpenCV 3 returns (image, contours, hierarchy); OpenCV 4 returns
    # (contours, hierarchy).
    contours = found[1] if len(found) == 3 else found[0]
    centres: list[tuple[int, int]] = []
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        if width * height > min_area:
            centres.append((x + width // 2, y + height // 2))
    return centres


def _interpolate(start: tuple[int, int], end: tuple[int, int], count: int = 8):
    """Return equally spaced points between start and end (excluding start)."""
    x_step = (end[0] - start[0]) / (count + 1)
    y_step = (end[1] - start[1]) / (count + 1)
    return [
        (int(round(start[0] + x_step * index)), int(round(start[1] + y_step * index)))
        for index in range(1, count + 1)
    ]


def gif_to_points(
    gif_path: Path,
    point_path: Path,
    *,
    min_area: int = 20,
    max_jump: int = 40,
) -> list[tuple[int, int]]:
    """Extract an ordered point list from a stroke-order GIF.

    Points are written as ``x,y`` lines. A ``-1,-1`` line starts a new stroke.
    """
    gif_path = Path(gif_path)
    point_path = Path(point_path)
    frames = read_gif_frames(gif_path)
    if len(frames) < 2:
        raise ValueError("GIF must contain at least two frames")

    points: list[tuple[int, int]] = []
    previous = frames[0]
    previous_point: tuple[int, int] | None = None

    for current in frames[1:]:
        centres = _contour_centres(previous, current, min_area=min_area)
        if not centres:
            if previous_point is not None:
                points.append((-1, -1))
                previous_point = None
            previous = current
            continue

        for centre in centres:
            if previous_point is None:
                points.append(centre)
            else:
                distance = math.dist(previous_point, centre)
                if distance > max_jump:
                    points.append((-1, -1))
                else:
                    points.extend(_interpolate(previous_point, centre, 8))
                points.append(centre)
            previous_point = centre
        previous = current

    point_path.parent.mkdir(parents=True, exist_ok=True)
    with point_path.open("w", encoding="utf-8") as handle:
        for x, y in points:
            handle.write(f"{x},{y}\n")
    return points


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a stroke-order GIF to point coordinates.")
    parser.add_argument("--gif", required=True, type=Path, help="input GIF")
    parser.add_argument("--out", required=True, type=Path, help="output point txt")
    parser.add_argument("--min-area", type=int, default=20)
    parser.add_argument("--max-jump", type=int, default=40)
    args = parser.parse_args()
    points = gif_to_points(args.gif, args.out, min_area=args.min_area, max_jump=args.max_jump)
    print(f"wrote {len(points)} points to {args.out}")


if __name__ == "__main__":
    main()
