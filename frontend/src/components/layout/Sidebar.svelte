<script lang="ts">
  import UploadPanel from "../panels/UploadPanel.svelte";
  import LayoutPanel from "../panels/LayoutPanel.svelte";
  import CentralityPanel from "../panels/CentralityPanel.svelte";
  import CommunityPanel from "../panels/CommunityPanel.svelte";
  import HomophilyPanel from "../panels/HomophilyPanel.svelte";
  import MetricsPanel from "../panels/MetricsPanel.svelte";
  import NodeSizePanel from "../panels/NodeSizePanel.svelte";
  import SankeyPanel from "../panels/SankeyPanel.svelte";
  import EnrichmentPanel from "../panels/EnrichmentPanel.svelte";
  import { currentProject } from "../../lib/projectStore";
</script>

<div class="sidebar">
  <UploadPanel />

  {#if $currentProject}
    <LayoutPanel />
    <CentralityPanel />
    <CommunityPanel />
    <NodeSizePanel />
    <HomophilyPanel />
    <SankeyPanel />
    <MetricsPanel />
    <EnrichmentPanel />
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
</style>
