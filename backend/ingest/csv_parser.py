from __future__ import annotations

import csv
import io
from typing import BinaryIO

import igraph as ig

# Common column names for source/target in edge lists
_SOURCE_NAMES = {"source", "src", "from", "node1", "node_1", "vertex1", "v1", "i", "ego"}
_TARGET_NAMES = {"target", "tgt", "to", "dest", "node2", "node_2", "vertex2", "v2", "j", "alter"}
_WEIGHT_NAMES = {"weight", "w", "value", "strength", "count"}


def _is_numeric(s: str) -> bool:
    if not s:
        return True  # empty treated as 0
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_csv_auto(
    file: BinaryIO,
    directed: bool = False,
    delimiter: str | None = None,
) -> ig.Graph:
    """
    Auto-detect CSV format and parse into an igraph Graph.

    Supports:
    - Edge list (2+ columns: source, target, optional weight/attrs)
    - Adjacency matrix (square numeric matrix with optional header)
    - Adjacency list (first column = node, remaining = neighbors)
    """
    text = file.read().decode("utf-8-sig").strip()
    if not text:
        raise ValueError("File is empty")

    # Auto-detect delimiter
    if delimiter is None:
        delimiter = _detect_delimiter(text)

    lines = text.split("\n")
    first_line = lines[0].strip()

    # Sniff: does the file have a header?
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)

    if len(rows) < 2:
        raise ValueError("File has fewer than 2 rows")

    header = [c.strip().lower() for c in rows[0]]
    n_cols = len(header)

    # Detect format — check matrix first (more specific), then edge list, then adj list
    if _is_adjacency_matrix(rows):
        return _parse_adjacency_matrix(rows, directed)
    elif _is_edge_list(header, rows):
        return _parse_edge_list(rows, header, delimiter, directed)
    else:
        return _parse_adjacency_list(rows, header, directed)


def _detect_delimiter(text: str) -> str:
    """Detect CSV delimiter from content."""
    first_lines = "\n".join(text.split("\n")[:5])
    for delim in [",", "\t", ";", "|", " "]:
        try:
            reader = csv.reader(io.StringIO(first_lines), delimiter=delim)
            counts = [len(row) for row in reader]
            if len(counts) >= 2 and counts[0] >= 2 and len(set(counts)) == 1:
                return delim
        except Exception:
            continue
    return ","


def _is_edge_list(header: list[str], rows: list[list[str]]) -> bool:
    """Check if the CSV is an edge list (has recognizable source/target columns or exactly 2-3 columns)."""
    # Check for known column names
    header_set = set(header)
    if header_set & _SOURCE_NAMES and header_set & _TARGET_NAMES:
        return True

    # 2 or 3 columns with non-numeric header suggests edge list
    if len(header) in (2, 3):
        # If header values look like data (both numeric), it might be headerless
        try:
            float(header[0])
            float(header[1])
            return True  # headerless edge list
        except ValueError:
            return True  # has header, 2-3 cols = edge list

    return False


def _is_adjacency_matrix(rows: list[list[str]]) -> bool:
    """Check if the CSV is a square adjacency matrix."""
    if len(rows) < 3:
        return False

    # Detect header row: first cell empty or non-numeric, rest are labels
    first_cell = rows[0][0].strip()
    has_header = (first_cell == "" or not _is_numeric(first_cell))

    data_start = 1 if has_header else 0
    data_rows = rows[data_start:]

    if len(data_rows) < 2:
        return False

    # Check if first column of data rows are labels (non-numeric)
    has_row_labels = not _is_numeric(data_rows[0][0].strip()) if data_rows[0][0].strip() else False
    col_offset = 1 if has_row_labels else 0

    n_rows = len(data_rows)
    n_data_cols = len(data_rows[0]) - col_offset

    # Must be square-ish
    if abs(n_data_cols - n_rows) > 1:
        return False

    # Check that data cells are numeric
    numeric_count = 0
    total = 0
    for row in data_rows[:min(5, n_rows)]:
        for val in row[col_offset:col_offset + min(5, n_data_cols)]:
            total += 1
            if _is_numeric(val.strip()):
                numeric_count += 1

    return total > 0 and numeric_count / total > 0.8


def _find_columns(header: list[str]) -> tuple[int, int, int | None]:
    """Find source, target, and optional weight column indices."""
    source_idx = None
    target_idx = None
    weight_idx = None

    for i, col in enumerate(header):
        col_clean = col.strip().lower()
        if col_clean in _SOURCE_NAMES and source_idx is None:
            source_idx = i
        elif col_clean in _TARGET_NAMES and target_idx is None:
            target_idx = i
        elif col_clean in _WEIGHT_NAMES and weight_idx is None:
            weight_idx = i

    # Default to first two columns if no match
    if source_idx is None:
        source_idx = 0
    if target_idx is None:
        target_idx = 1 if source_idx == 0 else 0

    return source_idx, target_idx, weight_idx


