<script lang="ts">
  import Toolbar from "./Toolbar.svelte";
  import Sidebar from "./Sidebar.svelte";
  import StatusBar from "./StatusBar.svelte";
  import SigmaCanvas from "../graph/SigmaCanvas.svelte";
  import CommunityGraphView from "../graph/CommunityGraphView.svelte";
  import ComparisonView from "../graph/ComparisonView.svelte";
  import { currentProject } from "../../lib/projectStore";
  import { viewMode, communityGraphData, comparisonData } from "../../lib/graphStore";
</script>

<div class="shell">
  <Toolbar />
  <div class="main">
    <Sidebar />
    <div class="canvas-area">
      {#if $currentProject}
        {#if $communityGraphData || $comparisonData}
          <div class="view-tabs">
            <button
              class:active={$viewMode === "graph"}
              on:click={() => ($viewMode = "graph")}
            >
              Node Graph
            </button>
            {#if $communityGraphData}
              <button
                class:active={$viewMode === "community-graph"}
                on:click={() => ($viewMode = "community-graph")}
              >
                Community Graph
              </button>
            {/if}
            {#if $comparisonData}
              <button
                class:active={$viewMode === "comparison"}
                on:click={() => ($viewMode = "comparison")}
              >
                Comparison
              </button>
            {/if}
          </div>
        {/if}

        {#if $viewMode === "graph"}
          <SigmaCanvas />
        {:else if $viewMode === "community-graph" && $communityGraphData}
          <CommunityGraphView />
        {:else if $viewMode === "comparison" && $comparisonData}
          <ComparisonView />
        {:else}
          <SigmaCanvas />
        {/if}
      {:else}
        <div class="empty">
          <p>Upload a graph to get started</p>
          <p class="sub">CSV, Excel, GEXF, GraphML, or Gephi</p>
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
    display: flex;
    flex-direction: column;
  }

  .view-tabs {
    display: flex;
    gap: 0;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }

  .view-tabs button {
    padding: 6px 16px;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid transparent;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 0;
  }

  .view-tabs button:hover {
    color: var(--text-primary);
  }

  .view-tabs button.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
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
