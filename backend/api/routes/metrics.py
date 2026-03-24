from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...core.tasks import task_manager
from ...analysis.density import graph_density
from ...bridges.rpy2_ergm import fit_ergm
from ...schemas.metrics import DensityResponse, ErgmRequest, ErgmResponse

router = APIRouter(prefix="/projects/{project_id}", tags=["metrics"])


@router.get("/density")
async def get_density(project_id: str):
    project = get_project(project_id)
    result = graph_density(project.graph)
    return DensityResponse(**result)


@router.post("/ergm", status_code=202)
async def run_ergm(project_id: str, req: ErgmRequest):
    project = get_project(project_id)

    n = project.node_count
    if n > 5000:
        raise HTTPException(
            400,
            f"ERGM is not feasible for graphs with {n} nodes. "
            "Consider sampling your network to < 5000 nodes.",
        )

    def _compute():
        result = fit_ergm(
            project.graph,
            terms=req.terms,
            burnin=req.burnin,
            samplesize=req.samplesize,
            interval=req.interval,
            seed=req.seed,
        )
        project.ergm_results["+".join(req.terms)] = result
        return result

    task_id = await task_manager.submit(project_id, "ergm", _compute)
    return {"task_id": task_id}
