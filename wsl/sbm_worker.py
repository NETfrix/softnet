#!/usr/bin/env python3
"""
SBM worker script — runs inside WSL with graph-tool installed.

Usage:
    python3 sbm_worker.py --input edges.csv --output result.json \
                          --meta meta.json --model nested --deg-corr
"""
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Run Peixoto's SBM via graph-tool")
    parser.add_argument("--input", required=True, help="CSV edge list path")
    parser.add_argument("--output", required=True, help="JSON output path")
    parser.add_argument("--meta", required=True, help="JSON metadata path")
    parser.add_argument("--model", default="nested", choices=["flat", "nested"])
    parser.add_argument("--deg-corr", action="store_true")
    args = parser.parse_args()

    try:
        import graph_tool.all as gt
    except ImportError:
        print("Error: graph-tool not installed. Run setup_graphtool.sh first.", file=sys.stderr)
        sys.exit(1)

    # Read metadata
    with open(args.meta) as f:
        meta = json.load(f)

    directed = meta.get("directed", False)
    n_vertices = meta.get("n_vertices", 0)

    # Build graph
    g = gt.Graph(directed=directed)
    if n_vertices > 0:
        g.add_vertex(n_vertices)

    edges = []
    with open(args.input) as f:
        header = f.readline()  # skip header
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            s, t = int(parts[0]), int(parts[1])
            edges.append((s, t))

    g.add_edge_list(edges)

    # Run SBM
    if args.model == "nested":
        state = gt.minimize_nested_blockmodel_dl(
            g, deg_corr=args.deg_corr, state_args=dict(recs=[], rec_types=[])
        )
        # Extract levels
        levels = []
        for level in state.levels:
            levels.append([int(x) for x in level.get_blocks().a])
        membership = levels[0] if levels else []
        dl = state.entropy()
    else:
        state = gt.minimize_blockmodel_dl(g, deg_corr=args.deg_corr)
        membership = [int(x) for x in state.get_blocks().a]
        levels = [membership]
        dl = state.entropy()

    result = {
        "membership": membership,
        "levels": levels,
        "description_length": float(dl),
    }

    with open(args.output, "w") as f:
        json.dump(result, f)

    print(f"SBM completed: {len(set(membership))} communities, DL={dl:.2f}", file=sys.stderr)


if __name__ == "__main__":
    main()
