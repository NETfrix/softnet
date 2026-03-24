from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...analysis.community.comparison import build_sankey_data
from ...schemas.community import SankeyRequest, SankeyResponse

router = APIRouter(prefix="/projects/{project_id}/sankey", tags=["sankey"])


@router.post("")
async def compute_sankey(project_id: str, req: SankeyRequest):
    project = get_project(project_id)

    if len(req.community_keys) != 2:
        raise HTTPException(400, "Exactly 2 community keys required")

    memberships = {}
    for key in req.community_keys:
        mem = project.communities.get(key)
        if mem is None:
            raise HTTPException(404, f"Community '{key}' not found")
        memberships[key] = mem

    result = build_sankey_data(memberships, project.node_ids)

    return {
        **result,
        "nmi": result["nmi"],
        "ari": result["ari"],
    }
