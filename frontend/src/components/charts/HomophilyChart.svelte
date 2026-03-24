<script lang="ts">
  import { onMount } from "svelte";

  export let distributions: Record<string, Record<string, number>>;
  export let attribute: string;

  let container: HTMLDivElement;

  onMount(async () => {
    const Plotly = await import("plotly.js-dist-min");

    const communities = Object.keys(distributions);
    const allValues = new Set<string>();
    for (const dist of Object.values(distributions)) {
      for (const v of Object.keys(dist)) allValues.add(v);
    }
    const attrValues = [...allValues].sort();

    const traces = communities.map((comm) => ({
      x: attrValues,
      y: attrValues.map((v) => distributions[comm]?.[v] || 0),
      name: `Community ${comm}`,
      type: "bar" as const,
    }));

    const layout = {
      title: { text: `${attribute} by community`, font: { size: 13, color: "#e4e4e7" } },
      barmode: "group" as const,
      font: { size: 11, color: "#a1a1aa" },
      paper_bgcolor: "transparent",
      plot_bgcolor: "transparent",
      xaxis: { gridcolor: "#2e3039" },
      yaxis: { gridcolor: "#2e3039" },
      margin: { l: 40, r: 10, t: 30, b: 30 },
      height: 300,
    };

    Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
  });
</script>

<div bind:this={container}></div>
