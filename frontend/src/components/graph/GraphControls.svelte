<script lang="ts">
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher();
</script>

<div class="controls">
  <button on:click={() => dispatch("zoomIn")} title="Zoom in">+</button>
  <button on:click={() => dispatch("zoomOut")} title="Zoom out">-</button>
  <button on:click={() => dispatch("fit")} title="Fit to screen">Fit</button>
</div>

<style>
  .controls {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  button {
    width: 36px;
    height: 28px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
  }
</style>
