<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { computeCentrality, pollTask, getProject } from "../../lib/api";

  let algorithm = "degree";
  let mode = "all";
  let damping = 0.85;
  let directed = true;
  let computing = false;

  async function run() {
    if (!$currentProject) return;
    computing = true;
    $statusMessage = `Computing ${algorithm}...`;

    try {
      const { task_id } = await computeCentrality($currentProject.id, {
        algorithm,
        mode,
        damping,
        directed,
        normalized: true,
      }) as { task_id: string };

      await pollTask(task_id);
      $currentProject = await getProject($currentProject.id);
      $statusMessage = `${algorithm} done`;
    } catch (e) {
      $statusMessage = `${algorithm} failed: ${e}`;
    } finally {
      computing = false;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Centrality</div>

  <div class="row">
    <label>
      Algorithm
      <select bind:value={algorithm}>
        <option value="degree">Degree</option>
        <option value="betweenness">Betweenness</option>
        <option value="closeness">Closeness</option>
        <option value="pagerank">PageRank</option>
      </select>
    </label>
  </div>

  {#if algorithm === "degree"}
    <div class="row">
      <label>
        Mode
        <select bind:value={mode}>
          <option value="all">All</option>
          <option value="in">In-degree</option>
          <option value="out">Out-degree</option>
        </select>
      </label>
    </div>
  {/if}

  {#if algorithm === "pagerank"}
    <div class="row">
      <label>
        Damping
        <input type="number" bind:value={damping} min="0" max="1" step="0.05" />
      </label>
    </div>
  {/if}

  {#if ["betweenness", "pagerank"].includes(algorithm)}
    <div class="row">
      <label class="checkbox-label">
        <input type="checkbox" bind:checked={directed} />
        Directed
      </label>
    </div>
  {/if}

  <button on:click={run} disabled={computing}>
    {computing ? "Computing..." : "Compute"}
  </button>

  {#if $currentProject?.centralities.length}
    <div class="computed">
      Computed: {$currentProject.centralities.join(", ")}
    </div>
  {/if}
</div>

<style>
  button { width: 100%; }
  .computed {
    margin-top: 8px;
    font-size: 11px;
    color: var(--text-muted);
  }
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-direction: row;
    font-size: 13px;
    color: var(--text-primary);
  }
</style>
