from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...core.tasks import task_manager
from ...analysis.community.louvain import louvain
from ...analysis.community.leiden import leiden
from ...analysis.community.infomap import infomap_detect
from ...bridges.wsl_graphtool import run_sbm
from ...analysis.community_graph import create_community_graph
from ...analysis.community.renumber import renumber_by_size
from ...schemas.community import CommunityRequest, CommunityResponse

router = APIRouter(prefix="/projects/{project_id}/community", tags=["community"])


@router.post("", status_code=202)
async def detect_communities(project_id: str, req: CommunityRequest):
    project = get_project(project_id)

    if req.algorithm == "sbm":
        # SBM runs async via WSL
        async def _run_sbm():
            result = await run_sbm(
                project.graph,
                model=req.model,
                deg_corr=req.deg_corr,
            )
            result["membership"] = renumber_by_size(result["membership"])
            project.communities[result["key"]] = result["membership"]
            return result

        # Submit as sync wrapper around async
        def _run_sbm_sync():
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(_run_sbm())
            finally:
                loop.close()

        task_id = await task_manager.submit(project_id, "community_sbm", _run_sbm_sync)
        return {"task_id": task_id, "algorithm": "sbm"}

    def _compute():
        if req.algorithm == "louvain":
            result = louvain(project.graph, resolution=req.resolution, quality=req.quality)
        elif req.algorithm == "leiden":
            result = leiden(
                project.graph,
                resolution=req.resolution,
                quality=req.quality,
                n_iterations=req.n_iterations,
                seed=req.seed,
            )
        elif req.algorithm == "infomap":
            result = infomap_detect(
                project.graph,
                directed=req.directed,
                num_trials=req.num_trials,
            )
        else:
            raise ValueError(f"Unknown algorithm: {req.algorithm}")

        result["membership"] = renumber_by_size(result["membership"])
        project.communities[result["key"]] = result["membership"]
        return result

    task_id = await task_manager.submit(project_id, f"community_{req.algorithm}", _compute)
    return {"task_id": task_id, "algorithm": req.algorithm}


@router.get("")
async def list_communities(project_id: str):
    project = get_project(project_id)
    info = {}
    for key, membership in project.communities.items():
        info[key] = {"n_communities": len(set(membership))}
    return {"communities": info}


@router.get("/{key}")
async def get_community(project_id: str, key: str):
    project = get_project(project_id)
    membership = project.communities.get(key)
    if membership is None:
        raise HTTPException(404, f"Community '{key}' not found")

    return CommunityResponse(
        algorithm=key.split("_")[0],
        key=key,
        membership=membership,
        n_communities=len(set(membership)),
    )


@router.post("/{key}/graph")
async def get_community_graph(project_id: str, key: str):
    """Create an aggregated community graph from a community partition."""
    project = get_project(project_id)
    membership = project.communities.get(key)
    if membership is None:
        raise HTTPException(404, f"Community '{key}' not found")

    cg = create_community_graph(project.graph, membership)

    nodes = []
    for v in cg.vs:
        nodes.append({
            "id": v["community_id"],
            "name": v["name"],
            "size": v["size"],
        })

    edges = []
    for e in cg.es:
        edges.append({
            "source": cg.vs[e.source]["community_id"],
            "target": cg.vs[e.target]["community_id"],
            "weight": e["weight"],
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "n_communities": cg.vcount(),
        "n_edges": cg.ecount(),
    }
