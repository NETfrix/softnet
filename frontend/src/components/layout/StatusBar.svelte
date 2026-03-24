<script lang="ts">
  import { currentProject, statusMessage } from "../../lib/projectStore";
</script>

<div class="statusbar">
  {#if $currentProject}
    <span>{$currentProject.node_count} nodes</span>
    <span>{$currentProject.edge_count} edges</span>
    <span>{$currentProject.directed ? "directed" : "undirected"}</span>
  {/if}
  <span class="spacer" />
  {#if $statusMessage}
    <span class="msg">{$statusMessage}</span>
  {/if}
</div>

<style>
  .statusbar {
    height: var(--statusbar-height);
    background: var(--bg-secondary);
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    padding: 0 12px;
    gap: 16px;
    font-size: 11px;
    color: var(--text-muted);
  }

  .spacer {
    flex: 1;
  }

  .msg {
    color: var(--accent);
  }
</style>
