from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...core.tasks import task_manager
from ...analysis.centrality import (
    betweenness_centrality,
    closeness_centrality,
    degree_centrality,
    pagerank,
)
from ...schemas.centrality import CentralityRequest, CentralityResponse

router = APIRouter(prefix="/projects/{project_id}/centrality", tags=["centrality"])

_ALGORITHMS = {
    "degree": degree_centrality,
    "betweenness": betweenness_centrality,
    "closeness": closeness_centrality,
    "pagerank": pagerank,
}


@router.post("", status_code=202)
async def compute_centrality(project_id: str, req: CentralityRequest):
    project = get_project(project_id)

    if req.algorithm not in _ALGORITHMS:
        raise HTTPException(400, f"Unknown algorithm: {req.algorithm}. Options: {list(_ALGORITHMS)}")

    def _compute():
        fn = _ALGORITHMS[req.algorithm]
        if req.algorithm == "degree":
            values = fn(project.graph, mode=req.mode, normalized=req.normalized)
        elif req.algorithm == "betweenness":
            values = fn(project.graph, directed=req.directed, cutoff=req.cutoff, normalized=req.normalized)
        elif req.algorithm == "closeness":
            values = fn(project.graph, mode=req.mode, normalized=req.normalized)
        elif req.algorithm == "pagerank":
            values = fn(project.graph, damping=req.damping, directed=req.directed)
        else:
            values = fn(project.graph)

        project.centralities[req.algorithm] = values
        return values

    task_id = await task_manager.submit(project_id, f"centrality_{req.algorithm}", _compute)
    return {"task_id": task_id, "algorithm": req.algorithm}


@router.get("")
async def list_centralities(project_id: str):
    project = get_project(project_id)
    return {"centralities": list(project.centralities.keys())}


@router.get("/{algorithm}")
async def get_centrality(project_id: str, algorithm: str):
    project = get_project(project_id)
    values = project.centralities.get(algorithm)
    if values is None:
        raise HTTPException(404, f"Centrality '{algorithm}' not computed yet")

    vals = list(values.values())
    return CentralityResponse(
        algorithm=algorithm,
        values=values,
        min=float(np.min(vals)),
        max=float(np.max(vals)),
        mean=float(np.mean(vals)),
    )
