"""Mirror a stroke-order GIF horizontally.

The arm workspace is mirrored relative to the image coordinate system, so the
team mirrored each GIF before extracting points.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def mirror_gif(gif_path: Path, output_path: Path) -> Path:
    """Write a horizontally mirrored copy of ``gif_path``."""
    gif_path = Path(gif_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(gif_path) as image:
        frames = []
        durations = []
        try:
            while True:
                frames.append(image.copy().transpose(Image.FLIP_LEFT_RIGHT))
                durations.append(image.info.get("duration", 100))
                image.seek(image.tell() + 1)
        except EOFError:
            pass

    if not frames:
        raise ValueError(f"no frames found in {gif_path}")
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=durations,
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Mirror a GIF horizontally.")
    parser.add_argument("--gif", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    mirror_gif(args.gif, args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
