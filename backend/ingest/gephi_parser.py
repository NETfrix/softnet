from __future__ import annotations

import io
import os
import tempfile
import zipfile
from typing import BinaryIO

import igraph as ig

from .gexf_parser import parse_gexf


def parse_gephi(file: BinaryIO) -> ig.Graph:
    """
    Parse a Gephi project file (.gephi).

    Gephi project files are ZIP archives. Modern versions (0.9+) store
    graph data as Java-serialized binary (graphstore_bytes). Older versions
    used XML. This parser handles:

    1. Embedded GEXF/GraphML files inside the ZIP
    2. Legacy XML workspace graph data
    3. Modern binary format -> helpful error with export instructions
    """
    data = file.read()

    # If it's not a ZIP, try parsing as GEXF directly (some users rename .gexf to .gephi)
    if not zipfile.is_zipfile(io.BytesIO(data)):
        return parse_gexf(io.BytesIO(data))

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()

        # 1. Look for embedded GEXF or GraphML files
        for name in names:
            lower = name.lower()
            if lower.endswith(".gexf"):
                return parse_gexf(io.BytesIO(zf.read(name)))
            if lower.endswith(".graphml") or lower.endswith(".xml"):
                # Try parsing as GraphML
                try:
                    with tempfile.NamedTemporaryFile(suffix=".graphml", delete=False) as tmp:
                        tmp.write(zf.read(name))
                        tmp_path = tmp.name
                    g = ig.Graph.Read_GraphML(tmp_path)
                    os.unlink(tmp_path)
                    if g.vcount() > 0:
                        if "name" not in g.vs.attributes():
                            g.vs["name"] = [str(i) for i in range(g.vcount())]
                        return g
                except Exception:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

        # 2. Check for legacy XML workspace entries
        xml_entries = [n for n in names if n.endswith("_xml") and "graphstore" in n.lower()]
        if xml_entries:
            # Try to parse legacy XML graph data
            for entry in xml_entries:
                try:
                    return _parse_legacy_xml_graph(zf.read(entry))
                except Exception:
                    continue

        # 3. Check for binary graphstore (modern Gephi 0.9+)
        binary_entries = [n for n in names if "graphstore" in n.lower() and "_bytes" in n.lower()]
        if binary_entries:
            raise ValueError(
                "This .gephi file uses Gephi's binary format (0.9+) which cannot be "
                "read directly. Please open it in Gephi and export as GEXF:\n"
                "  File -> Export -> Graph file -> GEXF\n"
                "Then upload the .gexf file here."
            )

        # 4. List what we found for debugging
        raise ValueError(
            f"Could not find graph data in this .gephi file. "
            f"ZIP contains: {', '.join(names[:10])}{'...' if len(names) > 10 else ''}. "
            f"Please export from Gephi as GEXF (File -> Export -> Graph file -> GEXF)."
        )


def _parse_legacy_xml_graph(xml_data: bytes) -> ig.Graph:
    """Attempt to parse legacy Gephi XML workspace graph data."""
    from lxml import etree

    root = etree.fromstring(xml_data)

    # Look for node and edge elements in various possible structures
    nodes = root.findall(".//{*}node") or root.findall(".//node")
    edges = root.findall(".//{*}edge") or root.findall(".//edge")

    if not nodes:
        raise ValueError("No nodes found in XML data")

    node_ids = []
    node_labels = []
    for node in nodes:
        nid = node.get("id") or node.get("label") or str(len(node_ids))
        node_ids.append(nid)
        node_labels.append(node.get("label", nid))

    name_to_idx = {nid: i for i, nid in enumerate(node_ids)}

    edge_list = []
    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if src in name_to_idx and tgt in name_to_idx:
            edge_list.append((name_to_idx[src], name_to_idx[tgt]))

    g = ig.Graph(n=len(node_ids), edges=edge_list, directed=False)
    g.vs["name"] = node_ids
    g.vs["label"] = node_labels

    return g
