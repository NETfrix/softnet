from __future__ import annotations

import igraph as ig


def infomap_detect(
    g: ig.Graph,
    directed: bool = True,
    num_trials: int = 10,
) -> dict:
    """
    Infomap community detection using igraph's built-in implementation.

    Uses igraph's C-level community_infomap which is compiled into the
    igraph binary — no external compiler or package needed.
    """
    membership = g.community_infomap(
        edge_weights="weight" if "weight" in g.es.attributes() else None,
        vertex_weights=None,
        trials=num_trials,
    ).membership

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
