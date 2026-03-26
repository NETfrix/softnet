from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...api.deps import get_project
from ...analysis.homophily import attribute_homophily, ei_index, newman_homophily
from ...schemas.community import HomophilyRequest, HomophilyResponse

router = APIRouter(prefix="/projects/{project_id}/homophily", tags=["homophily"])


@router.post("")
async def compute_homophily(project_id: str, req: HomophilyRequest):
    project = get_project(project_id)

    membership = project.communities.get(req.community_key)
    if membership is None:
        raise HTTPException(404, f"Community '{req.community_key}' not found")

    result = ei_index(project.graph, membership)

    attr_dist = None
    if req.attribute:
        try:
            attr_result = attribute_homophily(project.graph, membership, req.attribute)
            attr_dist = attr_result["distributions"]
        except ValueError as e:
            raise HTTPException(400, str(e))

    newman = newman_homophily(project.graph, membership)

    return HomophilyResponse(
        ei_index=result["ei_index"],
        internal_edges=result["internal_edges"],
        external_edges=result["external_edges"],
        community_sizes=result["community_sizes"],
        attribute_distributions=attr_dist,
        newman_assortativity=newman["assortativity"],
        newman_community_scores=newman["community_scores"],
    )
