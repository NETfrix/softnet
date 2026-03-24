from __future__ import annotations

import numpy as np


def normalize_positions(
    positions: list[tuple[float, float]],
    width: float = 1000.0,
    height: float = 1000.0,
) -> list[tuple[float, float]]:
    """Normalize positions to fit within a bounding box centered at origin."""
    if not positions:
        return positions

    coords = np.array(positions, dtype=np.float64)
    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0

    # Center and scale
    centered = coords - (mins + maxs) / 2
    scale = min(width, height) / max(ranges)
    scaled = centered * scale

    return [(float(x), float(y)) for x, y in scaled]
