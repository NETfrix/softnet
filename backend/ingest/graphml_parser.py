from __future__ import annotations

import tempfile
import os
from typing import BinaryIO

import igraph as ig


def parse_graphml(file: BinaryIO) -> ig.Graph:
    """Parse a GraphML file into an igraph Graph."""
    with tempfile.NamedTemporaryFile(suffix=".graphml", delete=False) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    try:
        g = ig.Graph.Read_GraphML(tmp_path)
    finally:
        os.unlink(tmp_path)

    # Ensure nodes have string names
    if "name" not in g.vs.attributes() and "id" in g.vs.attributes():
        g.vs["name"] = g.vs["id"]
    elif "name" not in g.vs.attributes():
        g.vs["name"] = [str(i) for i in range(g.vcount())]

    return g
