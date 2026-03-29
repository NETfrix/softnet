from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
import uuid
from pathlib import PureWindowsPath

import igraph as ig

IS_WINDOWS = sys.platform == "win32"


def _windows_to_wsl_path(win_path: str) -> str:
    """Convert C:\\Users\\... to /mnt/c/Users/..."""
    p = PureWindowsPath(win_path)
    drive = p.drive[0].lower()
    rest = str(p).split(":", 1)[1].replace("\\", "/")
    return f"/mnt/{drive}{rest}"


async def run_sbm(
    g: ig.Graph,
    model: str = "nested",
    deg_corr: bool = True,
    timeout: int = 600,
) -> dict:
    """
    Run Peixoto's SBM via graph-tool.

    On Windows: delegates to WSL subprocess.
    On Linux:   runs the worker script directly (graph-tool installed natively).
    """
    uid = uuid.uuid4().hex
    tmp_dir = tempfile.gettempdir()
    input_path = os.path.join(tmp_dir, f"softnet_sbm_{uid}.csv")
    output_path = os.path.join(tmp_dir, f"softnet_sbm_{uid}_result.json")

    # Write edge list
    with open(input_path, "w") as f:
        f.write("source,target\n")
        for edge in g.es:
            f.write(f"{edge.source},{edge.target}\n")

    # Write directedness flag
    meta_path = os.path.join(tmp_dir, f"softnet_sbm_{uid}_meta.json")
    with open(meta_path, "w") as f:
        json.dump({"directed": g.is_directed(), "n_vertices": g.vcount()}, f)

    # Find the worker script
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    worker_path = os.path.join(script_dir, "wsl", "sbm_worker.py")

    if IS_WINDOWS:
        wsl_input = _windows_to_wsl_path(input_path)
        wsl_output = _windows_to_wsl_path(output_path)
        wsl_meta = _windows_to_wsl_path(meta_path)
        wsl_script = _windows_to_wsl_path(worker_path)

        cmd = [
            "wsl.exe", "python3", wsl_script,
            "--input", wsl_input,
            "--output", wsl_output,
            "--meta", wsl_meta,
            "--model", model,
        ]
    else:
        # Linux / macOS — run graph-tool directly
        cmd = [
            sys.executable, worker_path,
            "--input", input_path,
            "--output", output_path,
            "--meta", meta_path,
            "--model", model,
        ]

    if deg_corr:
        cmd.append("--deg-corr")

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        _cleanup(input_path, output_path, meta_path)
        raise TimeoutError(f"SBM computation timed out after {timeout}s")

    if proc.returncode != 0:
        _cleanup(input_path, output_path, meta_path)
        raise RuntimeError(f"graph-tool SBM failed: {stderr.decode()}")

    with open(output_path) as f:
        result = json.load(f)

    _cleanup(input_path, output_path, meta_path)

    membership = result["membership"]
    n_communities = len(set(membership))
    key = f"sbm_{model}_{'dc' if deg_corr else 'ndc'}"

    return {
        "algorithm": "sbm",
        "key": key,
        "membership": membership,
        "n_communities": n_communities,
        "description_length": result.get("description_length"),
        "levels": result.get("levels"),
    }


def _cleanup(*paths: str) -> None:
    for p in paths:
        try:
            os.unlink(p)
        except OSError:
            pass
