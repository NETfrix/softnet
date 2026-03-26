<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { currentColorAttr } from "../../lib/graphStore";
  import { detectCommunity, getCommunityGraph, pollTask, getProject } from "../../lib/api";

  let algorithm = "leiden";
  let resolution = 1.0;
  let quality = "modularity";
  let model = "nested";
  let degCorr = true;
  let numTrials = 10;
  let directedInfomap = true;
  let computing = false;
  let communityGraphKey = "";
  let communityGraph: { nodes: { id: number; name: string; size: number }[]; edges: { source: number; target: number; weight: number }[] } | null = null;

  async function fetchCommunityGraph() {
    if (!$currentProject || !communityGraphKey) return;
    try {
      const result = await getCommunityGraph($currentProject.id, communityGraphKey);
      communityGraph = result as typeof communityGraph;
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
      const result = await pollTask(task_id);

      $currentProject = await getProject($currentProject.id);

      // Auto-color by this community
      if (result.result && typeof result.result === "object" && "key" in result.result) {
        $currentColorAttr = result.result.key as string;
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
        <input type="number" bind:value={resolution} min="0.01" max="10" step="0.1" />
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

      {#if communityGraph}
        <div class="comm-graph-info">
          <div>{communityGraph.nodes.length} communities, {communityGraph.edges.length} edges</div>
          {#each communityGraph.nodes as node}
            <div class="comm-node">{node.name}: {node.size} nodes</div>
          {/each}
        </div>
      {/if}
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
  .comm-graph-info {
    margin-top: 8px;
    font-size: 11px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
  }
  .comm-node {
    margin: 1px 0 1px 8px;
  }
</style>
