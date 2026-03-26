<script lang="ts">
  import UploadPanel from "../panels/UploadPanel.svelte";
  import LayoutPanel from "../panels/LayoutPanel.svelte";
  import CentralityPanel from "../panels/CentralityPanel.svelte";
  import CommunityPanel from "../panels/CommunityPanel.svelte";
  import HomophilyPanel from "../panels/HomophilyPanel.svelte";
  import MetricsPanel from "../panels/MetricsPanel.svelte";
  import SankeyPanel from "../panels/SankeyPanel.svelte";
  import EnrichmentPanel from "../panels/EnrichmentPanel.svelte";
  import { currentProject } from "../../lib/projectStore";
</script>

<div class="sidebar">
  <UploadPanel />

  {#if $currentProject}
    <div class="section">
      <div class="section-label">Layout</div>
      <LayoutPanel />
    </div>

    <div class="section">
      <div class="section-label">Analysis</div>
      <CentralityPanel />
      <CommunityPanel />
      <HomophilyPanel />
      <SankeyPanel />
      <MetricsPanel />
    </div>

    <div class="section">
      <div class="section-label">Data</div>
      <EnrichmentPanel />
    </div>
  {/if}
</div>

<style>
  .sidebar {
    width: var(--sidebar-width);
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    overflow-y: auto;
    flex-shrink: 0;
  }

  .section {
    border-top: 2px solid var(--border);
  }

  .section-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    padding: 8px 12px 2px;
  }
</style>
