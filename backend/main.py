import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.router import api_router
from .config import settings

# Paths
_ROOT = Path(__file__).resolve().parent.parent
_FRONTEND_DIR = _ROOT / "frontend"
_DIST_DIR = _FRONTEND_DIR / "dist"

app = FastAPI(
    title="Softnet",
    description="Social Network Analysis Tool",
    version="0.8.0",
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve frontend — must come after API routes
if _DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(_DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the Svelte SPA. All non-API routes fall through to index.html."""
        file_path = _DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_DIST_DIR / "index.html"))


def _build_frontend() -> None:
    """Build the frontend if dist/ doesn't exist or is stale."""
    if _DIST_DIR.exists():
        return

    print("Building frontend...")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"

    # Install deps if needed
    if not (_FRONTEND_DIR / "node_modules").exists():
        subprocess.run([npm, "install"], cwd=str(_FRONTEND_DIR), check=True)

    subprocess.run([npm, "run", "build"], cwd=str(_FRONTEND_DIR), check=True)
    print("Frontend built.")


def main() -> None:
    """Single entry point: build frontend + start server."""
    import uvicorn
    import webbrowser

    _build_frontend()

    url = f"http://localhost:{settings.port}"
    print(f"\n  Softnet running at {url}\n")
    webbrowser.open(url)

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.dev_mode,
    )


if __name__ == "__main__":
    main()
