"""Optional upstream image -> stylised line-art module.

Original author in the team repository: **Dii**. This file is included only so
the complete image -> line -> trajectory chain is understandable; it is not
the repository owner's work.

Requirements: TensorFlow 2.x + tensorflow-hub (see ``requirements-ml.txt``).
The TF-Hub model URL is an external dependency and may change over time.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def remove_background(image_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """GrabCut foreground removal with a white background."""
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"cannot read image: {image_path}")
    mask = np.zeros(image.shape[:2], np.uint8)
    background_model = np.zeros((1, 65), np.float64)
    foreground_model = np.zeros((1, 65), np.float64)
    height, width = image.shape[:2]
    rect = (50, 50, width - 50, height - 50)
    cv2.grabCut(image, mask, rect, background_model, foreground_model, 5, cv2.GC_INIT_WITH_RECT)
    foreground = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    result = image * foreground[:, :, np.newaxis]
    background = np.ones_like(image) * 255
    background = cv2.bitwise_and(background, background, mask=1 - foreground)
    return cv2.add(result, background), foreground


def _centre_crop(image: np.ndarray, size: int) -> np.ndarray:
    height, width = image.shape[:2]
    side = min(height, width)
    top = (height - side) // 2
    left = (width - side) // 2
    image = image[top : top + side, left : left + side]
    return cv2.resize(image, (size, size), interpolation=cv2.INTER_LINEAR)


def stylize(
    content_path: Path,
    style_path: Path,
    output_path: Path,
    *,
    size: int = 256,
) -> Path:
    """Apply arbitrary image stylisation and keep the foreground mask."""
    import tensorflow as tf
    import tensorflow_hub as hub
    from PIL import Image

    content, foreground = remove_background(content_path)
    content = _centre_crop(content, size)
    content = cv2.cvtColor(content, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    style = cv2.imread(str(style_path))
    if style is None:
        raise FileNotFoundError(f"cannot read image: {style_path}")
    style = _centre_crop(style, size)
    style = cv2.cvtColor(style, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    module = hub.load(
        "https://www.kaggle.com/models/google/arbitrary-image-stylization-v1/TensorFlow1/256/2"
    )
    outputs = module(tf.constant(content[None, ...]), tf.constant(style[None, ...]))
    stylized = outputs[0][0].numpy()

    mask = cv2.resize(foreground, (stylized.shape[1], stylized.shape[0]), interpolation=cv2.INTER_NEAREST)
    mask = mask[..., np.newaxis]
    result = stylized * mask + (1.0 - mask)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((result * 255).clip(0, 255).astype(np.uint8)).save(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Image -> stylised line art (optional).")
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--style", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(f"wrote {stylize(args.content, args.style, args.out)}")


if __name__ == "__main__":
    main()
