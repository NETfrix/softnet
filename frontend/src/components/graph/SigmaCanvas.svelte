<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import Sigma from "sigma";
  import { graphStore, labelsVisible, deserializeGraph, currentLayout, currentSizeAttr, currentColorAttr } from "../../lib/graphStore";
  import { currentProject, statusMessage } from "../../lib/projectStore";
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

    sigma = new Sigma($graphStore, container, {
      renderEdgeLabels: false,
      labelRenderedSizeThreshold: 6,
      labelFont: "12px sans-serif",
      labelColor: { color: "#e4e4e7" },
      defaultEdgeColor: "#2e3039",
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

  // React to project changes
  $: if ($currentProject) {
    loadGraph();
  }

  // React to graph data changes
  $: if ($graphStore && container) {
    initSigma();
  }

  // React to layout/size/color changes
  $: if ($currentProject && ($currentLayout || $currentSizeAttr || $currentColorAttr)) {
    // Reload on attribute changes (after initial load)
  }

  onMount(() => {
    if ($currentProject) loadGraph();
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
    <LabelToggle />
  </div>
  {#if hoveredNode}
    <NodeTooltip nodeId={hoveredNode} x={tooltipX} y={tooltipY} />
  {/if}
</div>

<style>
  .sigma-wrapper {
    width: 100%;
    height: 100%;
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
</style>
