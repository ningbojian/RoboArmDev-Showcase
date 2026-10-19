"""Capture a mouse drawing and export it as an arm trajectory.

Run:
    python -m src.drawing.repeat_drawing --out-dir examples/drawing

Left button draws, ``q`` finishes. The x axis is mirrored to match the arm
coordinate frame.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from .points_to_path import points_to_path


def capture(out_dir: Path, size: int = 500) -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    points_path = out_dir / "drawing_points.txt"
    path_path = out_dir / "drawing_path.txt"

    canvas = np.full((size, size), 255, dtype=np.uint8)
    strokes: list[list[tuple[int, int]]] = []
    current: list[tuple[int, int]] = []
    drawing = False

    def on_mouse(event, x, y, _flags, _param):
        nonlocal drawing, current
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            current = [(x, y)]
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            if current:
                cv2.line(canvas, current[-1], (x, y), 0, 2, cv2.LINE_AA)
            current.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP and drawing:
            drawing = False
            if len(current) > 1:
                strokes.append(current)
            current = []

    cv2.namedWindow("draw")
    cv2.setMouseCallback("draw", on_mouse)
    print("Left button draws; press q in the window to finish.")
    while True:
        cv2.imshow("draw", canvas)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()

    if drawing and len(current) > 1:
        strokes.append(current)
    if not strokes:
        raise SystemExit("No strokes captured.")

    with points_path.open("w", encoding="utf-8") as handle:
        for stroke in strokes:
            for x, y in stroke:
                handle.write(f"{x},{y}\n")
            handle.write("-1,-1\n")

    points_to_path(points_path, path_path)
    print(f"wrote {len(strokes)} strokes to {path_path}")
    return points_path, path_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture a mouse drawing.")
    parser.add_argument("--out-dir", type=Path, default=Path("examples/drawing"))
    parser.add_argument("--size", type=int, default=500)
    args = parser.parse_args()
    capture(args.out_dir, args.size)


if __name__ == "__main__":
    main()
