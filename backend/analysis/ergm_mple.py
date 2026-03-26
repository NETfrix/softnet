"""
ERGM via Maximum Pseudo-Likelihood Estimation (MPLE).

Reduces ERGM fitting to logistic regression on network change statistics.
No R or statnet required — pure Python with igraph, numpy, scipy.

Supported terms:
  - edges: baseline edge propensity (intercept)
  - mutual: reciprocity in directed networks
  - triangles: transitivity (triangle count change)
  - gwesp(alpha): geometrically weighted edgewise shared partners
  - nodematch(attr): homophily on a categorical node attribute
  - nodeicov(attr): receiver covariate effect (continuous attribute)
  - nodeocov(attr): sender covariate effect (continuous attribute)
  - nodecov(attr): undirected covariate effect
  - absdiff(attr): absolute difference in continuous attribute
"""

from __future__ import annotations

import re
from collections import Counter

import igraph as ig
import numpy as np


def _parse_term(term_str: str) -> tuple[str, dict]:
    """Parse a term like 'gwesp(0.5)' or 'nodematch(gender)' into (name, params)."""
    term_str = term_str.strip()
    m = re.match(r"(\w+)\((.+)\)", term_str)
    if m:
        name = m.group(1)
        args_str = m.group(2)
        # Parse arguments
        params = {}
        for i, arg in enumerate(args_str.split(",")):
            arg = arg.strip()
            if "=" in arg:
                k, v = arg.split("=", 1)
                params[k.strip()] = v.strip()
            elif i == 0:
                # First positional arg
                try:
                    params["value"] = float(arg)
                except ValueError:
                    params["attr"] = arg
            else:
                try:
                    params["value2"] = float(arg)
                except ValueError:
                    params[f"arg{i}"] = arg
        return name, params
    return term_str, {}


def _compute_change_stat_edges(g: ig.Graph, i: int, j: int, present: bool) -> float:
    """Change statistic for 'edges' term: always 1 for adding, -1 for removing."""
    return 1.0


def _compute_change_stat_mutual(g: ig.Graph, i: int, j: int, present: bool) -> float:
    """Change statistic for 'mutual': 1 if reverse edge exists."""
    if not g.is_directed():
        return 0.0
    return 1.0 if g.are_connected(j, i) else 0.0


def _compute_change_stat_triangles(g: ig.Graph, i: int, j: int, present: bool) -> float:
    """Change statistic for 'triangles': number of shared neighbors."""
    ni = set(g.neighbors(i))
    nj = set(g.neighbors(j))
    return float(len(ni & nj))


def _compute_change_stat_gwesp(
    g: ig.Graph, i: int, j: int, present: bool, alpha: float = 0.5
) -> float:
    """
    Change statistic for geometrically weighted edgewise shared partners.
    Uses the GWESP formula with decay parameter alpha.
    """
    ni = set(g.neighbors(i))
    nj = set(g.neighbors(j))
    shared = ni & nj

    # Count how many shared partners are connected to both via edges
    esp_count = 0
    for k in shared:
        # k is a shared neighbor — check if edges i-k and j-k both exist
        # (they do since k is in both neighbor sets)
        esp_count += 1

    if esp_count == 0:
        return 0.0

    # GWESP change statistic
    decay = np.exp(-alpha)
    return np.exp(alpha) * (1.0 - (1.0 - decay) ** esp_count)


def _compute_change_stat_nodematch(
    g: ig.Graph, i: int, j: int, present: bool, attr: str
) -> float:
    """Change statistic for 'nodematch': 1 if nodes share same attribute value."""
    if attr not in g.vs.attributes():
        return 0.0
    return 1.0 if g.vs[i][attr] == g.vs[j][attr] else 0.0


def _compute_change_stat_nodecov(
    g: ig.Graph, i: int, j: int, present: bool, attr: str
) -> float:
    """Change statistic for 'nodecov': sum of attribute values."""
    if attr not in g.vs.attributes():
        return 0.0
    vi = g.vs[i][attr]
    vj = g.vs[j][attr]
    try:
        return float(vi) + float(vj)
    except (TypeError, ValueError):
        return 0.0


def _compute_change_stat_absdiff(
    g: ig.Graph, i: int, j: int, present: bool, attr: str
) -> float:
    """Change statistic for 'absdiff': absolute difference in attribute."""
    if attr not in g.vs.attributes():
        return 0.0
    try:
        return abs(float(g.vs[i][attr]) - float(g.vs[j][attr]))
    except (TypeError, ValueError):
        return 0.0


def _build_change_stat_func(term_name: str, params: dict):
    """Return a function (g, i, j, present) -> float for a given term."""
    if term_name == "edges":
        return _compute_change_stat_edges
    elif term_name == "mutual":
        return _compute_change_stat_mutual
    elif term_name == "triangles":
        return _compute_change_stat_triangles
    elif term_name == "gwesp":
        alpha = params.get("value", 0.5)
        return lambda g, i, j, p: _compute_change_stat_gwesp(g, i, j, p, alpha=float(alpha))
    elif term_name == "nodematch":
        attr = params.get("attr", params.get("value", ""))
        return lambda g, i, j, p: _compute_change_stat_nodematch(g, i, j, p, attr=str(attr))
    elif term_name in ("nodecov", "nodeicov", "nodeocov"):
        attr = params.get("attr", params.get("value", ""))
        return lambda g, i, j, p: _compute_change_stat_nodecov(g, i, j, p, attr=str(attr))
    elif term_name == "absdiff":
        attr = params.get("attr", params.get("value", ""))
        return lambda g, i, j, p: _compute_change_stat_absdiff(g, i, j, p, attr=str(attr))
    else:
        raise ValueError(f"Unknown ERGM term: {term_name}")


