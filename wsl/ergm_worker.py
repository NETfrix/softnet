#!/usr/bin/env python3
"""
WSL worker: fit ERGM via R's ergm package using MCMC-MLE.

Reads graph edge list + parameters from temp files,
runs R's ergm(), writes results to JSON.

Supports MPLE-seeded MCMC via --init-coefs argument.
"""

import argparse
import json
import sys
import warnings

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Edge list CSV path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--meta", required=True, help="Meta JSON path (directed, n_vertices)")
    parser.add_argument("--terms", required=True, help="Comma-separated ERGM terms")
    parser.add_argument("--burnin", type=int, default=10000)
    parser.add_argument("--samplesize", type=int, default=10000)
    parser.add_argument("--interval", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--init-coefs", default=None, help="JSON array of initial coefficients from MPLE")
    args = parser.parse_args()

    # Suppress rpy2 symbol conflict warnings
    warnings.filterwarnings("ignore")

    import rpy2.robjects as ro
    from rpy2.robjects.packages import importr

    network_pkg = importr("network", on_conflict="warn")
    ergm_pkg = importr("ergm", on_conflict="warn")

    # Read meta
    with open(args.meta) as f:
        meta = json.load(f)

    directed = meta["directed"]
    n_vertices = meta["n_vertices"]

    # Read edge list and build adjacency matrix
    edges = []
    with open(args.input) as f:
        header = f.readline()  # skip header
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                edges.append((int(parts[0]), int(parts[1])))

    # Build adjacency matrix
    adj = np.zeros((n_vertices, n_vertices), dtype=float)
    for s, t in edges:
        adj[s, t] = 1.0
        if not directed:
            adj[t, s] = 1.0

    # Convert to R network
    r_matrix = ro.r["matrix"](
        ro.FloatVector(adj.flatten()),
        nrow=n_vertices,
        ncol=n_vertices,
    )
    net = network_pkg.as_network_matrix(r_matrix, directed=directed)

    # Build formula
    terms = [t.strip() for t in args.terms.split(",")]
    formula_str = "net ~ " + " + ".join(terms)

    ro.globalenv["net"] = net

    # Build control parameters
    control_kwargs = {
        "MCMC.burnin": args.burnin,
        "MCMC.samplesize": args.samplesize,
        "MCMC.interval": args.interval,
        "seed": args.seed,
    }

    # If MPLE initial coefficients provided, use them
    if args.init_coefs:
        init = json.loads(args.init_coefs)
        control_kwargs["init"] = ro.FloatVector(init)

    control = ergm_pkg.control_ergm(**control_kwargs)

    # Fit model
    formula = ro.Formula(formula_str)
    formula.environment["net"] = net

    print("Fitting ERGM via MCMC-MLE...", file=sys.stderr)
    result = ergm_pkg.ergm(formula, control=control)

    # Extract results
    coef_names = list(ro.r["names"](ro.r["coef"](result)))
    coef_values = [float(v) for v in ro.r["coef"](result)]
    coefficients = dict(zip(coef_names, coef_values))

    # Standard errors from summary
    try:
        summ = ro.r["summary"](result)
        # Try to extract coefficient table from summary
        coef_table = ro.r("function(s) { tryCatch(s$coefficients, error=function(e) tryCatch(s$coefs, error=function(e2) NULL)) }")(summ)
        if coef_table is not None and hasattr(coef_table, 'rx'):
            se_values = [float(coef_table.rx(i + 1, 2)[0]) for i in range(len(coef_names))]
            std_errors = dict(zip(coef_names, se_values))
            z_col = 3 if coef_table.ncol >= 3 else None
            if z_col:
                z_values_list = [float(coef_table.rx(i + 1, z_col)[0]) for i in range(len(coef_names))]
                z_values = dict(zip(coef_names, z_values_list))
            else:
                z_values = {k: None for k in coef_names}
        else:
            # Fallback: compute SE from vcov
            vcov = ro.r("function(m) tryCatch(vcov(m), error=function(e) NULL)")(result)
            if vcov is not None:
                se_values = [float(ro.r("function(v,i) sqrt(v[i,i])")(vcov, i + 1)[0]) for i in range(len(coef_names))]
                std_errors = dict(zip(coef_names, se_values))
                z_values = {k: round(coef_values[i] / se_values[i], 4) if se_values[i] > 0 else None for i, k in enumerate(coef_names)}
            else:
                std_errors = {k: None for k in coef_names}
                z_values = {k: None for k in coef_names}
    except Exception as e:
        print(f"SE extraction warning: {e}", file=sys.stderr)
        std_errors = {k: None for k in coef_names}
        z_values = {k: None for k in coef_names}

    aic = float(ro.r["AIC"](result)[0])
    bic = float(ro.r["BIC"](result)[0])

    # Log-likelihood
    try:
        ll = float(ro.r("function(m) as.numeric(logLik(m))")(result)[0])
    except Exception:
        ll = None

    output = {
        "coefficients": coefficients,
        "std_errors": std_errors,
        "z_values": z_values,
        "aic": round(aic, 2),
        "bic": round(bic, 2),
        "log_likelihood": round(ll, 2) if ll is not None else None,
        "formula": formula_str,
        "method": "MCMC-MLE (seeded)" if args.init_coefs else "MCMC-MLE",
        "n_edges": len(edges),
    }

    with open(args.output, "w") as f:
        json.dump(output, f)

    print("ERGM fitting complete.", file=sys.stderr)


if __name__ == "__main__":
    main()
