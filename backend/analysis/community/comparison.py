from __future__ import annotations

from collections import Counter


def compute_nmi(membership_a: list[int], membership_b: list[int]) -> float:
    """Compute Normalized Mutual Information between two partitions."""
    import igraph as ig

    return ig.compare_communities(membership_a, membership_b, method="nmi")


def compute_ari(membership_a: list[int], membership_b: list[int]) -> float:
    """Compute Adjusted Rand Index between two partitions."""
    import igraph as ig

    return ig.compare_communities(membership_a, membership_b, method="adjusted_rand")


def build_sankey_data(
    memberships: dict[str, list[int]],
    node_ids: list[str],
    top_n: int = 20,
) -> dict:
    """
    Build Sankey diagram data comparing two community partitions.

    Returns dict with labels, sources, targets, values for Plotly Sankey.
    """
    keys = list(memberships.keys())
    if len(keys) != 2:
        raise ValueError("Sankey comparison requires exactly 2 community assignments")

    mem_a = memberships[keys[0]]
    mem_b = memberships[keys[1]]

    # Count community sizes for each partition
    counter_a = Counter(mem_a)
    counter_b = Counter(mem_b)

    # Get top communities by size
    top_a = [c for c, _ in counter_a.most_common(top_n)]
    top_b = [c for c, _ in counter_b.most_common(top_n)]

    # Create labels: left side = partition A, right side = partition B
    labels_a = [f"{keys[0]}:{c}" for c in top_a]
    labels_b = [f"{keys[1]}:{c}" for c in top_b]
    all_labels = labels_a + labels_b

    # Map community IDs to Sankey node indices
    idx_a = {c: i for i, c in enumerate(top_a)}
    idx_b = {c: i + len(top_a) for i, c in enumerate(top_b)}

    # Count flows between communities
    flow_counts: Counter[tuple[int, int]] = Counter()
    for ca, cb in zip(mem_a, mem_b):
        if ca in idx_a and cb in idx_b:
            flow_counts[(idx_a[ca], idx_b[cb])] += 1

    sources = []
    targets = []
    values = []
    for (s, t), v in flow_counts.items():
        sources.append(s)
        targets.append(t)
        values.append(v)

    return {
        "labels": all_labels,
        "sources": sources,
        "targets": targets,
        "values": values,
        "nmi": compute_nmi(mem_a, mem_b),
        "ari": compute_ari(mem_a, mem_b),
    }