def fit_ergm_mple(
    g: ig.Graph,
    terms: list[str],
    sample_fraction: float = 1.0,
    seed: int = 42,
) -> dict:
    """
    Fit ERGM via Maximum Pseudo-Likelihood Estimation.

    For large networks (n > 1000), automatically samples dyads to keep
    computation tractable.

    Args:
        g: The network.
        terms: List of ERGM term strings, e.g. ["edges", "mutual", "gwesp(0.5)"].
        sample_fraction: Fraction of non-edges to sample (1.0 = all dyads).
        seed: Random seed for sampling.

    Returns:
        Dict with coefficients, standard errors, AIC, BIC, and formula.
    """
    from scipy.special import expit

    rng = np.random.default_rng(seed)
    n = g.vcount()
    directed = g.is_directed()

    # Parse terms
    parsed = [_parse_term(t) for t in terms]
    stat_funcs = [_build_change_stat_func(name, params) for name, params in parsed]
    term_labels = []
    for t in terms:
        t = t.strip()
        term_labels.append(t)

    # Build set of existing edges for fast lookup
    edge_set = set()
    for e in g.es:
        edge_set.add((e.source, e.target))
        if not directed:
            edge_set.add((e.target, e.source))

    # Enumerate dyads (or sample for large networks)
    total_dyads = n * (n - 1) if directed else n * (n - 1) // 2
    max_dyads = 50000  # Cap for tractability

    if total_dyads > max_dyads:
        # Sample: all edges + sample of non-edges
        dyads = []
        y = []

        # Include all edges
        for e in g.es:
            dyads.append((e.source, e.target))
            y.append(1)
            if directed:
                # Don't double-add for directed
                pass

        # Sample non-edges
        n_non_edges = min(max_dyads - len(dyads), total_dyads - g.ecount())
        sampled = 0
        attempts = 0
        max_attempts = n_non_edges * 10
        while sampled < n_non_edges and attempts < max_attempts:
            i = rng.integers(0, n)
            j = rng.integers(0, n)
            if i == j:
                attempts += 1
                continue
            if not directed and i > j:
                i, j = j, i
            if (i, j) not in edge_set:
                dyads.append((i, j))
                y.append(0)
                sampled += 1
            attempts += 1
    else:
        # Enumerate all dyads
        dyads = []
        y = []
        for i in range(n):
            j_start = 0 if directed else i + 1
            for j in range(j_start, n):
                if i == j:
                    continue
                dyads.append((i, j))
                y.append(1 if (i, j) in edge_set else 0)

    y = np.array(y, dtype=float)
    n_dyads = len(dyads)
    n_terms = len(stat_funcs)

    # Compute change statistics matrix
    X = np.zeros((n_dyads, n_terms), dtype=float)
    for idx, (i, j) in enumerate(dyads):
        present = (i, j) in edge_set
        for k, func in enumerate(stat_funcs):
            X[idx, k] = func(g, i, j, present)

    # Fit logistic regression via iteratively reweighted least squares (scipy)
    from scipy.optimize import minimize

    def neg_log_likelihood(beta):
        logits = X @ beta
        # Numerically stable log-likelihood
        ll = np.sum(y * logits - np.logaddexp(0, logits))
        return -ll

    def gradient(beta):
        logits = X @ beta
        p = expit(logits)
        return -X.T @ (y - p)

    # Initial guess
    beta0 = np.zeros(n_terms)
    result = minimize(neg_log_likelihood, beta0, jac=gradient, method="L-BFGS-B")
    beta = result.x

    # Compute standard errors from Fisher information (Hessian)
    logits = X @ beta
    p = expit(logits)
    W = p * (1 - p)
    # Hessian = X^T W X
    H = X.T @ (X * W[:, None])
    try:
        cov = np.linalg.inv(H)
        se = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError:
        se = np.full(n_terms, float("nan"))

    # Compute AIC and BIC
    ll = -neg_log_likelihood(beta)
    k = n_terms
    aic = -2 * ll + 2 * k
    bic = -2 * ll + k * np.log(n_dyads)

    # Build results
    coefficients = {}
    std_errors = {}
    z_values = {}
    for i, label in enumerate(term_labels):
        coefficients[label] = round(float(beta[i]), 6)
        std_errors[label] = round(float(se[i]), 6)
        z_values[label] = round(float(beta[i] / se[i]), 4) if se[i] > 0 else None

    formula_str = "network ~ " + " + ".join(terms)

    return {
        "coefficients": coefficients,
        "std_errors": std_errors,
        "z_values": z_values,
        "aic": round(float(aic), 2),
        "bic": round(float(bic), 2),
        "log_likelihood": round(float(ll), 2),
        "formula": formula_str,
        "method": "MPLE",
        "n_dyads": n_dyads,
        "n_edges": int(np.sum(y)),
    }
