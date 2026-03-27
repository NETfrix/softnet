<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { currentLayout } from "../../lib/graphStore";
  import { computeLayout, listCommunities, pollTask } from "../../lib/api";

  let algorithm = "forceatlas2";
  let iterations = 100;
  let gravity = 1.0;
  let scaling = 2.0;
  let strongGravity = false;
  let computing = false;

  // Community layout options
  let communityKey = "";
  let resolution = 1.0;
  let spacing = 2.0;
  let availableCommunities: string[] = [];

  // Load available communities when switching to community layout
  $: if (algorithm === "community" && $currentProject) {
    loadCommunities();
  }

  async function loadCommunities() {
    if (!$currentProject) return;
    try {
      const res = await listCommunities($currentProject.id) as { communities: Record<string, unknown> };
      availableCommunities = Object.keys(res.communities);
    } catch {
      availableCommunities = [];
    }
  }

  async function run() {
    if (!$currentProject) return;
    computing = true;
    $statusMessage = `Computing ${algorithm} layout...`;

    try {
      const params: Record<string, unknown> = {
        algorithm,
        iterations,
        gravity,
        scaling,
        strong_gravity: strongGravity,
        barnes_hut: true,
      };

      if (algorithm === "community") {
        params.community_key = communityKey || null;
        params.resolution = resolution;
        params.spacing = spacing;
      }

      const { task_id } = await computeLayout($currentProject.id, params) as { task_id: string };

      await pollTask(task_id);
      $currentLayout = algorithm === "community"
        ? `community_${communityKey || "leiden"}`
        : algorithm;
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
        <option value="community">Community Layout</option>
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

  {#if algorithm === "community"}
    <div class="row">
      <label>
        Community partition
        <select bind:value={communityKey}>
          <option value="">Auto-detect (Leiden)</option>
          {#each availableCommunities as key}
            <option value={key}>{key}</option>
          {/each}
        </select>
      </label>
    </div>
    {#if !communityKey}
      <div class="row">
        <label>
          Resolution
          <input type="number" bind:value={resolution} min="0.1" max="5" step="0.1" />
        </label>
      </div>
    {/if}
    <div class="row">
      <label>
        Spacing
        <input type="number" bind:value={spacing} min="0.5" max="10" step="0.5" />
      </label>
      <label>
        Internal iterations
        <input type="number" bind:value={iterations} min="10" max="500" />
      </label>
    </div>
    <div class="hint">
      Groups nodes by community. Uses Leiden detection if no partition is selected.
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
  .hint {
    margin-top: 4px;
    font-size: 10px;
    color: var(--text-muted);
    line-height: 1.4;
  }
</style>
