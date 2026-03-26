from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...core.tasks import task_manager
from ...analysis.density import (
    graph_density,
    connected_components,
    clustering_coefficient,
    reciprocity,
)
from ...analysis.ergm_mple import fit_ergm_mple
from ...schemas.metrics import (
    DensityResponse,
    ErgmRequest,
    ErgmResponse,
    ConnectedComponentsResponse,
    ClusteringCoefficientRequest,
    ClusteringCoefficientResponse,
    ReciprocityResponse,
)

router = APIRouter(prefix="/projects/{project_id}", tags=["metrics"])


@router.get("/density")
async def get_density(project_id: str):
    project = get_project(project_id)
    result = graph_density(project.graph)
    return DensityResponse(**result)


@router.get("/components")
async def get_components(project_id: str):
    project = get_project(project_id)
    result = connected_components(project.graph)
    return ConnectedComponentsResponse(**result)


@router.post("/clustering")
async def get_clustering(project_id: str, req: ClusteringCoefficientRequest):
    project = get_project(project_id)
    result = clustering_coefficient(project.graph, mode=req.mode)
    return ClusteringCoefficientResponse(**result)


@router.get("/reciprocity")
async def get_reciprocity(project_id: str):
    project = get_project(project_id)
    result = reciprocity(project.graph)
    return ReciprocityResponse(**result)


@router.post("/ergm", status_code=202)
async def run_ergm(project_id: str, req: ErgmRequest):
    project = get_project(project_id)

    def _compute():
        result = fit_ergm_mple(
            project.graph,
            terms=req.terms,
            seed=req.seed,
        )
        project.ergm_results["+".join(req.terms)] = result
        return result

    task_id = await task_manager.submit(project_id, "ergm", _compute)
    return {"task_id": task_id}
