"""Path -> arm controller adapter (dry-run by default).

The original team work contained separate painting/writing execution scripts
on the ArmPi/Hiwonder stack. Those hardware-specific files are not part of
this portfolio snapshot. This module keeps the integration seam explicit:

    path txt -> normalise -> ArmController.set_pitch_range_moving(...)

Implement ``ArmController`` with your own SDK adapter. The default
``DryRunController`` only prints the points, so reviewers can inspect the
trajectory without hardware.
"""
from __future__ import annotations

import argparse
import ast
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from src.trajectory.resize import resize_position


class ArmController(Protocol):
    """Minimal interface used by the execution loop."""

    def set_pitch_range_moving(
        self,
        point: tuple[float, float, float],
        pitch: float,
        roll_min: float,
        roll_max: float,
        speed: int,
    ) -> None:
        ...


@dataclass
class DryRunController:
    """Print points instead of moving hardware."""

    delay: float = 0.0
    moves: list[tuple[float, float, float]] = field(default_factory=list)

    def set_pitch_range_moving(
        self,
        point: tuple[float, float, float],
        pitch: float,
        roll_min: float,
        roll_max: float,
        speed: int,
    ) -> None:
        self.moves.append(point)
        print(f"move -> x={point[0]:.2f} y={point[1]:.2f} z={point[2]:.2f}")
        if self.delay:
            time.sleep(self.delay)


def load_paths(path_file: Path) -> list[list[list[float]]]:
    return ast.literal_eval(Path(path_file).read_text(encoding="utf-8"))


def z_for_y(y: float) -> float:
    """Small height adjustment used by the original writing script."""
    if y < 15:
        return 9.0
    if y < 20:
        return 10.0
    return 11.0


def execute(
    paths: list[list[list[float]]],
    controller: ArmController,
    *,
    limit: int | None = None,
    normalize: bool = False,
) -> int:
    """Send every point to the controller; return the number of moves."""
    if normalize:
        paths = resize_position(paths)
    count = 0
    for path in paths:
        for point in path:
            if limit is not None and count >= limit:
                return count
            x, y = point[0], point[1]
            controller.set_pitch_range_moving((x, y, z_for_y(y)), 0, -90, 0, 1000)
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Dry-run a trajectory through an arm interface.")
    parser.add_argument("--path", type=Path, default=Path("examples/cow/arm_path.txt"))
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()

    paths = load_paths(args.path)
    controller = DryRunController(delay=args.delay)
    count = execute(paths, controller, limit=args.limit, normalize=args.normalize)
    print(f"dry run: {count} moves from {args.path}")


if __name__ == "__main__":
    main()
