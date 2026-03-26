from __future__ import annotations

from collections import Counter

import igraph as ig


def ei_index(g: ig.Graph, membership: list[int]) -> dict:
    """
    Compute the E-I (External-Internal) index for a community partition.

    E-I = (external - internal) / (external + internal)
    Range: -1 (perfectly homophilic) to +1 (perfectly heterophilic)
    """
    internal = 0
    external = 0

    for edge in g.es:
        if membership[edge.source] == membership[edge.target]:
            internal += 1
        else:
            external += 1

    total = internal + external
    ei = (external - internal) / total if total > 0 else 0.0

    community_sizes = dict(Counter(membership))
    community_sizes = {str(k): v for k, v in community_sizes.items()}

    return {
        "ei_index": ei,
        "internal_edges": internal,
        "external_edges": external,
        "community_sizes": community_sizes,
    }


def attribute_homophily(
    g: ig.Graph,
    membership: list[int],
    attribute: str,
) -> dict:
    """
    Analyze how a node attribute distributes within each community.

    Returns per-community distribution of the attribute values.
    """
    if attribute not in g.vs.attributes():
        raise ValueError(f"Attribute '{attribute}' not found in graph nodes")

    attr_values = g.vs[attribute]
    n_communities = len(set(membership))

    distributions: dict[str, dict[str, int]] = {}
    for comm_id in sorted(set(membership)):
        comm_nodes = [i for i, m in enumerate(membership) if m == comm_id]
        comm_attrs = [str(attr_values[i]) for i in comm_nodes]
        distributions[str(comm_id)] = dict(Counter(comm_attrs))

    return {
        "attribute": attribute,
        "distributions": distributions,
    }


def newman_homophily(
    g: ig.Graph,
    membership: list[int],
) -> dict:
    """
    Compute Newman's assortativity coefficient for community membership.

    Measures the tendency of nodes to connect to others in the same community.
    Range: -1 (perfectly disassortative) to +1 (perfectly assortative/homophilic).
    """
    r = g.assortativity(membership, directed=g.is_directed())

    # Per-community scores: fraction of internal edges vs expected
    n_communities = len(set(membership))
    community_scores = {}
    total_edges = g.ecount()

    if total_edges > 0:
        for comm_id in sorted(set(membership)):
            comm_nodes = set(i for i, m in enumerate(membership) if m == comm_id)
            internal = sum(
                1
                for e in g.es
                if e.source in comm_nodes and e.target in comm_nodes
            )
            # Expected under random mixing
            comm_degree_sum = sum(g.degree(list(comm_nodes)))
            expected = (comm_degree_sum ** 2) / (4 * total_edges) if not g.is_directed() else (comm_degree_sum ** 2) / (2 * total_edges)
            community_scores[str(comm_id)] = {
                "internal_edges": internal,
                "expected_random": round(expected, 2),
                "newman_score": round(internal / expected - 1, 4) if expected > 0 else 0.0,
            }

    return {
        "assortativity": r,
        "community_scores": community_scores,
    }
