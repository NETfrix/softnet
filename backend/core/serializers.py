from __future__ import annotations

import msgpack
import numpy as np

from .project import ProjectState


def serialize_graph_for_sigma(
    project: ProjectState,
    layout_key: str = "default",
    node_size_attr: str | None = None,
    color_attr: str | None = None,
) -> bytes:
    """Serialize graph to MessagePack binary with typed arrays for Sigma.js."""
    g = project.graph
    n = g.vcount()

    node_ids = project.node_ids

    # Layout coordinates
    layout = project.layouts.get(layout_key)
    if layout is None:
        # Fallback: random layout
        import random

        random.seed(42)
        layout = [(random.uniform(-100, 100), random.uniform(-100, 100)) for _ in range(n)]

    x_coords = np.array([layout[i][0] for i in range(n)], dtype=np.float32)
    y_coords = np.array([layout[i][1] for i in range(n)], dtype=np.float32)

    # Node sizes
    sizes = np.ones(n, dtype=np.float32) * 3.0
    if node_size_attr and node_size_attr in project.centralities:
        values = project.centralities[node_size_attr]
        raw = np.array([values.get(nid, 0.0) for nid in node_ids], dtype=np.float32)
        mn, mx = raw.min(), raw.max()
        if mx > mn:
            sizes = 1.0 + 19.0 * (raw - mn) / (mx - mn)

    # Community colors
    colors = None
    if color_attr and color_attr in project.communities:
        colors = project.communities[color_attr]

    # Edge arrays
    edge_sources = np.array([e.source for e in g.es], dtype=np.int32)
    edge_targets = np.array([e.target for e in g.es], dtype=np.int32)

    # Node attributes (all vertex attributes except internal ones)
    node_attrs = {}
    for attr_name in g.vs.attributes():
        if attr_name.startswith("_"):
            continue
        vals = g.vs[attr_name]
        node_attrs[attr_name] = [str(v) if v is not None else "" for v in vals]

    payload = {
        "n": n,
        "m": g.ecount(),
        "directed": project.directed,
        "node_ids": node_ids,
        "x": x_coords.tobytes(),
        "y": y_coords.tobytes(),
        "sizes": sizes.tobytes(),
        "edge_sources": edge_sources.tobytes(),
        "edge_targets": edge_targets.tobytes(),
        "node_attrs": node_attrs,
    }
    if colors is not None:
        payload["colors"] = colors

    return msgpack.packb(payload, use_bin_type=True)
