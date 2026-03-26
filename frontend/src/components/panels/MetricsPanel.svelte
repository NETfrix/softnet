<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { getDensity, getConnectedComponents, getClusteringCoefficient, getReciprocity, runErgm, pollTask } from "../../lib/api";

  let density: number | null = null;
  let components: { count: number; largest_size: number; components: { rank: number; component_id: number; size: number }[] } | null = null;
  let clustering: { clustering_coefficient: number; mode: string } | null = null;
  let clusteringMode = "global";
  let reciprocityVal: number | null = null;
  let reciprocityError: string | null = null;
  let ergmTerms = "edges";
  let ergmMethod = "mple";
  let ergmResult: Record<string, unknown> | null = null;
  let computing = false;

  async function fetchDensity() {
    if (!$currentProject) return;
    try {
      const result = await getDensity($currentProject.id) as { density: number };
      density = result.density;
    } catch (e) {
      $statusMessage = `Density failed: ${e}`;
    }
  }

  async function fetchComponents() {
    if (!$currentProject) return;
    try {
      components = await getConnectedComponents($currentProject.id) as typeof components;
    } catch (e) {
      $statusMessage = `Components failed: ${e}`;
    }
  }

  async function fetchClustering() {
    if (!$currentProject) return;
    try {
      clustering = await getClusteringCoefficient($currentProject.id, clusteringMode) as typeof clustering;
    } catch (e) {
      $statusMessage = `Clustering failed: ${e}`;
    }
  }

  async function fetchReciprocity() {
    if (!$currentProject) return;
    try {
      const result = await getReciprocity($currentProject.id) as { reciprocity: number | null; error?: string };
      reciprocityVal = result.reciprocity;
      reciprocityError = result.error || null;
    } catch (e) {
      $statusMessage = `Reciprocity failed: ${e}`;
    }
  }

  async function runErgmModel() {
    if (!$currentProject) return;
    computing = true;
    $statusMessage = "Fitting ERGM...";

    try {
      const terms = ergmTerms.split(",").map((t) => t.trim()).filter(Boolean);
      const { task_id } = await runErgm($currentProject.id, { terms, method: ergmMethod }) as { task_id: string };
      const task = await pollTask(task_id, 3000);
      ergmResult = task.result || null;
      $statusMessage = "ERGM done";
    } catch (e) {
      $statusMessage = `ERGM failed: ${e}`;
    } finally {
      computing = false;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Network Metrics</div>

  <button on:click={fetchDensity}>Compute Density</button>
  {#if density !== null}
    <div class="metric">Density: {density.toFixed(6)}</div>
  {/if}

  <button on:click={fetchComponents}>Connected Components</button>
  {#if components}
    <div class="metric">
      Components: {components.count} | Largest: {components.largest_size} nodes
    </div>
    {#if components.components.length > 1}
      <div class="metric-detail">
        {#each components.components.slice(0, 10) as comp}
          <div>#{comp.rank}: {comp.size} nodes</div>
        {/each}
        {#if components.components.length > 10}
          <div>... and {components.components.length - 10} more</div>
        {/if}
      </div>
    {/if}
  {/if}

  <div class="inline-row">
    <button on:click={fetchClustering} style="flex:1">Clustering Coefficient</button>
    <select bind:value={clusteringMode}>
      <option value="global">Global</option>
      <option value="local">Local (avg)</option>
    </select>
  </div>
  {#if clustering}
    <div class="metric">
      {clustering.mode} clustering: {clustering.clustering_coefficient.toFixed(6)}
    </div>
  {/if}

  <button on:click={fetchReciprocity}>Reciprocity</button>
  {#if reciprocityVal !== null}
    <div class="metric">Reciprocity: {reciprocityVal.toFixed(6)}</div>
  {:else if reciprocityError}
    <div class="note">{reciprocityError}</div>
  {/if}

  <div class="ergm-section">
    <div class="sub-title">ERGM</div>
    <label>
      Method
      <select bind:value={ergmMethod}>
        <option value="mple">MPLE (fast, Python)</option>
        <option value="mcmc">MCMC-MLE (R via WSL)</option>
        <option value="mple_mcmc">MPLE + MCMC (seeded, fastest MCMC)</option>
      </select>
    </label>
    <label>
      Terms (comma-separated)
      <input bind:value={ergmTerms} placeholder="edges, mutual, triangles, gwesp(0.5)" />
    </label>
    <button on:click={runErgmModel} disabled={computing}>
      {computing ? "Fitting ERGM..." : "Fit ERGM"}
    </button>
    {#if computing}
      <div class="progress-bar"><div class="progress-fill"></div></div>
    {/if}
    <div class="note">
      Terms: edges, mutual, triangles, gwesp(alpha), nodematch(attr), nodecov(attr), absdiff(attr)
    </div>

    {#if ergmResult}
      <div class="ergm-results">
        <div class="ergm-formula">{ergmResult.formula}</div>
        <div class="ergm-meta">
          Method: {ergmResult.method} | Dyads: {ergmResult.n_dyads?.toLocaleString()} | Edges: {ergmResult.n_edges?.toLocaleString()}
        </div>
        <table class="ergm-table">
          <thead>
            <tr><th>Term</th><th>Coef</th><th>SE</th><th>z</th></tr>
          </thead>
          <tbody>
            {#each Object.entries(ergmResult.coefficients || {}) as [term, coef]}
              <tr>
                <td>{term}</td>
                <td>{Number(coef).toFixed(4)}</td>
                <td>{ergmResult.std_errors?.[term] != null ? Number(ergmResult.std_errors[term]).toFixed(4) : "—"}</td>
                <td>{ergmResult.z_values?.[term] != null ? Number(ergmResult.z_values[term]).toFixed(2) : "—"}</td>
              </tr>
            {/each}
          </tbody>
        </table>
        <div class="ergm-fit">
          AIC: {Number(ergmResult.aic).toFixed(1)} | BIC: {Number(ergmResult.bic).toFixed(1)} | LL: {Number(ergmResult.log_likelihood).toFixed(1)}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  button { width: 100%; margin-bottom: 4px; }
  .metric {
    font-size: 12px;
    color: var(--text-primary);
    font-family: var(--font-mono);
    margin: 4px 0 8px;
  }
  .metric-detail {
    font-size: 11px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
    margin: 0 0 8px 8px;
  }
  .metric-detail div {
    margin: 1px 0;
  }
  .inline-row {
    display: flex;
    gap: 4px;
    margin-bottom: 4px;
  }
  .inline-row select {
    width: 90px;
    font-size: 11px;
  }
  .ergm-section {
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
  .note {
    font-size: 10px;
    color: var(--warning);
    margin-top: 4px;
  }
  .progress-bar {
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    margin: 4px 0;
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    width: 30%;
    background: var(--accent);
    border-radius: 2px;
    animation: slide 1.2s ease-in-out infinite;
  }
  @keyframes slide {
    0% { transform: translateX(-100%); width: 30%; }
    50% { width: 60%; }
    100% { transform: translateX(350%); width: 30%; }
  }
  .ergm-results {
    margin-top: 8px;
    font-size: 11px;
    color: var(--text-secondary);
  }
  .ergm-formula {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--accent);
    margin-bottom: 4px;
  }
  .ergm-meta {
    font-size: 10px;
    color: var(--text-muted);
    margin-bottom: 6px;
  }
  .ergm-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-mono);
    font-size: 11px;
  }
  .ergm-table th {
    text-align: left;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
    padding: 2px 4px;
    font-weight: 600;
  }
  .ergm-table td {
    padding: 2px 4px;
    color: var(--text-primary);
  }
  .ergm-fit {
    margin-top: 6px;
    font-size: 10px;
    color: var(--text-muted);
    font-family: var(--font-mono);
  }
</style>
