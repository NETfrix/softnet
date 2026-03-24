from __future__ import annotations

import os
import tempfile
from typing import BinaryIO

import igraph as ig


def parse_gexf(file: BinaryIO) -> ig.Graph:
    """Parse a GEXF file (Gephi format) into an igraph Graph."""
    with tempfile.NamedTemporaryFile(suffix=".gexf", delete=False) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    try:
        g = _parse_gexf_lxml(tmp_path)
    finally:
        os.unlink(tmp_path)

    return g


def _parse_gexf_lxml(path: str) -> ig.Graph:
    """Parse GEXF using lxml."""
    from lxml import etree

    tree = etree.parse(path)
    root = tree.getroot()
    ns = {"g": root.nsmap.get(None, "http://www.gexf.net/1.2draft")}

    graph_el = root.find(".//g:graph", ns)
    directed = graph_el.get("defaultedgetype", "undirected") == "directed"

    # Parse attribute declarations
    attr_defs: dict[str, dict[str, str]] = {}
    for attrs_el in root.findall(".//g:attributes", ns):
        for attr_el in attrs_el.findall("g:attribute", ns):
            attr_defs[attr_el.get("id")] = {
                "title": attr_el.get("title"),
                "class": attrs_el.get("class", "node"),
            }

    # Parse nodes
    nodes: list[str] = []
    node_attrs: dict[str, list] = {}
    node_labels: list[str] = []

    for node_el in graph_el.findall(".//g:node", ns):
        node_id = node_el.get("id")
        nodes.append(node_id)
        node_labels.append(node_el.get("label", node_id))

        attvalues = node_el.find("g:attvalues", ns)
        if attvalues is not None:
            for av in attvalues.findall("g:attvalue", ns):
                attr_id = av.get("for")
                attr_info = attr_defs.get(attr_id, {})
                attr_name = attr_info.get("title", attr_id)
                if attr_name not in node_attrs:
                    node_attrs[attr_name] = [None] * (len(nodes) - 1)
                node_attrs[attr_name].append(av.get("value"))

        # Pad missing attrs
        for key in node_attrs:
            while len(node_attrs[key]) < len(nodes):
                node_attrs[key].append(None)

    name_to_idx = {name: i for i, name in enumerate(nodes)}

    # Parse edges
    edges: list[tuple[int, int]] = []
    edge_weights: list[float] = []
    for edge_el in graph_el.findall(".//g:edge", ns):
        src = edge_el.get("source")
        tgt = edge_el.get("target")
        if src in name_to_idx and tgt in name_to_idx:
            edges.append((name_to_idx[src], name_to_idx[tgt]))
            w = edge_el.get("weight")
            edge_weights.append(float(w) if w else 1.0)

    g = ig.Graph(n=len(nodes), edges=edges, directed=directed)
    g.vs["name"] = nodes
    g.vs["label"] = node_labels
    for attr_name, values in node_attrs.items():
        g.vs[attr_name] = values
    if edge_weights:
        g.es["weight"] = edge_weights

    return g
