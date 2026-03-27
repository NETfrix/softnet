<script lang="ts">
  import { currentProject, projects, statusMessage, layoutReady } from "../../lib/projectStore";
  import { uploadGraph, listProjects, pollTask } from "../../lib/api";

  let name = "Untitled";
  let directed = false;
  let fileInput: HTMLInputElement;
  let nodeFileInput: HTMLInputElement;
  let uploading = false;

  async function handleUpload() {
    if (!fileInput?.files?.length) {
      $statusMessage = "Please select a file first";
      return;
    }

    uploading = true;
    $statusMessage = "Uploading...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("name", name || fileInput.files[0].name);
    formData.append("directed", String(directed));

    if (nodeFileInput?.files?.length) {
      formData.append("node_file", nodeFileInput.files[0]);
    }

    try {
      $layoutReady = false;
      const result = await uploadGraph(formData);
      $currentProject = result.project;
      $projects = await listProjects();
      $statusMessage = "Computing layout...";
      await pollTask(result.layout_task_id);
      $layoutReady = true;
      $statusMessage = "";
    } catch (e) {
      $statusMessage = `Upload failed: ${e}`;
    } finally {
      uploading = false;
    }
  }
</script>

<div class="panel">
  <div class="panel-title">Upload Graph</div>

  <div class="row">
    <label>
      Name
      <input bind:value={name} placeholder="Project name" />
    </label>
  </div>

  <div class="row">
    <label>
      Graph file
      <input type="file" accept=".csv,.tsv,.txt,.xlsx,.xls,.gexf,.graphml,.xml,.gephi" bind:this={fileInput} />
    </label>
  </div>

  <div class="row">
    <label>
      Node attributes (optional)
      <input type="file" accept=".csv,.tsv,.txt" bind:this={nodeFileInput} />
    </label>
  </div>

  <div class="row">
    <label class="checkbox-label">
      <input type="checkbox" bind:checked={directed} />
      Directed
    </label>
  </div>

  <button class="primary" on:click={handleUpload} disabled={uploading}>
    {uploading ? "Uploading..." : "Upload"}
  </button>

  <div class="hint">
    CSV/Excel: auto-detects edge list, adjacency matrix, or adjacency list.
    Also supports GEXF, GraphML, and Gephi project files.
  </div>
</div>

<style>
  input[type="file"] {
    font-size: 12px;
    margin-top: 2px;
  }

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

  button {
    width: 100%;
    margin-top: 4px;
  }

  .hint {
    margin-top: 8px;
    font-size: 10px;
    color: var(--text-muted);
    line-height: 1.4;
  }
</style>
