<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { enrichNodes } from "../../lib/api";

  let nodeIds = "";
  let sources = ["wikipedia"];
  let results: Array<{ node_id: string; data: Record<string, unknown> }> = [];
  let enriching = false;

  async function run() {
    if (!$currentProject || !nodeIds.trim()) return;
    enriching = true;
    $statusMessage = "Enriching nodes...";

    try {
      const ids = nodeIds.split(",").map((s) => s.trim()).filter(Boolean);
      const response = await enrichNodes($currentProject.id, ids, sources) as {
        results: Array<{ node_id: string; data: Record<string, unknown> }>;
      };
      results = response.results;
      $statusMessage = `Enriched ${results.length} nodes`;
    } catch (e) {
      $statusMessage = `Enrichment failed: ${e}`;
    } finally {
      enriching = false;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Enrichment</div>

  <div class="row">
    <label>
      Node IDs (comma-separated)
      <input bind:value={nodeIds} placeholder="node1, node2, ..." />
    </label>
  </div>

  <div class="row">
    <label class="checkbox-label">
      <input
        type="checkbox"
        checked={sources.includes("wikipedia")}
        on:change={(e) => {
          if (e.currentTarget.checked) sources = [...sources, "wikipedia"];
          else sources = sources.filter((s) => s !== "wikipedia");
        }}
      />
      Wikipedia
    </label>
    <label class="checkbox-label">
      <input
        type="checkbox"
        checked={sources.includes("wikidata")}
        on:change={(e) => {
          if (e.currentTarget.checked) sources = [...sources, "wikidata"];
          else sources = sources.filter((s) => s !== "wikidata");
        }}
      />
      Wikidata
    </label>
    <label class="checkbox-label">
      <input
        type="checkbox"
        checked={sources.includes("websearch")}
        on:change={(e) => {
          if (e.currentTarget.checked) sources = [...sources, "websearch"];
          else sources = sources.filter((s) => s !== "websearch");
        }}
      />
      Web Search
    </label>
  </div>

  <button on:click={run} disabled={enriching || !nodeIds.trim()}>
    {enriching ? "Enriching..." : "Enrich Nodes"}
  </button>

  {#if results.length}
    <div class="results">
      {#each results as r}
        <div class="result-item">
          <strong>{r.node_id}</strong>
          {#if r.data.title}
            <div>{r.data.title}</div>
          {/if}
          {#if r.data.extract}
            <div class="extract">{String(r.data.extract).slice(0, 150)}...</div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  button { width: 100%; }
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-direction: row;
    font-size: 13px;
    color: var(--text-primary);
  }
  .results {
    margin-top: 8px;
    font-size: 12px;
    max-height: 200px;
    overflow-y: auto;
  }
  .result-item {
    padding: 6px 0;
    border-bottom: 1px solid var(--border);
  }
  .extract {
    color: var(--text-muted);
    font-size: 11px;
    margin-top: 2px;
  }
</style>
