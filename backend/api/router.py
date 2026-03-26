from fastapi import APIRouter

from .routes import (
    bipartite,
    centrality,
    community,
    enrichment,
    homophily,
    layout,
    metrics,
    projects,
    sankey,
    tasks,
    visualization,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(projects.router)
api_router.include_router(centrality.router)
api_router.include_router(community.router)
api_router.include_router(homophily.router)
api_router.include_router(sankey.router)
api_router.include_router(metrics.router)
api_router.include_router(layout.router)
api_router.include_router(enrichment.router)
api_router.include_router(visualization.router)
api_router.include_router(bipartite.router)
api_router.include_router(tasks.router)
