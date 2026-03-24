from __future__ import annotations

import igraph as ig
import leidenalg


def leiden(
    g: ig.Graph,
    resolution: float = 1.0,
    quality: str = "modularity",
    n_iterations: int = 2,
    seed: int | None = None,
) -> dict:
    """
    Leiden community detection.

    quality: "modularity" -> ModularityVertexPartition (resolution via RBConfiguration)
             "CPM" -> CPMVertexPartition
    """
    if quality == "CPM":
        partition_type = leidenalg.CPMVertexPartition
    else:
        # Use RBConfigurationVertexPartition for resolution support
        if resolution != 1.0:
            partition_type = leidenalg.RBConfigurationVertexPartition
        else:
            partition_type = leidenalg.ModularityVertexPartition

    kwargs = {"n_iterations": n_iterations}
    if seed is not None:
        kwargs["seed"] = seed
    if partition_type != leidenalg.ModularityVertexPartition:
        kwargs["resolution_parameter"] = resolution

    partition = leidenalg.find_partition(g, partition_type, **kwargs)
    membership = list(partition.membership)
    modularity = g.modularity(membership)
    n_communities = len(set(membership))
    key = f"leiden_{resolution}_{quality}"

    return {
        "algorithm": "leiden",
        "key": key,
        "membership": membership,
        "n_communities": n_communities,
        "modularity": modularity,
    }
