from __future__ import annotations

import igraph as ig


def louvain(
    g: ig.Graph,
    resolution: float = 1.0,
    quality: str = "modularity",
) -> dict:
    """
    Louvain community detection.

    quality: "modularity" uses igraph's community_multilevel.
             "CPM" uses leidenalg with Louvain optimizer and CPMVertexPartition.
    """
    if quality == "CPM":
        return _louvain_cpm(g, resolution)

    # Standard modularity-based Louvain
    if resolution != 1.0:
        # igraph's community_multilevel doesn't support resolution directly,
        # use leidenalg with RBConfigurationVertexPartition as Louvain-like
        import leidenalg

        partition = leidenalg.find_partition(
            g,
            leidenalg.RBConfigurationVertexPartition,
            resolution_parameter=resolution,
            n_iterations=-1,  # run until no improvement (Louvain-like)
        )
        membership = list(partition.membership)
        modularity = g.modularity(membership)
    else:
        result = g.community_multilevel()
        membership = list(result.membership)
        modularity = result.modularity

    n_communities = len(set(membership))
    key = f"louvain_{resolution}_{quality}"

    return {
        "algorithm": "louvain",
        "key": key,
        "membership": membership,
        "n_communities": n_communities,
        "modularity": modularity,
    }


def _louvain_cpm(g: ig.Graph, resolution: float) -> dict:
    import leidenalg

    partition = leidenalg.find_partition(
        g,
        leidenalg.CPMVertexPartition,
        resolution_parameter=resolution,
        n_iterations=-1,
    )
    membership = list(partition.membership)
    modularity = g.modularity(membership)
    n_communities = len(set(membership))
    key = f"louvain_{resolution}_CPM"

    return {
        "algorithm": "louvain",
        "key": key,
        "membership": membership,
        "n_communities": n_communities,
        "modularity": modularity,
    }
