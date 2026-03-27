"""
ForceAtlas2 layout — uses compiled fa2 library when available,
falls back to igraph's C-based force-directed layouts for speed.
"""
from __future__ import annotations

import igraph as ig

try:
    from fa2 import ForceAtlas2 as _FA2
    _HAS_FA2 = True
except Exception:
    _HAS_FA2 = False


def compute_forceatlas2(
    g: ig.Graph,
    iterations: int = 100,
    scaling: float = 2.0,
    gravity: float = 1.0,
    strong_gravity: bool = True,
    barnes_hut: bool = True,
) -> list[tuple[float, float]]:
    """Compute ForceAtlas2 layout.

    Uses the compiled fa2 library if available (Gephi-speed).
    Falls back to igraph's C-based Fruchterman-Reingold which is
    also fast and produces similar force-directed results.
    """
    n = g.vcount()
    if n == 0:
        return []
    if n == 1:
        return [(0.0, 0.0)]

    if _HAS_FA2:
        try:
            fa2 = _FA2(
                outboundAttractionDistribution=False,
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
        except Exception:
            pass  # fall through to igraph

    # Fallback: igraph's C-based force-directed layout (very fast)
    if n > 5000:
        layout = g.layout_drl(options="default")
    else:
        layout = g.layout_fruchterman_reingold(
            niter=iterations,
            grid="auto",
        )
    return [(float(x), float(y)) for x, y in layout.coords]
