from __future__ import annotations

from pydantic import BaseModel


class LayoutRequest(BaseModel):
    algorithm: str  # forceatlas2, yifan_hu, community
    iterations: int = 100
    scaling: float = 2.0
    gravity: float = 1.0
    strong_gravity: bool = False
    barnes_hut: bool = True
    # Community layout options
    community_key: str | None = None  # existing community partition to use
    resolution: float = 1.0  # Leiden resolution (if no community_key)
    spacing: float = 2.0  # gap between communities


class LayoutResponse(BaseModel):
    algorithm: str
    key: str
    node_count: int
