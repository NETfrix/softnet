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
import asyncio

from ...analysis.ergm_mple import fit_ergm_mple
from ...bridges.wsl_ergm import run_ergm_mcmc
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

    if req.method == "mple":
        def _compute():
            result = fit_ergm_mple(
                project.graph,
                terms=req.terms,
                seed=req.seed,
            )
            project.ergm_results["+".join(req.terms)] = result
            return result

        task_id = await task_manager.submit(project_id, "ergm", _compute)

    elif req.method == "mcmc":
        def _compute_mcmc():
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(run_ergm_mcmc(
                    project.graph,
                    terms=req.terms,
                    burnin=req.burnin,
                    samplesize=req.samplesize,
                    interval=req.interval,
                    seed=req.seed,
                ))
            finally:
                loop.close()
            project.ergm_results["+".join(req.terms)] = result
            return result

        task_id = await task_manager.submit(project_id, "ergm_mcmc", _compute_mcmc)

    elif req.method == "mple_mcmc":
        def _compute_seeded():
            # Step 1: MPLE for initial estimates
            mple_result = fit_ergm_mple(
                project.graph,
                terms=req.terms,
                seed=req.seed,
            )
            init_coefs = [mple_result["coefficients"][t] for t in req.terms]

            # Step 2: MCMC-MLE seeded with MPLE coefficients (shorter burn-in)
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(run_ergm_mcmc(
                    project.graph,
                    terms=req.terms,
                    init_coefs=init_coefs,
                    burnin=max(req.burnin // 2, 5000),
                    samplesize=req.samplesize,
                    interval=req.interval,
                    seed=req.seed,
                ))
            finally:
                loop.close()

            # Include MPLE estimates for comparison
            result["mple_coefficients"] = mple_result["coefficients"]
            project.ergm_results["+".join(req.terms)] = result
            return result

        task_id = await task_manager.submit(project_id, "ergm_seeded", _compute_seeded)

    else:
        raise HTTPException(400, f"Unknown ERGM method: {req.method}. Use 'mple', 'mcmc', or 'mple_mcmc'.")

    return {"task_id": task_id}
