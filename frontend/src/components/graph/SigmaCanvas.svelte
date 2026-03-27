<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import Sigma from "sigma";
  import { graphStore, labelsVisible, deserializeGraph, currentLayout, currentSizeAttr, currentColorAttr, edgeScale, labelScale, edgeBrightness } from "../../lib/graphStore";
  import { currentProject, statusMessage, layoutReady } from "../../lib/projectStore";
  import { getGraphData } from "../../lib/api";
  import GraphControls from "./GraphControls.svelte";
  import LabelToggle from "./LabelToggle.svelte";
  import NodeTooltip from "./NodeTooltip.svelte";

  let container: HTMLDivElement;
  let sigma: Sigma | null = null;
  let hoveredNode: string | null = null;
  let tooltipX = 0;
  let tooltipY = 0;

  async function loadGraph() {
    if (!$currentProject) return;
    $statusMessage = "Loading graph...";

    try {
      const buffer = await getGraphData(
        $currentProject.id,
        $currentLayout,
        $currentSizeAttr || undefined,
        $currentColorAttr || undefined
      );
      const graph = deserializeGraph(buffer);
      graphStore.set(graph);
      $statusMessage = "";
    } catch (e) {
      $statusMessage = `Error: ${e}`;
    }
  }

  function initSigma() {
    if (!container || !$graphStore) return;

    if (sigma) {
      sigma.kill();
    }

    const fontSize = Math.round(12 * $labelScale);
    const bright = Math.round($edgeBrightness * 255);
    const edgeColor = `rgb(${bright}, ${bright}, ${Math.round(bright * 1.1)})`;

    sigma = new Sigma($graphStore, container, {
      renderEdgeLabels: false,
      labelRenderedSizeThreshold: 6,
      labelFont: `${fontSize}px sans-serif`,
      labelColor: { color: "#e4e4e7" },
      defaultEdgeColor: edgeColor,
      defaultNodeColor: "#6366f1",
      labelDensity: 0.07,
      labelGridCellSize: 60,
      zIndex: true,
      enableEdgeEvents: false,
    });

    // Hover events
    sigma.on("enterNode", ({ node }) => {
      hoveredNode = node;
      const pos = sigma!.getNodeDisplayData(node);
      if (pos) {
        const viewport = sigma!.graphToViewport(pos);
        tooltipX = viewport.x;
        tooltipY = viewport.y;
      }
    });

    sigma.on("leaveNode", () => {
      hoveredNode = null;
    });
  }

  // React to label visibility toggle
  $: if (sigma) {
    sigma.setSetting("renderLabels", $labelsVisible);
  }

  // React to edge scale / label scale / edge brightness changes — reinit sigma
  let prevEdgeScale = $edgeScale;
  let prevLabelScale = $labelScale;
  let prevBrightness = $edgeBrightness;

  $: {
    if (sigma && $graphStore && (
      $edgeScale !== prevEdgeScale ||
      $labelScale !== prevLabelScale ||
      $edgeBrightness !== prevBrightness
    )) {
      prevEdgeScale = $edgeScale;
      prevLabelScale = $labelScale;
      prevBrightness = $edgeBrightness;

      // Update edge sizes
      $graphStore.forEachEdge((edge) => {
        $graphStore!.setEdgeAttribute(edge, "size", 0.5 * $edgeScale);
      });

      // Update label font and edge color by reiniting
      const fontSize = Math.round(12 * $labelScale);
      const bright = Math.round($edgeBrightness * 255);
      const edgeColor = `rgb(${bright}, ${bright}, ${Math.round(bright * 1.1)})`;
      sigma.setSetting("labelFont", `${fontSize}px sans-serif`);
      sigma.setSetting("defaultEdgeColor", edgeColor);

      // Update existing edge colors
      $graphStore.forEachEdge((edge) => {
        $graphStore!.setEdgeAttribute(edge, "color", edgeColor);
      });

      sigma.refresh();
    }
  }

  // React to project changes — wait until layout is computed
  $: if ($currentProject && $layoutReady) {
    loadGraph();
  }

  // React to graph data changes
  $: if ($graphStore && container) {
    initSigma();
  }

  // React to layout/size/color changes — reload graph data from server
  let prevLayout = $currentLayout;
  let prevSize = $currentSizeAttr;
  let prevColor = $currentColorAttr;

  $: {
    const layoutChanged = $currentLayout !== prevLayout;
    const sizeChanged = $currentSizeAttr !== prevSize;
    const colorChanged = $currentColorAttr !== prevColor;

    if ($currentProject && (layoutChanged || sizeChanged || colorChanged)) {
      prevLayout = $currentLayout;
      prevSize = $currentSizeAttr;
      prevColor = $currentColorAttr;
      loadGraph();
    }
  }

  onMount(() => {
    if ($currentProject && $layoutReady) loadGraph();
  });

  onDestroy(() => {
    if (sigma) sigma.kill();
  });

  export function zoomIn() {
    if (sigma) {
      const camera = sigma.getCamera();
      camera.animatedZoom({ duration: 200 });
    }
  }

  export function zoomOut() {
    if (sigma) {
      const camera = sigma.getCamera();
      camera.animatedUnzoom({ duration: 200 });
    }
  }

  export function fitToScreen() {
    if (sigma) {
      const camera = sigma.getCamera();
      camera.animatedReset({ duration: 300 });
    }
  }
</script>

<div class="sigma-wrapper">
  <div class="sigma-container" bind:this={container}></div>
  <div class="overlay top-right">
    <GraphControls on:zoomIn={zoomIn} on:zoomOut={zoomOut} on:fit={fitToScreen} />
  </div>
  {#if hoveredNode}
    <NodeTooltip nodeId={hoveredNode} x={tooltipX} y={tooltipY} />
  {/if}
  {#if $currentProject}
    <div class="overlay bottom-left network-info">
      <span>{$currentProject.node_count.toLocaleString()} nodes</span>
      <span class="sep">|</span>
      <span>{$currentProject.edge_count.toLocaleString()} edges</span>
      <span class="sep">|</span>
      <span>{$currentProject.directed ? "directed" : "undirected"}</span>
    </div>
  {/if}
</div>

<style>
  .sigma-wrapper {
    width: 100%;
    flex: 1;
    position: relative;
  }

  .sigma-container {
    width: 100%;
    height: 100%;
  }

  .overlay {
    position: absolute;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .overlay.top-right {
    top: 12px;
    right: 12px;
  }

  .overlay.bottom-left {
    bottom: 12px;
    left: 12px;
    flex-direction: row;
  }

  .network-info {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
  }

  .network-info .sep {
    margin: 0 4px;
    opacity: 0.4;
  }
</style>
