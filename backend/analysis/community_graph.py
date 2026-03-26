from __future__ import annotations

from collections import Counter

import igraph as ig


def create_community_graph(
    g: ig.Graph,
    membership: list[int],
) -> ig.Graph:
    """
    Create a community-level graph by contracting nodes by community membership.

    Each community becomes a node. Edges between communities are aggregated
    with weights representing the number of inter-community edges.
    Self-loops represent intra-community edges.
    """
    communities = sorted(set(membership))
    n_communities = len(communities)
    comm_to_idx = {c: i for i, c in enumerate(communities)}

    # Count edges between communities
    edge_counts: Counter[tuple[int, int]] = Counter()
    for edge in g.es:
        src_comm = comm_to_idx[membership[edge.source]]
        tgt_comm = comm_to_idx[membership[edge.target]]
        if src_comm > tgt_comm and not g.is_directed():
            src_comm, tgt_comm = tgt_comm, src_comm
        edge_counts[(src_comm, tgt_comm)] += 1

    # Build community graph
    edges = list(edge_counts.keys())
    weights = [edge_counts[e] for e in edges]

    cg = ig.Graph(
        n=n_communities,
        edges=edges,
        directed=g.is_directed(),
    )

    # Community sizes as node attribute
    comm_sizes = Counter(membership)
    cg.vs["name"] = [f"Community {c}" for c in communities]
    cg.vs["size"] = [comm_sizes[c] for c in communities]
    cg.vs["community_id"] = list(communities)
    cg.es["weight"] = weights

    return cg
