export interface ProjectMeta {
  id: string;
  name: string;
  node_count: number;
  edge_count: number;
  directed: boolean;
  created_at: number;
  centralities: string[];
  communities: string[];
  layouts: string[];
}

export interface TaskRecord {
  id: string;
  project_id: string;
  task_type: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  result?: Record<string, unknown>;
  error?: string;
}

export interface CentralityValues {
  algorithm: string;
  values: Record<string, number>;
  min: number;
  max: number;
  mean: number;
}

export interface CommunityInfo {
  algorithm: string;
  key: string;
  membership: number[];
  n_communities: number;
  modularity?: number;
}

export interface SankeyData {
  labels: string[];
  sources: number[];
  targets: number[];
  values: number[];
  nmi: number;
  ari: number;
}

export interface HomophilyResult {
  ei_index: number;
  internal_edges: number;
  external_edges: number;
  community_sizes: Record<string, number>;
  attribute_distributions?: Record<string, Record<string, number>>;
}

export interface GraphPayload {
  n: number;
  m: number;
  directed: boolean;
  node_ids: string[];
  x: Uint8Array;
  y: Uint8Array;
  sizes: Uint8Array;
  edge_sources: Uint8Array;
  edge_targets: Uint8Array;
  colors?: number[];
  node_attrs?: Record<string, string[]>;
}
