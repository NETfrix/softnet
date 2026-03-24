from __future__ import annotations

import httpx
import igraph as ig


async def fetch_graph_from_api(
    endpoint: str,
    headers: dict[str, str],
    node_path: str = "nodes",
    edge_path: str = "edges",
    source_field: str = "source",
    target_field: str = "target",
    directed: bool = False,
) -> ig.Graph:
    """Fetch graph data from a REST API endpoint."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(endpoint, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # Navigate to nodes and edges in response
    nodes_data = _navigate_path(data, node_path)
    edges_data = _navigate_path(data, edge_path)

    if not isinstance(nodes_data, list) or not isinstance(edges_data, list):
        raise ValueError("node_path and edge_path must point to arrays in the response")

    # Build node list
    node_ids: list[str] = []
    node_attrs: dict[str, list] = {}
    for node in nodes_data:
        if isinstance(node, dict):
            nid = str(node.get("id", node.get("name", len(node_ids))))
            node_ids.append(nid)
            for k, v in node.items():
                if k not in ("id", "name"):
                    node_attrs.setdefault(k, []).append(str(v) if v is not None else "")
        else:
            node_ids.append(str(node))

    # Pad any short attribute lists
    for k in node_attrs:
        while len(node_attrs[k]) < len(node_ids):
            node_attrs[k].append("")

    name_to_idx = {name: i for i, name in enumerate(node_ids)}

    # Build edges
    edges: list[tuple[int, int]] = []
    for edge in edges_data:
        src = str(edge.get(source_field, ""))
        tgt = str(edge.get(target_field, ""))
        si = name_to_idx.get(src)
        ti = name_to_idx.get(tgt)
        if si is not None and ti is not None:
            edges.append((si, ti))

    g = ig.Graph(n=len(node_ids), edges=edges, directed=directed)
    g.vs["name"] = node_ids
    for k, v in node_attrs.items():
        g.vs[k] = v

    return g


def _navigate_path(data: dict, path: str):
    """Navigate a dot-separated path in a nested dict."""
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            current = current[int(part)]
        else:
            return None
    return current
