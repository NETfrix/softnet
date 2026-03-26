<script lang="ts">
  import SankeyDiagram from "../charts/SankeyDiagram.svelte";
  import { comparisonData } from "../../lib/graphStore";
  import type { SankeyData } from "../../lib/types";

  $: data = $comparisonData as SankeyData | null;
</script>

<div class="comparison-wrapper">
  {#if data}
    <div class="comparison-content">
      <SankeyDiagram {data} />
      <div class="metrics-row">
        <div class="metric"><span class="lbl">NMI:</span> {data.nmi.toFixed(4)}</div>
        <div class="metric"><span class="lbl">ARI:</span> {data.ari.toFixed(4)}</div>
      </div>
    </div>
  {:else}
    <div class="empty-msg">No comparison data</div>
  {/if}
</div>

<style>
  .comparison-wrapper {
    width: 100%;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    overflow: auto;
  }

  .comparison-content {
    width: 100%;
    max-width: 800px;
  }

  .metrics-row {
    display: flex;
    gap: 24px;
    justify-content: center;
    margin-top: 16px;
  }

  .metric {
    font-size: 14px;
    color: var(--text-primary);
    font-family: var(--font-mono);
  }

  .lbl {
    color: var(--text-muted);
  }

  .empty-msg {
    color: var(--text-muted);
    font-size: 14px;
  }
</style>
