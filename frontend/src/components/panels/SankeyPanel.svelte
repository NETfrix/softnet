<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { computeSankey } from "../../lib/api";
  import SankeyDiagram from "../charts/SankeyDiagram.svelte";
  import type { SankeyData } from "../../lib/types";

  let keyA = "";
  let keyB = "";
  let data: SankeyData | null = null;
  let showModal = false;

  $: communities = $currentProject?.communities || [];

  async function run() {
    if (!$currentProject || !keyA || !keyB) return;
    $statusMessage = "Computing Sankey...";

    try {
      data = await computeSankey($currentProject.id, [keyA, keyB]);
      showModal = true;
      $statusMessage = "";
    } catch (e) {
      $statusMessage = `Sankey failed: ${e}`;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Compare Communities</div>

  <div class="row">
    <label>
      Partition A
      <select bind:value={keyA}>
        <option value="">Select...</option>
        {#each communities as c}
          <option value={c}>{c}</option>
        {/each}
      </select>
    </label>
  </div>

  <div class="row">
    <label>
      Partition B
      <select bind:value={keyB}>
        <option value="">Select...</option>
        {#each communities as c}
          <option value={c}>{c}</option>
        {/each}
      </select>
    </label>
  </div>

  <button on:click={run} disabled={!keyA || !keyB || keyA === keyB}>
    Sankey Diagram
  </button>

  {#if data && !showModal}
    <div class="metrics">
      <div><span class="lbl">NMI:</span> {data.nmi.toFixed(4)}</div>
      <div><span class="lbl">ARI:</span> {data.ari.toFixed(4)}</div>
    </div>
  {/if}
</div>

{#if showModal && data}
  <div class="modal-backdrop" on:click={() => (showModal = false)} on:keydown={() => {}}>
    <div class="modal" on:click|stopPropagation on:keydown|stopPropagation>
      <div class="modal-header">
        <span>Community Comparison</span>
        <button on:click={() => (showModal = false)}>X</button>
      </div>
      <div class="modal-body">
        <SankeyDiagram {data} />
        <div class="metrics">
          <div><span class="lbl">NMI:</span> {data.nmi.toFixed(4)}</div>
          <div><span class="lbl">ARI:</span> {data.ari.toFixed(4)}</div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  button { width: 100%; }
  .metrics {
    margin-top: 8px;
    font-size: 12px;
    color: var(--text-secondary);
  }
  .lbl { color: var(--text-muted); }

  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
  }

  .modal {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    width: 700px;
    max-height: 80vh;
    overflow: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    font-weight: 600;
  }

  .modal-header button {
    width: auto;
    padding: 4px 8px;
  }

  .modal-body {
    padding: 16px;
  }
</style>
