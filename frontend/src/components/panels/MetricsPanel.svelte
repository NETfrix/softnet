<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
  import { getDensity, runErgm, pollTask } from "../../lib/api";

  let density: number | null = null;
  let ergmTerms = "edges";
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

  async function runErgmModel() {
    if (!$currentProject) return;
    computing = true;
    $statusMessage = "Fitting ERGM...";

    try {
      const terms = ergmTerms.split(",").map((t) => t.trim()).filter(Boolean);
      const { task_id } = await runErgm($currentProject.id, { terms }) as { task_id: string };
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

  <div class="ergm-section">
    <div class="sub-title">ERGM</div>
    <label>
      Terms (comma-separated)
      <input bind:value={ergmTerms} placeholder="edges, mutual, gwesp(0.5, fixed=TRUE)" />
    </label>
    <button on:click={runErgmModel} disabled={computing}>
      {computing ? "Fitting..." : "Fit ERGM"}
    </button>
    <div class="note">Requires R + statnet. Max ~5000 nodes.</div>

    {#if ergmResult}
      <div class="ergm-results">
        <pre>{JSON.stringify(ergmResult, null, 2)}</pre>
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
  .ergm-results pre {
    font-size: 11px;
    background: var(--bg-primary);
    padding: 8px;
    border-radius: 4px;
    overflow-x: auto;
    margin-top: 8px;
    color: var(--text-secondary);
  }
</style>