def _parse_edge_list(
    rows: list[list[str]], header: list[str], delimiter: str, directed: bool
) -> ig.Graph:
    """Parse edge list CSV."""
    source_idx, target_idx, weight_idx = _find_columns(header)

    # Determine if first row is header or data
    has_header = False
    header_set = set(header)
    if header_set & _SOURCE_NAMES or header_set & _TARGET_NAMES:
        has_header = True
    else:
        # If first row values look non-numeric and different from other rows, it's a header
        try:
            float(rows[0][source_idx].strip())
            float(rows[0][target_idx].strip())
        except ValueError:
            has_header = True

    data_start = 1 if has_header else 0
    col_names = header if has_header else None

    edges: list[tuple[str, str]] = []
    weights: list[float] = []
    extra_cols: list[int] = []
    edge_attrs: dict[str, list] = {}

    if col_names:
        extra_cols = [i for i in range(len(col_names)) if i not in (source_idx, target_idx, weight_idx)]
        edge_attrs = {col_names[i]: [] for i in extra_cols}

    for row in rows[data_start:]:
        if len(row) <= max(source_idx, target_idx):
            continue
        src = row[source_idx].strip()
        tgt = row[target_idx].strip()
        if not src or not tgt:
            continue
        edges.append((src, tgt))

        if weight_idx is not None and weight_idx < len(row):
            try:
                weights.append(float(row[weight_idx].strip()))
            except (ValueError, TypeError):
                weights.append(1.0)

        for i in extra_cols:
            edge_attrs[col_names[i]].append(row[i].strip() if i < len(row) else "")

    if not edges:
        raise ValueError("No edges found in file")

    # Build graph
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
    for attr_name, values in edge_attrs.items():
        if len(values) == g.ecount():
            g.es[attr_name] = values

    return g


def _parse_adjacency_matrix(rows: list[list[str]], directed: bool) -> ig.Graph:
    """Parse adjacency matrix CSV."""
    # Detect header row: first cell empty or non-numeric while data cells are numeric
    first_cell = rows[0][0].strip()
    has_header = first_cell == "" or (not _is_numeric(first_cell) and len(rows[0]) > 2)

    # If header not obvious, check if first row has non-numeric values in positions 1+
    if not has_header and len(rows) > 2:
        data_vals = [v.strip() for v in rows[0][1:] if v.strip()]
        if data_vals and not all(_is_numeric(v) for v in data_vals):
            has_header = True

    data_start = 1 if has_header else 0
    data_rows = rows[data_start:]

    # Check if first column of data rows are labels (non-numeric)
    has_row_labels = False
    if data_rows:
        first_data_cell = data_rows[0][0].strip()
        has_row_labels = bool(first_data_cell) and not _is_numeric(first_data_cell)

    col_offset = 1 if has_row_labels else 0
    n = len(data_rows)

    # Get node names
    if has_header and has_row_labels:
        node_names = [rows[0][i].strip() for i in range(col_offset, len(rows[0]))]
    elif has_row_labels:
        node_names = [row[0].strip() for row in data_rows]
    elif has_header:
        node_names = [rows[0][i].strip() for i in range(len(rows[0]))]
    else:
        node_names = [str(i) for i in range(n)]

    # Build edges from matrix
    edges: list[tuple[int, int]] = []
    weights: list[float] = []

    for i, row in enumerate(data_rows):
        for j in range(col_offset, len(row)):
            val_str = row[j].strip()
            if not val_str:
                continue
            try:
                val = float(val_str)
            except ValueError:
                continue
            if val != 0:
                col_idx = j - col_offset
                if col_idx < n:
                    if directed or col_idx >= i:  # avoid duplicate edges for undirected
                        edges.append((i, col_idx))
                        weights.append(val)

    g = ig.Graph(n=n, edges=edges, directed=directed)
    g.vs["name"] = node_names[:n]
    if weights and any(w != 1.0 for w in weights):
        g.es["weight"] = weights

    return g


def _parse_adjacency_list(rows: list[list[str]], header: list[str], directed: bool) -> ig.Graph:
    """Parse adjacency list CSV (first column = node, rest = neighbors)."""
    # Check if first row is header
    has_header = False
    try:
        # If header looks like labels not data
        if any(h.strip().lower() in ("node", "vertex", "id", "name") for h in header):
            has_header = True
    except Exception:
        pass

    data_start = 1 if has_header else 0

    edges: list[tuple[str, str]] = []
    for row in rows[data_start:]:
        if len(row) < 2:
            continue
        node = row[0].strip()
        if not node:
            continue
        for neighbor in row[1:]:
            neighbor = neighbor.strip()
            if neighbor:
                edges.append((node, neighbor))

    if not edges:
        raise ValueError("No edges found. Could not detect format (edge list, adjacency matrix, or adjacency list).")

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

    return g


def parse_node_csv(
    graph: ig.Graph,
    file: BinaryIO,
    delimiter: str = ",",
) -> ig.Graph:
    """Add node attributes from a CSV file to an existing graph."""
    text = file.read().decode("utf-8-sig")
    if not text.strip():
        return graph

    if delimiter is None:
        delimiter = _detect_delimiter(text)

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    # Auto-detect ID column
    id_col = None
    for col in reader.fieldnames or []:
        if col.strip().lower() in ("id", "name", "node", "vertex", "label"):
            id_col = col
            break
    if id_col is None and reader.fieldnames:
        id_col = reader.fieldnames[0]

    attr_cols = [c for c in (reader.fieldnames or []) if c != id_col]
    node_names = graph.vs["name"] if "name" in graph.vs.attributes() else [str(i) for i in range(graph.vcount())]
    name_to_idx = {name: i for i, name in enumerate(node_names)}

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
