<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { viewMode, comparisonData } from "../../lib/graphStore";
  import { computeSankey } from "../../lib/api";

  let keyA = "";
  let keyB = "";

  $: communities = $currentProject?.communities || [];

  async function run() {
    if (!$currentProject || !keyA || !keyB) return;
    $statusMessage = "Computing comparison...";

    try {
      const data = await computeSankey($currentProject.id, [keyA, keyB]);
      comparisonData.set(data as Record<string, unknown>);
      $viewMode = "comparison";
      $statusMessage = "";
    } catch (e) {
      $statusMessage = `Comparison failed: ${e}`;
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
    Compare
  </button>
</div>

<style>
  button { width: 100%; }
</style>
