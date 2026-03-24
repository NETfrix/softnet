from __future__ import annotations

import igraph as ig


def compute_yifan_hu(g: ig.Graph) -> list[tuple[float, float]]:
    """
    Compute Yifan Hu layout using igraph's DrL (Distributed Recursive Layout).

    DrL is a multi-level force-directed layout similar to Yifan Hu's algorithm,
    suitable for large graphs. Falls back to graphopt for very large graphs.
    """
    n = g.vcount()

    if n > 50000:
        # For very large graphs, use layout_drl which is optimized for scale
        layout = g.layout_drl()
    else:
        # layout_graphopt is closer to Yifan Hu for moderate graphs
        layout = g.layout_graphopt(niter=500, node_charge=0.001)

    return [(coord[0], coord[1]) for coord in layout]
