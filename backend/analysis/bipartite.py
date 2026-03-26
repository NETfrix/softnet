from __future__ import annotations

import igraph as ig


def detect_bipartite(g: ig.Graph) -> dict:
    """Check if the graph is bipartite and return type assignments."""
    is_bip = g.is_bipartite()
    if not is_bip:
        return {"is_bipartite": False, "types": None, "type_sizes": None}

    types = g.vs["type"] if "type" in g.vs.attributes() else None
    if types is None:
        # Try to compute bipartite types
        try:
            _, types = g.is_bipartite(return_types=True)
        except Exception:
            return {"is_bipartite": False, "types": None, "type_sizes": None}

    type0 = sum(1 for t in types if not t)
    type1 = sum(1 for t in types if t)

    return {
        "is_bipartite": True,
        "types": [bool(t) for t in types],
        "type_sizes": {"type_0": type0, "type_1": type1},
    }


def project_bipartite(
    g: ig.Graph,
    which: int = 0,
) -> ig.Graph:
    """
    Project a bipartite graph onto one of its node types.

    Args:
        g: A bipartite graph with 'type' vertex attribute.
        which: 0 or 1, indicating which node type to project onto.

    Returns:
        The projected unipartite graph.
    """
    if "type" not in g.vs.attributes():
        _, types = g.is_bipartite(return_types=True)
        g.vs["type"] = types

    projected = g.bipartite_projection(which=which)

    # Preserve node names
    if "name" not in projected.vs.attributes():
        projected.vs["name"] = [str(i) for i in range(projected.vcount())]

    return projected
