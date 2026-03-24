<script lang="ts">
  import { graphStore } from "../../lib/graphStore";

  export let nodeId: string;
  export let x: number;
  export let y: number;

  $: attrs = $graphStore?.getNodeAttributes(nodeId) || {};
</script>

<div class="tooltip" style="left: {x + 15}px; top: {y - 10}px;">
  <div class="name">{nodeId}</div>
  {#each Object.entries(attrs) as [key, val]}
    {#if !["x", "y", "size", "color", "label"].includes(key) && val}
      <div class="attr">
        <span class="key">{key}:</span>
        <span>{val}</span>
      </div>
    {/if}
  {/each}
</div>

<style>
  .tooltip {
    position: absolute;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 8px 10px;
    font-size: 12px;
    max-width: 260px;
    pointer-events: none;
    z-index: 100;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }

  .name {
    font-weight: 600;
    margin-bottom: 4px;
    color: var(--accent);
  }

  .attr {
    color: var(--text-secondary);
    line-height: 1.4;
  }

  .key {
    color: var(--text-muted);
  }
</style>
