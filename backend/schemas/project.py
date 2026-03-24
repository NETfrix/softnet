from __future__ import annotations

from pydantic import BaseModel


class ProjectMeta(BaseModel):
    id: str
    name: str
    node_count: int
    edge_count: int
    directed: bool
    created_at: float
    centralities: list[str]
    communities: list[str]
    layouts: list[str]


class UploadParams(BaseModel):
    name: str = "Untitled"
    directed: bool = False
    delimiter: str = ","
    source_col: str = "source"
    target_col: str = "target"
    weight_col: str | None = None


class ApiConnectorParams(BaseModel):
    name: str = "API Import"
    endpoint: str
    headers: dict[str, str] = {}
    node_path: str = "nodes"
    edge_path: str = "edges"
    source_field: str = "source"
    target_field: str = "target"
    directed: bool = False
