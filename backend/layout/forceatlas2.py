from __future__ import annotations

import igraph as ig
import numpy as np


def compute_forceatlas2(
    g: ig.Graph,
    iterations: int = 100,
    scaling: float = 2.0,
    gravity: float = 1.0,
    strong_gravity: bool = False,
    barnes_hut: bool = True,
) -> list[tuple[float, float]]:
    """
    Compute ForceAtlas2 layout.

    Uses the fa2 library with Barnes-Hut optimization for large graphs.
    Falls back to igraph layout_fruchterman_reingold if fa2 is unavailable.
    """
    try:
        from fa2 import ForceAtlas2

        fa = ForceAtlas2(
            outboundAttractionDistribution=True,
            linLogMode=False,
            adjustSizes=False,
            edgeWeightInfluence=1.0,
            jitterTolerance=1.0,
            barnesHutOptimize=barnes_hut,
            barnesHutTheta=1.2,
            scalingRatio=scaling,
            strongGravityMode=strong_gravity,
            gravity=gravity,
            verbose=False,
        )

        # fa2 needs a networkx-like or adjacency input
        # Convert igraph to edge list for fa2
        positions = _fa2_from_igraph(g, fa, iterations)
        return positions

    except ImportError:
        # Fallback to igraph's Fruchterman-Reingold (similar force-directed)
        layout = g.layout_fruchterman_reingold(niter=iterations)
        return [(coord[0], coord[1]) for coord in layout]


def _fa2_from_igraph(
    g: ig.Graph, fa, iterations: int
) -> list[tuple[float, float]]:
    """Run ForceAtlas2 using igraph adjacency."""
    n = g.vcount()

    # Initial random positions
    rng = np.random.default_rng(42)
    positions = rng.uniform(-100, 100, size=(n, 2)).tolist()

    # Build adjacency as edge list for fa2
    # fa2 expects a graph object — use igraph's adjacency matrix
    adj = g.get_adjacency_sparse()

    try:
        positions = fa.forceatlas2(adj, pos=positions, iterations=iterations)
    except Exception:
        # Some fa2 versions take different args
        positions = fa.forceatlas2_networkx_layout(
            _igraph_to_nx_compat(g), pos=None, iterations=iterations
        )
        positions = list(positions.values())

    return [(p[0], p[1]) for p in positions]


def _igraph_to_nx_compat(g: ig.Graph):
    """Create a minimal networkx-compatible graph for fa2."""
    try:
        import networkx as nx

        if g.is_directed():
            nxg = nx.DiGraph()
        else:
            nxg = nx.Graph()
        nxg.add_nodes_from(range(g.vcount()))
        edges = [(e.source, e.target) for e in g.es]
        nxg.add_edges_from(edges)
        return nxg
    except ImportError:
        raise ImportError("ForceAtlas2 fallback requires networkx")
