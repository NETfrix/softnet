<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { currentLayout } from "../../lib/graphStore";
  import { computeLayout, pollTask } from "../../lib/api";

  let algorithm = "forceatlas2";
  let iterations = 100;
  let gravity = 1.0;
  let scaling = 2.0;
  let strongGravity = false;
  let computing = false;

  async function run() {
    if (!$currentProject) return;
    computing = true;
    $statusMessage = `Computing ${algorithm} layout...`;

    try {
      const { task_id } = await computeLayout($currentProject.id, {
        algorithm,
        iterations,
        gravity,
        scaling,
        strong_gravity: strongGravity,
        barnes_hut: true,
      }) as { task_id: string };

      await pollTask(task_id);
      $currentLayout = algorithm;
      $statusMessage = "";
    } catch (e) {
      $statusMessage = `Layout failed: ${e}`;
    } finally {
      computing = false;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Layout</div>

  <div class="row">
    <label>
      Algorithm
      <select bind:value={algorithm}>
        <option value="forceatlas2">MultiGravity ForceAtlas2</option>
        <option value="yifan_hu">Yifan Hu</option>
      </select>
    </label>
  </div>

  {#if algorithm === "forceatlas2"}
    <div class="row">
      <label>
        Iterations
        <input type="number" bind:value={iterations} min="10" max="1000" />
      </label>
      <label>
        Gravity
        <input type="number" bind:value={gravity} min="0.1" max="10" step="0.1" />
      </label>
    </div>
    <div class="row">
      <label>
        Scaling
        <input type="number" bind:value={scaling} min="0.1" max="10" step="0.1" />
      </label>
      <label class="checkbox-label">
        <input type="checkbox" bind:checked={strongGravity} />
        Strong gravity
      </label>
    </div>
  {/if}

  <button on:click={run} disabled={computing}>
    {computing ? "Computing..." : "Compute Layout"}
  </button>
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
    margin-top: 16px;
  }
</style>
