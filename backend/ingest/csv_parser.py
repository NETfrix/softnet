from __future__ import annotations

import csv
import io
from typing import BinaryIO

import igraph as ig


def parse_edge_csv(
    file: BinaryIO,
    delimiter: str = ",",
    source_col: str = "source",
    target_col: str = "target",
    weight_col: str | None = None,
    directed: bool = False,
) -> ig.Graph:
    """Parse a CSV edge list into an igraph Graph."""
    text = file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    if source_col not in reader.fieldnames or target_col not in reader.fieldnames:
        raise ValueError(
            f"CSV must contain '{source_col}' and '{target_col}' columns. "
            f"Found: {reader.fieldnames}"
        )

    edges: list[tuple[str, str]] = []
    weights: list[float] = []
    extra_cols = [
        c for c in reader.fieldnames if c not in (source_col, target_col, weight_col)
    ]
    edge_attrs: dict[str, list] = {c: [] for c in extra_cols}

    for row in reader:
        src = row[source_col].strip()
        tgt = row[target_col].strip()
        if not src or not tgt:
            continue
        edges.append((src, tgt))
        if weight_col and weight_col in row:
            try:
                weights.append(float(row[weight_col]))
            except (ValueError, TypeError):
                weights.append(1.0)
        for c in extra_cols:
            edge_attrs[c].append(row.get(c, ""))

    # Collect unique node names preserving order
    seen: set[str] = set()
    node_names: list[str] = []
    for src, tgt in edges:
        for n in (src, tgt):
            if n not in seen:
                seen.add(n)
                node_names.append(n)

    name_to_idx = {name: i for i, name in enumerate(node_names)}
    indexed_edges = [(name_to_idx[s], name_to_idx[t]) for s, t in edges]

    g = ig.Graph(n=len(node_names), edges=indexed_edges, directed=directed)
    g.vs["name"] = node_names

    if weights:
        g.es["weight"] = weights
    for c in extra_cols:
        g.es[c] = edge_attrs[c]

    return g


def parse_node_csv(
    graph: ig.Graph,
    file: BinaryIO,
    id_col: str = "id",
    delimiter: str = ",",
) -> ig.Graph:
    """Add node attributes from a CSV file to an existing graph."""
    text = file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    if id_col not in reader.fieldnames:
        raise ValueError(f"Node CSV must contain '{id_col}' column. Found: {reader.fieldnames}")

    attr_cols = [c for c in reader.fieldnames if c != id_col]
    node_names = graph.vs["name"] if "name" in graph.vs.attributes() else [str(i) for i in range(graph.vcount())]
    name_to_idx = {name: i for i, name in enumerate(node_names)}

    # Initialize attribute lists
    attrs: dict[str, list] = {c: [None] * graph.vcount() for c in attr_cols}

    for row in reader:
        node_id = row[id_col].strip()
        idx = name_to_idx.get(node_id)
        if idx is None:
            continue
        for c in attr_cols:
            attrs[c][idx] = row.get(c, "")

    for c, values in attrs.items():
        graph.vs[c] = values

    return graph
