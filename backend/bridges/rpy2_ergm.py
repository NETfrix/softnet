from __future__ import annotations

from typing import Any

import igraph as ig
import numpy as np

# Lazy-load R packages to avoid import errors when R is not available
_network_pkg = None
_ergm_pkg = None
_initialized = False


def check_r_available() -> tuple[bool, str]:
    """Check if R and required packages are available."""
    try:
        import rpy2.robjects as ro
    except ImportError:
        return False, "rpy2 is not installed. Run: pip install rpy2"
    try:
        from rpy2.robjects.packages import importr
        importr("network")
        importr("ergm")
    except Exception as e:
        return False, f"R packages missing: {e}. In R, run: install.packages(c('network', 'ergm'))"
    return True, "ok"


def _init_r() -> None:
    global _network_pkg, _ergm_pkg, _initialized
    if _initialized:
        return

    import rpy2.robjects as ro
    from rpy2.robjects.packages import importr

    _network_pkg = importr("network")
    _ergm_pkg = importr("ergm")
    _initialized = True


def igraph_to_r_network(g: ig.Graph):
    """Convert igraph.Graph to R network object via adjacency matrix."""
    import rpy2.robjects as ro

    _init_r()

    adj = np.array(g.get_adjacency().data, dtype=float)
    directed = g.is_directed()

    r_matrix = ro.r["matrix"](
        ro.FloatVector(adj.flatten()),
        nrow=adj.shape[0],
        ncol=adj.shape[1],
    )

    net = _network_pkg.as_network_matrix(r_matrix, directed=directed)

    # Transfer node attributes
    for attr_name in g.vs.attributes():
        if attr_name.startswith("_"):
            continue
        values = g.vs[attr_name]
        try:
            if all(isinstance(v, (int, float)) for v in values if v is not None):
                r_values = ro.FloatVector([float(v) if v is not None else float("nan") for v in values])
            else:
                r_values = ro.StrVector([str(v) if v is not None else "" for v in values])
            _network_pkg.set_vertex_attribute(net, attr_name, r_values)
        except Exception:
            pass  # Skip attributes that can't be converted

    return net


def fit_ergm(
    g: ig.Graph,
    terms: list[str],
    burnin: int = 10000,
    samplesize: int = 10000,
    interval: int = 1024,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Fit ERGM using R's ergm package.

    terms: e.g. ["edges", "mutual", "gwesp(0.5, fixed=TRUE)"]

    WARNING: ERGM is computationally expensive. Not feasible for graphs > ~5000 nodes.
    """
    import rpy2.robjects as ro

    _init_r()

    net = igraph_to_r_network(g)

    # Build formula string
    formula_str = "net ~ " + " + ".join(terms)

    # Place network in R global env
    ro.globalenv["net"] = net

    # Configure MCMC control
    control = _ergm_pkg.control_ergm(
        **{
            "MCMC.burnin": burnin,
            "MCMC.samplesize": samplesize,
            "MCMC.interval": interval,
            "seed": seed,
        }
    )

    # Fit model
    formula = ro.Formula(formula_str)
    formula.environment["net"] = net
    result = _ergm_pkg.ergm(formula, control=control)

    # Extract results
    coef_names = list(ro.r["names"](ro.r["coef"](result)))
    coef_values = list(ro.r["coef"](result))
    coefficients = dict(zip(coef_names, [float(v) for v in coef_values]))

    aic = float(ro.r["AIC"](result)[0])
    bic = float(ro.r["BIC"](result)[0])

    return {
        "coefficients": coefficients,
        "aic": aic,
        "bic": bic,
        "formula": formula_str,
    }
