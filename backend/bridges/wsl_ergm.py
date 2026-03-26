from __future__ import annotations

import asyncio
import json
import os
import tempfile
import uuid
from pathlib import PureWindowsPath

import igraph as ig


def _windows_to_wsl_path(win_path: str) -> str:
    """Convert C:\\Users\\... to /mnt/c/Users/..."""
    p = PureWindowsPath(win_path)
    drive = p.drive[0].lower()
    rest = str(p).split(":", 1)[1].replace("\\", "/")
    return f"/mnt/{drive}{rest}"


async def run_ergm_mcmc(
    g: ig.Graph,
    terms: list[str],
    init_coefs: list[float] | None = None,
    burnin: int = 10000,
    samplesize: int = 10000,
    interval: int = 1024,
    seed: int = 42,
    timeout: int = 600,
) -> dict:
    """
    Run ERGM via R's ergm package in WSL using MCMC-MLE.

    Args:
        g: The network.
        terms: ERGM term strings.
        init_coefs: Optional MPLE coefficients to seed MCMC.
        burnin: MCMC burn-in iterations.
        samplesize: MCMC sample size.
        interval: MCMC sampling interval.
        seed: Random seed.
        timeout: Max seconds to wait.
    """
    uid = uuid.uuid4().hex
    tmp_dir = tempfile.gettempdir()
    input_path = os.path.join(tmp_dir, f"softnet_ergm_{uid}.csv")
    output_path = os.path.join(tmp_dir, f"softnet_ergm_{uid}_result.json")
    meta_path = os.path.join(tmp_dir, f"softnet_ergm_{uid}_meta.json")

    # Write edge list
    with open(input_path, "w") as f:
        f.write("source,target\n")
        for edge in g.es:
            f.write(f"{edge.source},{edge.target}\n")

    # Write meta
    with open(meta_path, "w") as f:
        json.dump({"directed": g.is_directed(), "n_vertices": g.vcount()}, f)

    wsl_input = _windows_to_wsl_path(input_path)
    wsl_output = _windows_to_wsl_path(output_path)
    wsl_meta = _windows_to_wsl_path(meta_path)

    # Find the worker script
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    worker_path = os.path.join(script_dir, "wsl", "ergm_worker.py")
    wsl_script = _windows_to_wsl_path(worker_path)

    cmd = [
        "wsl.exe", "python3", wsl_script,
        "--input", wsl_input,
        "--output", wsl_output,
        "--meta", wsl_meta,
        "--terms", ",".join(terms),
        "--burnin", str(burnin),
        "--samplesize", str(samplesize),
        "--interval", str(interval),
        "--seed", str(seed),
    ]

    if init_coefs is not None:
        cmd.extend(["--init-coefs", json.dumps(init_coefs)])

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
        raise TimeoutError(f"ERGM MCMC timed out after {timeout}s")

    if proc.returncode != 0:
        _cleanup(input_path, output_path, meta_path)
        raise RuntimeError(f"ERGM MCMC failed: {stderr.decode()}")

    with open(output_path) as f:
        result = json.load(f)

    _cleanup(input_path, output_path, meta_path)
    return result


def _cleanup(*paths: str) -> None:
    for p in paths:
        try:
            os.unlink(p)
        except OSError:
            pass
