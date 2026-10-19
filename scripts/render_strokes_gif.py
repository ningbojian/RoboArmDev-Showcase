"""Render a stroke-order animation from a path txt using Pillow.

    python scripts/render_strokes_gif.py \
        --input examples/strokes/hua.txt \
        --out docs/images/stroke-order-hua.gif
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a stroke animation GIF.")
    parser.add_argument("--input", type=Path, default=Path("examples/strokes/hua.txt"))
    parser.add_argument("--out", type=Path, default=Path("docs/images/stroke-order-hua.gif"))
    parser.add_argument("--size", type=int, default=360)
    parser.add_argument("--stride", type=int, default=3, help="points per frame")
    args = parser.parse_args()

    paths = ast.literal_eval(args.input.read_text(encoding="utf-8"))
    points = [point for path in paths for point in path]
    if not points:
        raise SystemExit("empty path file")

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span = max(max_x - min_x, max_y - min_y) or 1
    margin = 20
    scale = (args.size - margin * 2) / span

    def project(point: tuple[float, float]) -> tuple[float, float]:
        return (
            margin + (point[0] - min_x) * scale,
            margin + (point[1] - min_y) * scale,
        )

    frames = []
    image = Image.new("RGB", (args.size, args.size), "white")
    draw = ImageDraw.Draw(image)
    flat_index = 0
    for path in paths:
        if len(path) < 2:
            continue
        for index in range(1, len(path), args.stride):
            draw.line([project(path[index - 1]), project(path[index])], fill="black", width=4)
            flat_index += 1
            if flat_index % 2 == 0:
                frames.append(image.copy())
    if not frames:
        frames.append(image)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        args.out,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=30,
    )
    print(f"wrote {len(frames)} frames to {args.out}")


if __name__ == "__main__":
    main()
