"""
MultiGravity ForceAtlas2 layout — using compiled fa2 library for speed.

Falls back to igraph's Fruchterman-Reingold if fa2 is unavailable.
"""
from __future__ import annotations

import igraph as ig
import numpy as np

try:
    from fa2 import ForceAtlas2 as _FA2
    _HAS_FA2 = True
except ImportError:
    _HAS_FA2 = False


def compute_forceatlas2(
    g: ig.Graph,
    iterations: int = 100,
    scaling: float = 2.0,
    gravity: float = 1.0,
    strong_gravity: bool = False,
    barnes_hut: bool = True,
) -> list[tuple[float, float]]:
    """Compute ForceAtlas2 layout using the compiled fa2 library."""
    n = g.vcount()
    if n == 0:
        return []
    if n == 1:
        return [(0.0, 0.0)]

    if _HAS_FA2:
        fa2 = _FA2(
            outboundAttractionDistribution=True,  # MultiGravity (LinLog mode)
            scalingRatio=scaling,
            gravity=gravity,
            strongGravityMode=strong_gravity,
            barnesHutOptimize=barnes_hut,
            barnesHutTheta=1.2,
            verbose=False,
        )
        positions = fa2.forceatlas2_igraph_layout(
            g, pos=None, iterations=iterations
        )
        return [(float(x), float(y)) for x, y in positions]

    # Fallback: igraph's C-based Fruchterman-Reingold (very fast)
    layout = g.layout_fruchterman_reingold(niter=iterations)
    return [(float(x), float(y)) for x, y in layout.coords]
