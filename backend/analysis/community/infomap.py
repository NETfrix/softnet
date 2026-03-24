from __future__ import annotations

import igraph as ig

try:
    from infomap import Infomap
    HAS_INFOMAP = True
except ImportError:
    HAS_INFOMAP = False


def infomap_detect(
    g: ig.Graph,
    directed: bool = True,
    num_trials: int = 10,
) -> dict:
    """Infomap community detection."""
    if not HAS_INFOMAP:
        raise ImportError(
            "Infomap is not installed. Install it with: pip install infomap "
            "(requires a C compiler)"
        )
    im = Infomap(silent=True, num_trials=num_trials, directed=directed)

    # Add edges
    node_ids = (
        [str(v["name"]) for v in g.vs]
        if "name" in g.vs.attributes()
        else [str(v.index) for v in g.vs]
    )
    n = g.vcount()

    for edge in g.es:
        weight = edge["weight"] if "weight" in g.es.attributes() else 1.0
        im.add_link(edge.source, edge.target, weight)

    im.run()

    # Extract membership
    membership = [0] * n
    for node_id in im.tree:
        if node_id.is_leaf:
            membership[node_id.node_id] = node_id.module_id

    n_communities = len(set(membership))
    modularity = g.modularity(membership)
    key = f"infomap_{num_trials}"

    return {
        "algorithm": "infomap",
        "key": key,
        "membership": membership,
        "n_communities": n_communities,
        "modularity": modularity,
    }
