"""
Community-aware layout: Leiden/Louvain detection + per-community positioning.

1. Detect communities (or reuse existing partition)
2. Build meta-graph (communities as nodes, inter-community edges)
3. Layout meta-graph to position community centers
4. Layout nodes within each community using force-directed
5. Scale and combine into final positions
"""
from __future__ import annotations

from collections import defaultdict

import igraph as ig
import numpy as np


def compute_community_layout(
    g: ig.Graph,
    membership: list[int],
    internal_iterations: int = 50,
    spacing: float = 2.0,
) -> list[tuple[float, float]]:
    """Compute a layout that groups nodes by community.

    Parameters
    ----------
    g : igraph.Graph
    membership : list of community IDs per node
    internal_iterations : FR iterations for intra-community layout
    spacing : gap multiplier between communities (higher = more separation)
    """
    n = g.vcount()
    if n == 0:
        return []
    if n == 1:
        return [(0.0, 0.0)]

    # Group nodes by community
    comm_nodes: dict[int, list[int]] = defaultdict(list)
    for node_idx, comm_id in enumerate(membership):
        comm_nodes[comm_id].append(node_idx)

    n_communities = len(comm_nodes)
    if n_communities == 1:
        # Single community — just do a normal force-directed layout
        layout = _layout_subgraph(g, list(range(n)), internal_iterations)
        return layout

    # Build meta-graph: one node per community, edges = inter-community connections
    meta = ig.Graph(n=n_communities, directed=False)
    comm_ids_sorted = sorted(comm_nodes.keys())
    comm_to_meta = {c: i for i, c in enumerate(comm_ids_sorted)}
    meta.vs["size"] = [len(comm_nodes[c]) for c in comm_ids_sorted]

    meta_edges: dict[tuple[int, int], int] = defaultdict(int)
    for e in g.es:
        c_src = membership[e.source]
        c_tgt = membership[e.target]
        if c_src != c_tgt:
            pair = (min(comm_to_meta[c_src], comm_to_meta[c_tgt]),
                    max(comm_to_meta[c_src], comm_to_meta[c_tgt]))
            meta_edges[pair] += 1

    if meta_edges:
        edges, weights = zip(*[((s, t), w) for (s, t), w in meta_edges.items()])
        meta.add_edges(edges)
        meta.es["weight"] = list(weights)

    # Layout meta-graph — position community centers
    if n_communities <= 50:
        meta_layout = meta.layout_fruchterman_reingold(
            niter=500, weights="weight" if meta_edges else None
        )
    else:
        meta_layout = meta.layout_drl(weights="weight" if meta_edges else None)

    meta_coords = np.array(meta_layout.coords, dtype=np.float64)

    # Normalize meta-coords to [0, 1] range
    meta_min = meta_coords.min(axis=0)
    meta_max = meta_coords.max(axis=0)
    meta_range = meta_max - meta_min
    meta_range[meta_range == 0] = 1.0
    meta_coords = (meta_coords - meta_min) / meta_range

    # Compute radii for each community proportional to sqrt(size)
    sizes = np.array([len(comm_nodes[c]) for c in comm_ids_sorted], dtype=np.float64)
    radii = np.sqrt(sizes)
    radii /= radii.max()  # normalize to [0, 1]

    # Scale meta-coordinates so communities don't overlap
    # Spread them out by spacing factor
    meta_coords *= spacing * np.sqrt(n_communities)

    # Layout each community internally
    positions = [None] * n
    for comm_id in comm_ids_sorted:
        meta_idx = comm_to_meta[comm_id]
        nodes = comm_nodes[comm_id]
        center_x, center_y = meta_coords[meta_idx]
        radius = radii[meta_idx]

        if len(nodes) == 1:
            positions[nodes[0]] = (center_x, center_y)
            continue

        # Extract subgraph and compute internal layout
        sub_positions = _layout_subgraph(g, nodes, internal_iterations)

        # Scale internal layout to fit within community radius
        sub_arr = np.array(sub_positions, dtype=np.float64)
        sub_min = sub_arr.min(axis=0)
        sub_max = sub_arr.max(axis=0)
        sub_range = sub_max - sub_min
        sub_range[sub_range == 0] = 1.0

        # Center and scale to radius
        sub_centered = sub_arr - (sub_min + sub_max) / 2
        scale = radius / max(sub_range) * spacing
        sub_scaled = sub_centered * scale

        # Offset by community center
        for i, node_idx in enumerate(nodes):
            positions[node_idx] = (
                center_x + sub_scaled[i, 0],
                center_y + sub_scaled[i, 1],
            )

    return positions


def _layout_subgraph(
    g: ig.Graph,
    node_indices: list[int],
    iterations: int,
) -> list[tuple[float, float]]:
    """Layout a subgraph induced by node_indices."""
    sub = g.subgraph(node_indices)
    n = sub.vcount()

    if n > 5000:
        layout = sub.layout_drl(options="default")
    elif n > 500:
        layout = sub.layout_fruchterman_reingold(niter=iterations, grid="auto")
    else:
        layout = sub.layout_fruchterman_reingold(niter=iterations)

    return [(float(x), float(y)) for x, y in layout.coords]
