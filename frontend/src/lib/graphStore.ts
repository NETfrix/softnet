import { writable, derived } from "svelte/store";
import Graph from "graphology";
import { decode } from "@msgpack/msgpack";
import type { GraphPayload } from "./types";

// Color palette for communities
const PALETTE = [
  "#6366f1", "#ec4899", "#f59e0b", "#22c55e", "#06b6d4",
  "#8b5cf6", "#f43f5e", "#eab308", "#10b981", "#0ea5e9",
  "#a855f7", "#e11d48", "#d97706", "#059669", "#0284c7",
  "#7c3aed", "#be123c", "#b45309", "#047857", "#0369a1",
  "#6d28d9", "#9f1239", "#92400e", "#065f46", "#075985",
];

export const graphStore = writable<Graph | null>(null);
export const labelsVisible = writable(true);
export const currentLayout = writable("default");
export const currentSizeAttr = writable<string | null>(null);
export const currentColorAttr = writable<string | null>(null);
export const edgeScale = writable(1.0);

// View mode: "graph" | "community-graph" | "comparison"
export const viewMode = writable<string>("graph");
export const communityGraphData = writable<{
  nodes: { id: number; name: string; size: number }[];
  edges: { source: number; target: number; weight: number }[];
} | null>(null);
export const comparisonData = writable<Record<string, unknown> | null>(null);

export function deserializeGraph(buffer: ArrayBuffer): Graph {
  const data = decode(new Uint8Array(buffer)) as GraphPayload;
  const graph = new Graph({
    type: data.directed ? "directed" : "undirected",
    allowSelfLoops: true,
    multi: false,
  });

  const xs = new Float32Array(
    data.x instanceof Uint8Array ? data.x.buffer.slice(data.x.byteOffset, data.x.byteOffset + data.x.byteLength) : data.x
  );
  const ys = new Float32Array(
    data.y instanceof Uint8Array ? data.y.buffer.slice(data.y.byteOffset, data.y.byteOffset + data.y.byteLength) : data.y
  );
  const szs = new Float32Array(
    data.sizes instanceof Uint8Array ? data.sizes.buffer.slice(data.sizes.byteOffset, data.sizes.byteOffset + data.sizes.byteLength) : data.sizes
  );
  const srcs = new Int32Array(
    data.edge_sources instanceof Uint8Array ? data.edge_sources.buffer.slice(data.edge_sources.byteOffset, data.edge_sources.byteOffset + data.edge_sources.byteLength) : data.edge_sources
  );
  const tgts = new Int32Array(
    data.edge_targets instanceof Uint8Array ? data.edge_targets.buffer.slice(data.edge_targets.byteOffset, data.edge_targets.byteOffset + data.edge_targets.byteLength) : data.edge_targets
  );

  // Add nodes
  for (let i = 0; i < data.n; i++) {
    const attrs: Record<string, unknown> = {
      x: xs[i],
      y: ys[i],
      size: szs[i],
      label: data.node_ids[i],
      color: data.colors
        ? PALETTE[data.colors[i] % PALETTE.length]
        : "#6366f1",
    };

    // Add extra node attributes
    if (data.node_attrs) {
      for (const [key, values] of Object.entries(data.node_attrs)) {
        attrs[key] = values[i];
      }
    }

    graph.addNode(data.node_ids[i], attrs);
  }

  // Add edges
  for (let i = 0; i < data.m; i++) {
    const src = data.node_ids[srcs[i]];
    const tgt = data.node_ids[tgts[i]];
    if (!graph.hasEdge(src, tgt)) {
      graph.addEdge(src, tgt, { size: 0.5, color: "#2e3039" });
    }
  }

  return graph;
}
