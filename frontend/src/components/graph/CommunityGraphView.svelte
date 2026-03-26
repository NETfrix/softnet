<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import Sigma from "sigma";
  import Graph from "graphology";
  import { communityGraphData } from "../../lib/graphStore";
  import circular from "graphology-layout/circular";

  const PALETTE = [
    "#6366f1", "#ec4899", "#f59e0b", "#22c55e", "#06b6d4",
    "#8b5cf6", "#f43f5e", "#eab308", "#10b981", "#0ea5e9",
  ];

  let container: HTMLDivElement;
  let sigma: Sigma | null = null;

  function buildGraph() {
    if (!$communityGraphData || !container) return;

    if (sigma) sigma.kill();

    const graph = new Graph({ type: "undirected", allowSelfLoops: true, multi: false });

    const maxSize = Math.max(...$communityGraphData.nodes.map((n) => n.size));

    $communityGraphData.nodes.forEach((node, i) => {
      graph.addNode(String(node.id), {
        label: `${node.name} (${node.size})`,
        size: 8 + (node.size / maxSize) * 30,
        color: PALETTE[i % PALETTE.length],
        x: 0,
        y: 0,
      });
    });

    const maxWeight = Math.max(...$communityGraphData.edges.map((e) => e.weight), 1);
    $communityGraphData.edges.forEach((edge) => {
      const key = `${edge.source}-${edge.target}`;
      if (!graph.hasEdge(String(edge.source), String(edge.target))) {
        graph.addEdge(String(edge.source), String(edge.target), {
          size: 1 + (edge.weight / maxWeight) * 6,
          label: String(edge.weight),
          color: edge.source === edge.target ? "#4a4a5a" : "#6366f1aa",
        });
      }
    });

    circular.assign(graph);

    sigma = new Sigma(graph, container, {
      renderEdgeLabels: true,
      labelRenderedSizeThreshold: 0,
      labelFont: "13px sans-serif",
      labelColor: { color: "#e4e4e7" },
      defaultEdgeColor: "#6366f1aa",
      defaultNodeColor: "#6366f1",
      labelDensity: 1,
      zIndex: true,
    });
  }

  $: if ($communityGraphData && container) {
    buildGraph();
  }

  onMount(() => {
    if ($communityGraphData) buildGraph();
  });

  onDestroy(() => {
    if (sigma) sigma.kill();
  });
</script>

<div class="comm-graph-wrapper">
  <div class="comm-graph-container" bind:this={container}></div>
  <div class="info-overlay">
    {#if $communityGraphData}
      {$communityGraphData.nodes.length} communities
    {/if}
  </div>
</div>

<style>
  .comm-graph-wrapper {
    width: 100%;
    flex: 1;
    position: relative;
  }

  .comm-graph-container {
    width: 100%;
    height: 100%;
  }

  .info-overlay {
    position: absolute;
    bottom: 12px;
    left: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
  }
</style>
