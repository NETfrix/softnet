<script lang="ts">
  import { onMount } from "svelte";
  import type { SankeyData } from "../../lib/types";

  export let data: SankeyData;

  const PALETTE = [
    "#6366f1", "#ec4899", "#f59e0b", "#22c55e", "#06b6d4",
    "#8b5cf6", "#f43f5e", "#eab308", "#10b981", "#0ea5e9",
  ];

  let container: HTMLDivElement;

  function hexToRgba(hex: string, alpha: number): string {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  onMount(async () => {
    const Plotly = await import("plotly.js-dist-min");

    const nodeColors = data.labels.map((_, i) => PALETTE[i % PALETTE.length]);

    // Color each link by its source community node color
    const linkColors = data.sources.map((srcIdx) =>
      hexToRgba(nodeColors[srcIdx], 0.4)
    );

    const trace = {
      type: "sankey" as const,
      orientation: "h" as const,
      node: {
        pad: 15,
        thickness: 20,
        line: { color: "#2e3039", width: 0.5 },
        label: data.labels,
        color: nodeColors,
      },
      link: {
        source: data.sources,
        target: data.targets,
        value: data.values,
        color: linkColors,
      },
    };

    const layout = {
      font: { size: 12, color: "#e4e4e7" },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      margin: { l: 0, r: 0, t: 10, b: 10 },
      height: 400,
    };

    Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
  });
</script>

<div class="sankey" bind:this={container}></div>

<style>
  .sankey {
    width: 100%;
    min-height: 400px;
  }
</style>
