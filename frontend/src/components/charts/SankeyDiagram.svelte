<script lang="ts">
  import { onMount } from "svelte";
  import type { SankeyData } from "../../lib/types";

  export let data: SankeyData;

  let container: HTMLDivElement;

  onMount(async () => {
    const Plotly = await import("plotly.js-dist-min");

    const trace = {
      type: "sankey" as const,
      orientation: "h" as const,
      node: {
        pad: 15,
        thickness: 20,
        line: { color: "#2e3039", width: 0.5 },
        label: data.labels,
        color: data.labels.map((_, i) => {
          const palette = [
            "#6366f1", "#ec4899", "#f59e0b", "#22c55e", "#06b6d4",
            "#8b5cf6", "#f43f5e", "#eab308", "#10b981", "#0ea5e9",
          ];
          return palette[i % palette.length];
        }),
      },
      link: {
        source: data.sources,
        target: data.targets,
        value: data.values,
        color: data.sources.map(() => "rgba(99, 102, 241, 0.2)"),
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
