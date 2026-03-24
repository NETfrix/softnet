<script lang="ts">
  import { labelsVisible } from "../../lib/graphStore";
</script>

<button
  class:active={$labelsVisible}
  on:click={() => ($labelsVisible = !$labelsVisible)}
  title="Toggle labels"
>
  Lbl
</button>

<style>
  button {
    width: 36px;
    height: 28px;
    font-size: 11px;
    padding: 0;
  }

  button.active {
    background: var(--accent);
    border-color: var(--accent);
  }
</style>
