import type {
  ProjectMeta,
  TaskRecord,
  CentralityValues,
  CommunityInfo,
  SankeyData,
  HomophilyResult,
} from "./types";

const BASE = "/api";

async function json_fetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status}: ${body}`);
  }
  return res.json();
}

// Projects
export async function uploadGraph(formData: FormData): Promise<{ project: ProjectMeta; layout_task_id: string }> {
  const res = await fetch(BASE + "/projects/upload", { method: "POST", body: formData });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function importFromApi(params: Record<string, unknown>) {
  return json_fetch("/projects/from-api", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function listProjects(): Promise<ProjectMeta[]> {
  return json_fetch("/projects");
}

export async function getProject(id: string): Promise<ProjectMeta> {
  return json_fetch(`/projects/${id}`);
}

export async function deleteProject(id: string) {
  return json_fetch(`/projects/${id}`, { method: "DELETE" });
}

export async function getGraphData(
  id: string,
  layout = "default",
  sizeAttr?: string,
  colorAttr?: string
): Promise<ArrayBuffer> {
  const params = new URLSearchParams({ layout });
  if (sizeAttr) params.set("size_attr", sizeAttr);
  if (colorAttr) params.set("color_attr", colorAttr);
  const res = await fetch(`${BASE}/projects/${id}/graph?${params}`);
  if (!res.ok) throw new Error(await res.text());
  return res.arrayBuffer();
}

// Centrality
export async function computeCentrality(projectId: string, params: Record<string, unknown>) {
  return json_fetch(`/projects/${projectId}/centrality`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function getCentrality(projectId: string, algorithm: string): Promise<CentralityValues> {
  return json_fetch(`/projects/${projectId}/centrality/${algorithm}`);
}

export async function listCentralities(projectId: string): Promise<{ centralities: string[] }> {
  return json_fetch(`/projects/${projectId}/centrality`);
}

// Community
export async function detectCommunity(projectId: string, params: Record<string, unknown>) {
  return json_fetch(`/projects/${projectId}/community`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function getCommunity(projectId: string, key: string): Promise<CommunityInfo> {
  return json_fetch(`/projects/${projectId}/community/${key}`);
}

export async function listCommunities(projectId: string) {
  return json_fetch(`/projects/${projectId}/community`);
}

// Homophily
export async function computeHomophily(projectId: string, params: Record<string, unknown>): Promise<HomophilyResult> {
  return json_fetch(`/projects/${projectId}/homophily`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

// Sankey
export async function computeSankey(projectId: string, keys: string[]): Promise<SankeyData> {
  return json_fetch(`/projects/${projectId}/sankey`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ community_keys: keys }),
  });
}

// Metrics
export async function getDensity(projectId: string) {
  return json_fetch(`/projects/${projectId}/density`);
}

export async function getConnectedComponents(projectId: string) {
  return json_fetch(`/projects/${projectId}/components`);
}

export async function getClusteringCoefficient(projectId: string, mode: string = "global") {
  return json_fetch(`/projects/${projectId}/clustering`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
}

export async function getReciprocity(projectId: string) {
  return json_fetch(`/projects/${projectId}/reciprocity`);
}

export async function runErgm(projectId: string, params: Record<string, unknown>) {
  return json_fetch(`/projects/${projectId}/ergm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

// Bipartite
export async function checkBipartite(projectId: string) {
  return json_fetch(`/projects/${projectId}/bipartite`);
}

export async function projectBipartite(projectId: string, which: number = 0) {
  return json_fetch(`/projects/${projectId}/bipartite/project`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ which }),
  });
}

// Community Graph
export async function getCommunityGraph(projectId: string, communityKey: string) {
  return json_fetch(`/projects/${projectId}/community/${communityKey}/graph`, {
    method: "POST",
  });
}

// Layout
export async function computeLayout(projectId: string, params: Record<string, unknown>) {
  return json_fetch(`/projects/${projectId}/layout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

// Enrichment
export async function enrichNodes(projectId: string, nodeIds: string[], sources: string[] = ["wikipedia"]) {
  return json_fetch(`/projects/${projectId}/enrich`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ node_ids: nodeIds, sources }),
  });
}

// Tasks
export async function getTask(taskId: string): Promise<TaskRecord> {
  return json_fetch(`/tasks/${taskId}`);
}

export async function pollTask(taskId: string, intervalMs = 1000, maxWaitMs = 5 * 60 * 1000): Promise<TaskRecord> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const check = async () => {
      if (Date.now() - startTime > maxWaitMs) {
        reject(new Error("Layout computation timed out"));
        return;
      }
      try {
        const task = await getTask(taskId);
        if (task.status === "completed") {
          resolve(task);
        } else if (task.status === "failed") {
          reject(new Error(task.error || "Task failed"));
        } else {
          setTimeout(check, intervalMs);
        }
      } catch (e) {
        reject(e);
      }
    };
    check();
  });
}
