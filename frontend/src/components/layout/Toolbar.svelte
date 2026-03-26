<script lang="ts">
  import { currentProject, projects } from "../../lib/projectStore";
  import { listProjects, getProject } from "../../lib/api";
  import { onMount } from "svelte";

  onMount(async () => {
    try {
      $projects = await listProjects();
    } catch {}
  });

  async function selectProject(id: string) {
    $currentProject = await getProject(id);
  }
</script>

<div class="toolbar">
  <div class="brand">Softnet <span class="version">0.8</span></div>

  <div class="project-selector">
    {#if $projects.length > 0}
      <select
        value={$currentProject?.id || ""}
        on:change={(e) => selectProject(e.currentTarget.value)}
      >
        <option value="" disabled>Select project</option>
        {#each $projects as p}
          <option value={p.id}>{p.name} ({p.node_count}n / {p.edge_count}e)</option>
        {/each}
      </select>
    {/if}
  </div>

  <div class="spacer" />
</div>

<style>
  .toolbar {
    height: var(--toolbar-height);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 12px;
    gap: 12px;
  }

  .brand {
    font-weight: 700;
    font-size: 15px;
    color: var(--accent);
    letter-spacing: 0.5px;
  }

  .project-selector select {
    min-width: 200px;
  }

  .version {
    font-size: 11px;
    font-weight: 400;
    color: var(--text-muted);
  }

  .spacer {
    flex: 1;
  }
</style>
