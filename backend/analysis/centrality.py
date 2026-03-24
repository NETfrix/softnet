from __future__ import annotations

import igraph as ig
import numpy as np


def degree_centrality(
    g: ig.Graph, mode: str = "all", normalized: bool = True
) -> dict[str, float]:
    """Compute degree centrality. mode: 'all', 'in', 'out'."""
    degrees = g.degree(mode=mode)
    node_ids = _node_ids(g)
    n = g.vcount()
    if normalized and n > 1:
        divisor = (n - 1) if not g.is_directed() else (n - 1)
        values = {nid: d / divisor for nid, d in zip(node_ids, degrees)}
    else:
        values = {nid: float(d) for nid, d in zip(node_ids, degrees)}
    return values


def betweenness_centrality(
    g: ig.Graph, directed: bool = True, cutoff: int | None = None,
    normalized: bool = True,
) -> dict[str, float]:
    """Compute betweenness centrality using igraph (Brandes algorithm)."""
    bw = g.betweenness(directed=directed, cutoff=cutoff)
    node_ids = _node_ids(g)
    n = g.vcount()
    if normalized and n > 2:
        if directed:
            divisor = (n - 1) * (n - 2)
        else:
            divisor = (n - 1) * (n - 2) / 2
        values = {nid: b / divisor for nid, b in zip(node_ids, bw)}
    else:
        values = {nid: float(b) for nid, b in zip(node_ids, bw)}
    return values


def closeness_centrality(
    g: ig.Graph, mode: str = "all", normalized: bool = True
) -> dict[str, float]:
    """Compute closeness centrality."""
    cl = g.closeness(mode=mode, normalized=normalized)
    node_ids = _node_ids(g)
    # Replace NaN/None with 0
    values = {
        nid: (c if c is not None and not np.isnan(c) else 0.0)
        for nid, c in zip(node_ids, cl)
    }
    return values


def pagerank(
    g: ig.Graph, damping: float = 0.85, directed: bool = True
) -> dict[str, float]:
    """Compute PageRank centrality."""
    pr = g.pagerank(damping=damping, directed=directed)
    node_ids = _node_ids(g)
    return {nid: float(p) for nid, p in zip(node_ids, pr)}


def _node_ids(g: ig.Graph) -> list[str]:
    if "name" in g.vs.attributes():
        return [str(v["name"]) for v in g.vs]
    return [str(v.index) for v in g.vs]
