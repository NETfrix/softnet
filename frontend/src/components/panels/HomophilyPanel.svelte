<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { computeHomophily } from "../../lib/api";
  import type { HomophilyResult } from "../../lib/types";

  let communityKey = "";
  let attribute = "";
  let result: HomophilyResult | null = null;

  $: communities = $currentProject?.communities || [];

  async function run() {
    if (!$currentProject || !communityKey) return;
    $statusMessage = "Computing homophily...";

    try {
      result = await computeHomophily($currentProject.id, {
        community_key: communityKey,
        attribute: attribute || null,
      });
      $statusMessage = "";
    } catch (e) {
      $statusMessage = `Homophily failed: ${e}`;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Homophily</div>

  <div class="row">
    <label>
      Community
      <select bind:value={communityKey}>
        <option value="">Select...</option>
        {#each communities as c}
          <option value={c}>{c}</option>
        {/each}
      </select>
    </label>
  </div>

  <div class="row">
    <label>
      Attribute (optional)
      <input bind:value={attribute} placeholder="Node attribute name" />
    </label>
  </div>

  <button on:click={run} disabled={!communityKey}>Compute Homophily</button>

  {#if result}
    <div class="results">
      <div class="metric">
        <span class="lbl">E-I Index:</span>
        <span class="val">{result.ei_index.toFixed(4)}</span>
      </div>
      <div class="metric">
        <span class="lbl">Internal:</span>
        <span class="val">{result.internal_edges}</span>
      </div>
      <div class="metric">
        <span class="lbl">External:</span>
        <span class="val">{result.external_edges}</span>
      </div>
      <div class="interpretation">
        {#if result.ei_index < -0.5}
          Strong homophily
        {:else if result.ei_index < 0}
          Moderate homophily
        {:else if result.ei_index < 0.5}
          Moderate heterophily
        {:else}
          Strong heterophily
        {/if}
      </div>

      {#if result.newman_assortativity != null}
        <div class="sub-title">Newman Assortativity</div>
        <div class="metric">
          <span class="lbl">Score:</span>
          <span class="val">{result.newman_assortativity.toFixed(4)}</span>
        </div>
        <div class="interpretation">
          {#if result.newman_assortativity > 0.3}
            Strong assortative mixing (homophilic)
          {:else if result.newman_assortativity > 0}
            Weak assortative mixing
          {:else if result.newman_assortativity > -0.3}
            Weak disassortative mixing
          {:else}
            Strong disassortative mixing (heterophilic)
          {/if}
        </div>
      {/if}

      {#if result.newman_community_scores}
        <div class="sub-title">Per-Community Newman Scores</div>
        <div class="community-table">
          {#each Object.entries(result.newman_community_scores) as [commId, scores]}
            <div class="metric">
              <span class="lbl">Community {commId}:</span>
              <span class="val">{scores.newman_score?.toFixed(4) ?? "N/A"}</span>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  button { width: 100%; }
  .results {
    margin-top: 8px;
    font-size: 12px;
  }
  .metric {
    display: flex;
    justify-content: space-between;
    padding: 2px 0;
  }
  .lbl { color: var(--text-muted); }
  .val { color: var(--text-primary); font-family: var(--font-mono); }
  .interpretation {
    margin-top: 4px;
    color: var(--accent);
    font-size: 11px;
  }
  .sub-title {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    margin: 8px 0 4px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
  }
  .community-table {
    max-height: 150px;
    overflow-y: auto;
  }
</style>
