from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import igraph as ig


@dataclass
class ProjectState:
    id: str
    name: str
    graph: ig.Graph
    directed: bool
    created_at: float = field(default_factory=time.time)

    # Computed results keyed by algorithm name
    centralities: dict[str, dict[str, float]] = field(default_factory=dict)
    communities: dict[str, list[int]] = field(default_factory=dict)
    layouts: dict[str, list[tuple[float, float]]] = field(default_factory=dict)
    homophily_results: dict[str, Any] = field(default_factory=dict)
    ergm_results: dict[str, Any] = field(default_factory=dict)
    enrichment_cache: dict[str, dict] = field(default_factory=dict)

    @property
    def node_count(self) -> int:
        return self.graph.vcount()

    @property
    def edge_count(self) -> int:
        return self.graph.ecount()

    @property
    def node_ids(self) -> list[str]:
        if "name" in self.graph.vs.attributes():
            return [str(v["name"]) for v in self.graph.vs]
        return [str(v.index) for v in self.graph.vs]

    def metadata(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "directed": self.directed,
            "created_at": self.created_at,
            "centralities": list(self.centralities.keys()),
            "communities": list(self.communities.keys()),
            "layouts": list(self.layouts.keys()),
        }

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex[:12]
