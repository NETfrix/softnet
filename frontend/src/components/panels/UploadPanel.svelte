<script lang="ts">
  import { currentProject, projects, statusMessage } from "../../lib/projectStore";
  import { uploadGraph, listProjects, pollTask } from "../../lib/api";

  let name = "Untitled";
  let directed = false;
  let sourceCol = "source";
  let targetCol = "target";
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
    formData.append("name", name);
    formData.append("directed", String(directed));
    formData.append("source_col", sourceCol);
    formData.append("target_col", targetCol);

    if (nodeFileInput?.files?.length) {
      formData.append("node_file", nodeFileInput.files[0]);
    }

    try {
      const result = await uploadGraph(formData);
      $currentProject = result.project;
      $projects = await listProjects();
      $statusMessage = "Computing layout...";
      await pollTask(result.layout_task_id);
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
      Edge file (CSV/GEXF/GraphML/Gephi)
      <input type="file" accept=".csv,.tsv,.gexf,.graphml,.xml,.gephi" bind:this={fileInput} />
    </label>
  </div>

  <div class="row">
    <label>
      Node attributes (optional CSV)
      <input type="file" accept=".csv" bind:this={nodeFileInput} />
    </label>
  </div>

  <div class="row">
    <label>
      Source col
      <input bind:value={sourceCol} />
    </label>
    <label>
      Target col
      <input bind:value={targetCol} />
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
</style>
