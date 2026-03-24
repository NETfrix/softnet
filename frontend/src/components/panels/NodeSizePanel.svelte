<script lang="ts">
  import { currentProject } from "../../lib/projectStore";
  import { currentSizeAttr } from "../../lib/graphStore";

  $: centralities = $currentProject?.centralities || [];
</script>

<div class="panel">
  <div class="panel-title">Node Size</div>

  <div class="row">
    <label>
      Size by
      <select bind:value={$currentSizeAttr}>
        <option value={null}>Uniform</option>
        {#each centralities as c}
          <option value={c}>{c}</option>
        {/each}
      </select>
    </label>
  </div>
</div>
