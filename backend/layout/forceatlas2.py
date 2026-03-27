"""
MultiGravity ForceAtlas2 layout — pure Python with NumPy.

Based on Jacomy et al. (2014) "ForceAtlas2, a Continuous Graph Layout Algorithm
for Handy Network Visualization Designed for the Gephi Software".

MultiGravity variant: gravity force scales with node degree, preventing
small components from drifting to the periphery.
"""
from __future__ import annotations

import igraph as ig
import numpy as np


def compute_forceatlas2(
    g: ig.Graph,
    iterations: int = 100,
    scaling: float = 2.0,
    gravity: float = 1.0,
    strong_gravity: bool = False,
    barnes_hut: bool = True,
) -> list[tuple[float, float]]:
    """Compute MultiGravity ForceAtlas2 layout."""
    n = g.vcount()
    if n == 0:
        return []
    if n == 1:
        return [(0.0, 0.0)]

    edges = np.array(g.get_edgelist(), dtype=np.int32)
    weights = np.ones(len(edges), dtype=np.float64)
    if "weight" in g.es.attributes():
        w = g.es["weight"]
        weights = np.array([abs(x) if x is not None else 1.0 for x in w], dtype=np.float64)

    degree = np.array(g.degree(), dtype=np.float64)
    mass = degree + 1.0

    rng = np.random.default_rng(42)
    pos = rng.uniform(-100, 100, size=(n, 2))

    speed = np.ones(n, dtype=np.float64)
    swing_prev = np.zeros(n, dtype=np.float64)

    kr = scaling
    kg = gravity

    for _it in range(iterations):
        forces = np.zeros((n, 2), dtype=np.float64)

        # --- Repulsion (all pairs or Barnes-Hut approximation) ---
        if barnes_hut and n > 500:
            forces += _barnes_hut_repulsion(pos, mass, kr)
        else:
            forces += _pairwise_repulsion(pos, mass, kr)

        # --- Attraction (along edges) ---
        if len(edges) > 0:
            src = edges[:, 0]
            tgt = edges[:, 1]
            diff = pos[tgt] - pos[src]
            attr = (diff * weights[:, None])
            np.add.at(forces, src, attr)
            np.add.at(forces, tgt, -attr)

        # --- MultiGravity (gravity proportional to node mass/degree) ---
        center = np.mean(pos, axis=0)
        diff_to_center = center - pos
        dist_to_center = np.linalg.norm(diff_to_center, axis=1, keepdims=True)
        dist_to_center = np.maximum(dist_to_center, 1e-6)

        if strong_gravity:
            # Strong gravity: force independent of distance
            forces += kg * mass[:, None] * (diff_to_center / dist_to_center)
        else:
            # MultiGravity: force = kg * mass (proportional to degree)
            forces += kg * mass[:, None] * (diff_to_center / dist_to_center)

        # --- Adaptive speed (swing/traction) ---
        force_mag = np.linalg.norm(forces, axis=1)
        swing = np.abs(force_mag - swing_prev)
        swing_prev = force_mag.copy()

        global_swing = np.sum(mass * swing)
        global_traction = np.sum(mass * 0.5 * (force_mag + swing_prev))

        global_speed = 1.0
        if global_swing > 0:
            global_speed = min(1.0, global_traction / (global_swing + 1e-6))

        max_rise = 0.5
        node_swing = swing + 1e-6
        node_speed = global_speed / (1.0 + global_speed * node_swing)
        node_speed = np.minimum(node_speed, speed * (1.0 + max_rise))
        speed = node_speed

        displacement = forces * node_speed[:, None]

        # Limit max displacement
        disp_mag = np.linalg.norm(displacement, axis=1, keepdims=True)
        max_disp = 10.0
        scale = np.minimum(1.0, max_disp / (disp_mag + 1e-6))
        displacement *= scale

        pos += displacement

    return [(float(pos[i, 0]), float(pos[i, 1])) for i in range(n)]


