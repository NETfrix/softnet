<script lang="ts">
  import { onMount } from "svelte";

  export let values: number[];
  export let title: string = "Distribution";

  let container: HTMLDivElement;

  onMount(async () => {
    const Plotly = await import("plotly.js-dist-min");

    const trace = {
      x: values,
      type: "histogram" as const,
      marker: { color: "#6366f1" },
      nbinsx: 50,
    };

    const layout = {
      title: { text: title, font: { size: 13, color: "#e4e4e7" } },
      font: { size: 11, color: "#a1a1aa" },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      xaxis: { gridcolor: "#2e3039" },
      yaxis: { gridcolor: "#2e3039" },
      margin: { l: 40, r: 10, t: 30, b: 30 },
      height: 250,
    };

    Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
  });
</script>

<div bind:this={container}></div>
