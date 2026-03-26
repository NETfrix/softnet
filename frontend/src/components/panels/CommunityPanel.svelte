<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { currentColorAttr, viewMode, communityGraphData } from "../../lib/graphStore";
  import { detectCommunity, getCommunityGraph, pollTask, getProject } from "../../lib/api";

  let algorithm = "leiden";
  let resolution = 1.0;
  let quality = "modularity";

  // When quality changes to CPM, set default gamma to 0.01
  $: if (quality === "CPM" && resolution === 1.0) {
    resolution = 0.01;
  } else if (quality === "modularity" && resolution === 0.01) {
    resolution = 1.0;
  }
  let model = "nested";
  let degCorr = true;
  let numTrials = 10;
  let directedInfomap = true;
  let computing = false;
  let communityGraphKey = "";
  let lastResult: Record<string, unknown> | null = null;

  async function fetchCommunityGraph() {
    if (!$currentProject || !communityGraphKey) return;
    try {
      const result = await getCommunityGraph($currentProject.id, communityGraphKey);
      communityGraphData.set(result as typeof $communityGraphData);
      $viewMode = "community-graph";
      $statusMessage = "Community graph created";
    } catch (e) {
      $statusMessage = `Community graph failed: ${e}`;
    }
  }

  async function run() {
    if (!$currentProject) return;
    computing = true;
    $statusMessage = `Detecting communities (${algorithm})...`;

    try {
      const params: Record<string, unknown> = { algorithm, resolution, quality };
      if (algorithm === "sbm") {
        params.model = model;
        params.deg_corr = degCorr;
      }
      if (algorithm === "infomap") {
        params.num_trials = numTrials;
        params.directed = directedInfomap;
      }

      const { task_id } = await detectCommunity($currentProject.id, params) as { task_id: string };
      const task = await pollTask(task_id);
      lastResult = (task.result as Record<string, unknown>) || null;

      $currentProject = await getProject($currentProject.id);

      // Auto-color by this community
      if (lastResult && "key" in lastResult) {
        $currentColorAttr = lastResult.key as string;
      }

      $statusMessage = `${algorithm} done`;
    } catch (e) {
      $statusMessage = `${algorithm} failed: ${e}`;
    } finally {
      computing = false;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Community Detection</div>

  <div class="row">
    <label>
      Algorithm
      <select bind:value={algorithm}>
        <option value="louvain">Louvain</option>
        <option value="leiden">Leiden</option>
        <option value="sbm">Bayesian SBM (Peixoto)</option>
        <option value="infomap">Infomap</option>
      </select>
    </label>
  </div>

  {#if ["louvain", "leiden"].includes(algorithm)}
    <div class="row">
      <label>
        Resolution (gamma)
        <input type="number" bind:value={resolution} min="0.001" max="10" step="0.01" />
      </label>
      <label>
        Quality
        <select bind:value={quality}>
          <option value="modularity">Modularity</option>
          <option value="CPM">CPM</option>
        </select>
      </label>
    </div>
  {/if}

  {#if algorithm === "sbm"}
    <div class="row">
      <label>
        Model
        <select bind:value={model}>
          <option value="nested">Nested</option>
          <option value="flat">Flat</option>
        </select>
      </label>
      <label class="checkbox-label">
        <input type="checkbox" bind:checked={degCorr} />
        Degree-corrected
      </label>
    </div>
    <div class="note">Runs via WSL (graph-tool)</div>
  {/if}

  {#if algorithm === "infomap"}
    <div class="row">
      <label>
        Trials
        <input type="number" bind:value={numTrials} min="1" max="100" />
      </label>
      <label class="checkbox-label">
        <input type="checkbox" bind:checked={directedInfomap} />
        Directed
      </label>
    </div>
  {/if}

  <button on:click={run} disabled={computing}>
    {computing ? "Detecting..." : "Detect Communities"}
  </button>

  {#if lastResult}
    <div class="result-info">
      <div class="metric-row">
        <span class="lbl">Communities:</span>
        <span class="val">{lastResult.n_communities}</span>
      </div>
      {#if lastResult.cpm_quality != null}
        <div class="metric-row">
          <span class="lbl">H (CPM quality):</span>
          <span class="val">{Number(lastResult.cpm_quality).toFixed(4)}</span>
        </div>
      {:else if lastResult.modularity != null}
        <div class="metric-row">
          <span class="lbl">Modularity:</span>
          <span class="val">{Number(lastResult.modularity).toFixed(4)}</span>
        </div>
      {/if}
    </div>
  {/if}

  {#if $currentProject?.communities.length}
    <div class="computed">
      Detected: {$currentProject.communities.join(", ")}
    </div>

    <div class="comm-graph-section">
      <div class="sub-title">Community Graph</div>
      <div class="row">
        <label>
          Partition
          <select bind:value={communityGraphKey}>
            <option value="">Select...</option>
            {#each $currentProject.communities as c}
              <option value={c}>{c}</option>
            {/each}
          </select>
        </label>
      </div>
      <button on:click={fetchCommunityGraph} disabled={!communityGraphKey}>
        Create Community Graph
      </button>
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
  .note {
    font-size: 11px;
    color: var(--warning);
    margin-bottom: 4px;
  }
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-direction: row;
    font-size: 13px;
    color: var(--text-primary);
    margin-top: 16px;
  }
  .result-info {
    margin-top: 8px;
    padding: 6px 8px;
    background: var(--bg-primary);
    border-radius: 4px;
    font-size: 12px;
  }
  .metric-row {
    display: flex;
    justify-content: space-between;
    padding: 1px 0;
  }
  .lbl { color: var(--text-muted); }
  .val { color: var(--text-primary); font-family: var(--font-mono); }
  .comm-graph-section {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
  }
  .sub-title {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 6px;
  }
</style>
