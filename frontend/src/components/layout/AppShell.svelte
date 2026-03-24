<script lang="ts">
  import Toolbar from "./Toolbar.svelte";
  import Sidebar from "./Sidebar.svelte";
  import StatusBar from "./StatusBar.svelte";
  import SigmaCanvas from "../graph/SigmaCanvas.svelte";
  import { currentProject } from "../../lib/projectStore";
</script>

<div class="shell">
  <Toolbar />
  <div class="main">
    <Sidebar />
    <div class="canvas-area">
      {#if $currentProject}
        <SigmaCanvas />
      {:else}
        <div class="empty">
          <p>Upload a graph to get started</p>
          <p class="sub">CSV edge list, GEXF, or GraphML</p>
        </div>
      {/if}
    </div>
  </div>
  <StatusBar />
</div>

<style>
  .shell {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
  }

  .main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .canvas-area {
    flex: 1;
    position: relative;
    background: var(--bg-primary);
  }

  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
  }

  .empty .sub {
    font-size: 13px;
    margin-top: 4px;
  }
</style>