def _pairwise_repulsion(
    pos: np.ndarray, mass: np.ndarray, kr: float
) -> np.ndarray:
    """O(n^2) repulsion: F = kr * mass_i * mass_j / distance."""
    n = len(pos)
    forces = np.zeros((n, 2), dtype=np.float64)

    for i in range(n):
        diff = pos[i] - pos[i + 1:]
        dist = np.linalg.norm(diff, axis=1, keepdims=True)
        dist = np.maximum(dist, 0.01)

        f = kr * mass[i] * mass[i + 1:, None] * diff / (dist * dist)

        forces[i] += np.sum(f, axis=0)
        forces[i + 1:] -= f

    return forces


def _barnes_hut_repulsion(
    pos: np.ndarray, mass: np.ndarray, kr: float, theta: float = 1.2
) -> np.ndarray:
    """Barnes-Hut approximation for repulsion (quad-tree)."""
    n = len(pos)
    forces = np.zeros((n, 2), dtype=np.float64)

    tree = _build_quadtree(pos, mass)

    for i in range(n):
        fx, fy = _bh_force(tree, pos[i, 0], pos[i, 1], mass[i], kr, theta)
        forces[i, 0] = fx
        forces[i, 1] = fy

    return forces


def _build_quadtree(pos: np.ndarray, mass: np.ndarray):
    """Build a simple quad-tree for Barnes-Hut."""
    x_min, y_min = pos.min(axis=0) - 1
    x_max, y_max = pos.max(axis=0) + 1
    size = max(x_max - x_min, y_max - y_min)

    root = {
        "cx": 0.0, "cy": 0.0, "mass": 0.0,
        "x": x_min, "y": y_min, "size": size,
        "children": None, "leaf": True, "idx": -1,
    }

    for i in range(len(pos)):
        _qt_insert(root, pos[i, 0], pos[i, 1], mass[i], i)

    return root


def _qt_insert(node, px, py, m, idx):
    """Insert a point into the quad-tree."""
    if node["mass"] == 0 and node["leaf"]:
        node["cx"] = px
        node["cy"] = py
        node["mass"] = m
        node["idx"] = idx
        return

    if node["leaf"]:
        node["children"] = [None, None, None, None]
        node["leaf"] = False
        # Re-insert existing point
        old_cx, old_cy, old_m, old_idx = node["cx"], node["cy"], node["mass"], node["idx"]
        node["cx"] = 0.0
        node["cy"] = 0.0
        node["mass"] = 0.0
        node["idx"] = -1
        _qt_insert_into_child(node, old_cx, old_cy, old_m, old_idx)

    _qt_insert_into_child(node, px, py, m, idx)

    total_mass = node["mass"] + m
    node["cx"] = (node["cx"] * node["mass"] + px * m) / total_mass
    node["cy"] = (node["cy"] * node["mass"] + py * m) / total_mass
    node["mass"] = total_mass


def _qt_insert_into_child(node, px, py, m, idx):
    half = node["size"] / 2
    mx = node["x"] + half
    my = node["y"] + half

    if px < mx:
        qi = 0 if py < my else 2
    else:
        qi = 1 if py < my else 3

    if node["children"][qi] is None:
        cx = node["x"] if qi in (0, 2) else mx
        cy = node["y"] if qi in (0, 1) else my
        node["children"][qi] = {
            "cx": 0.0, "cy": 0.0, "mass": 0.0,
            "x": cx, "y": cy, "size": half,
            "children": None, "leaf": True, "idx": -1,
        }

    _qt_insert(node["children"][qi], px, py, m, idx)


def _bh_force(node, px, py, pm, kr, theta):
    """Compute repulsive force on point (px,py) from quad-tree node."""
    if node["mass"] == 0:
        return 0.0, 0.0

    dx = px - node["cx"]
    dy = py - node["cy"]
    dist_sq = dx * dx + dy * dy
    dist = max(dist_sq ** 0.5, 0.01)

    if node["leaf"]:
        if dist < 0.01:
            return 0.0, 0.0
        f = kr * pm * node["mass"] / dist_sq
        return f * dx / dist, f * dy / dist

    if node["size"] / dist < theta:
        f = kr * pm * node["mass"] / dist_sq
        return f * dx / dist, f * dy / dist

    fx, fy = 0.0, 0.0
    if node["children"]:
        for child in node["children"]:
            if child is not None:
                cfx, cfy = _bh_force(child, px, py, pm, kr, theta)
                fx += cfx
                fy += cfy

    return fx, fy
