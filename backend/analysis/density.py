from __future__ import annotations

from collections import Counter

import igraph as ig


def graph_density(g: ig.Graph) -> dict:
    """Compute graph density."""
    return {
        "density": g.density(),
        "directed": g.is_directed(),
    }


def connected_components(g: ig.Graph) -> dict:
    """Compute connected components: count, sizes, largest component ID."""
    mode = "strong" if g.is_directed() else "weak"
    components = g.connected_components(mode=mode)
    sizes = [len(c) for c in components]
    # Number by size descending (1 = biggest)
    indexed = sorted(enumerate(sizes), key=lambda x: -x[1])
    ranked = []
    for rank, (comp_id, size) in enumerate(indexed, 1):
        ranked.append({"rank": rank, "component_id": comp_id, "size": size})

    return {
        "count": len(components),
        "largest_size": max(sizes) if sizes else 0,
        "largest_id": indexed[0][0] if indexed else None,
        "directed": g.is_directed(),
        "mode": mode,
        "components": ranked,
    }


def clustering_coefficient(g: ig.Graph, mode: str = "global") -> dict:
    """Compute clustering coefficient (transitivity).

    mode: 'global' for global transitivity, 'local' for per-node average.
    """
    if mode == "global":
        value = g.transitivity_undirected(mode="zero")
    else:
        value = g.transitivity_avglocal_undirected(mode="zero")

    return {
        "clustering_coefficient": value,
        "mode": mode,
    }


def reciprocity(g: ig.Graph) -> dict:
    """Compute reciprocity for directed networks."""
    if not g.is_directed():
        return {"reciprocity": None, "directed": False, "error": "Network is not directed"}
    return {
        "reciprocity": g.reciprocity(),
        "directed": True,
    }
