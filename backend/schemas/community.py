from __future__ import annotations

from pydantic import BaseModel


class CommunityRequest(BaseModel):
    algorithm: str  # louvain, leiden, sbm, infomap
    resolution: float = 1.0
    quality: str = "modularity"  # modularity, CPM
    n_iterations: int = 2  # for leiden
    seed: int | None = None
    # SBM params
    model: str = "nested"  # flat, nested
    deg_corr: bool = True
    # Infomap params
    num_trials: int = 10
    directed: bool = True


class CommunityResponse(BaseModel):
    algorithm: str
    key: str  # storage key like "leiden_1.0_modularity"
    membership: list[int]
    n_communities: int
    modularity: float | None = None
    description_length: float | None = None


class SankeyRequest(BaseModel):
    community_keys: list[str]  # exactly 2 keys to compare


class SankeyResponse(BaseModel):
    labels: list[str]
    sources: list[int]
    targets: list[int]
    values: list[int]


class HomophilyRequest(BaseModel):
    community_key: str
    attribute: str | None = None  # node attribute to test homophily on


class HomophilyResponse(BaseModel):
    ei_index: float
    internal_edges: int
    external_edges: int
    community_sizes: dict[str, int]
    attribute_distributions: dict[str, dict[str, int]] | None = None
    newman_assortativity: float | None = None
    newman_community_scores: dict[str, dict] | None = None
