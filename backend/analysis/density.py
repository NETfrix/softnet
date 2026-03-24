from __future__ import annotations

import igraph as ig


def graph_density(g: ig.Graph) -> dict:
    """Compute graph density."""
    return {
        "density": g.density(),
        "directed": g.is_directed(),
    }
