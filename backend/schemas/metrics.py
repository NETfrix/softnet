from __future__ import annotations

from pydantic import BaseModel
from typing import Any


class DensityResponse(BaseModel):
    density: float
    directed: bool


class ErgmRequest(BaseModel):
    terms: list[str]  # e.g. ["edges", "mutual", "gwesp(0.5)"]
    seed: int = 42


class ErgmResponse(BaseModel):
    coefficients: dict[str, float]
    std_errors: dict[str, float]
    z_values: dict[str, float | None]
    aic: float
    bic: float
    log_likelihood: float
    formula: str
    method: str
    n_dyads: int
    n_edges: int


class ComponentInfo(BaseModel):
    rank: int
    component_id: int
    size: int


class ConnectedComponentsResponse(BaseModel):
    count: int
    largest_size: int
    largest_id: int | None
    directed: bool
    mode: str
    components: list[ComponentInfo]


class ClusteringCoefficientRequest(BaseModel):
    mode: str = "global"  # "global" or "local"


class ClusteringCoefficientResponse(BaseModel):
    clustering_coefficient: float
    mode: str


class ReciprocityResponse(BaseModel):
    reciprocity: float | None
    directed: bool
    error: str | None = None
