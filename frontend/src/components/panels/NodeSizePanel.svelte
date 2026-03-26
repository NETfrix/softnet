<script lang="ts">
  import { currentProject } from "../../lib/projectStore";
  import { currentSizeAttr, currentColorAttr, edgeScale, labelScale, edgeBrightness, labelsVisible } from "../../lib/graphStore";

  let selectedSize: string | null = $currentSizeAttr;
  let selectedColor: string | null = $currentColorAttr;
  let selectedEdgeScale: number = $edgeScale;
  let selectedLabelScale: number = $labelScale;
  let selectedEdgeBrightness: number = $edgeBrightness;
  let showLabels: boolean = $labelsVisible;

  $: centralities = $currentProject?.centralities || [];
  $: communities = $currentProject?.communities || [];

  function apply() {
    $currentSizeAttr = selectedSize;
    $currentColorAttr = selectedColor;
    $edgeScale = selectedEdgeScale;
    $labelScale = selectedLabelScale;
    $edgeBrightness = selectedEdgeBrightness;
    $labelsVisible = showLabels;
  }
</script>

<div class="panel">
  <div class="panel-title">Appearance</div>

  <div class="row">
    <label>
      Node size
      <select bind:value={selectedSize}>
        <option value={null}>Uniform</option>
        {#each centralities as c}
          <option value={c}>{c}</option>
        {/each}
      </select>
    </label>
  </div>

  <div class="row">
    <label>
      Node color
      <select bind:value={selectedColor}>
        <option value={null}>Default</option>
        {#each communities as c}
          <option value={c}>{c}</option>
        {/each}
        {#each centralities as c}
          <option value={c}>{c}</option>
        {/each}
      </select>
    </label>
  </div>

  <div class="row">
    <label class="checkbox-label">
      <input type="checkbox" bind:checked={showLabels} />
      Show node labels
    </label>
  </div>

  <div class="row">
    <label>
      Label size
      <input type="range" bind:value={selectedLabelScale} min="0.3" max="3" step="0.1" />
      <span class="range-val">{selectedLabelScale.toFixed(1)}x</span>
    </label>
  </div>

  <div class="row">
    <label>
      Edge thickness
      <input type="range" bind:value={selectedEdgeScale} min="0.1" max="5" step="0.1" />
      <span class="range-val">{selectedEdgeScale.toFixed(1)}x</span>
    </label>
  </div>

  <div class="row">
    <label>
      Edge brightness
      <input type="range" bind:value={selectedEdgeBrightness} min="0.05" max="1" step="0.05" />
      <span class="range-val">{Math.round(selectedEdgeBrightness * 100)}%</span>
    </label>
  </div>

  <button on:click={apply}>Apply</button>
</div>

<style>
  button { width: 100%; }
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-direction: row;
    font-size: 13px;
    color: var(--text-primary);
  }
  .checkbox-label input {
    margin: 0;
  }
  input[type="range"] {
    width: 100%;
    margin-top: 2px;
  }
  .range-val {
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
  }
</style>
