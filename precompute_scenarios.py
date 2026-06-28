"""
Run once locally to generate precomputed optimisation scenarios.
Requires a valid Gurobi licence.

Usage:
    conda activate capstone
    python precompute_scenarios.py

Outputs saved to: data/precomputed/
  - scenarios.json   (lambda sweep + named scenarios)
  - monte_carlo.json (100 Monte Carlo runs)
"""

import glob
import json
import os
import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

BASE_DIR       = Path(__file__).parent
SERVICES_DIR   = BASE_DIR / "services"
PRECOMPUTED    = BASE_DIR / "data" / "precomputed"
PRECOMPUTED.mkdir(parents=True, exist_ok=True)

K_EPSILON  = 0.4
MAX_EPS    = 0.05
M_BIG      = 1e7
LAMBDA_DEF = 1e-2

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading optimization_inputs.pkl …")
with open(BASE_DIR / "optimization_inputs.pkl", "rb") as f:
    optimization_inputs = pickle.load(f)

n = len(optimization_inputs)

# Claim counts for adaptive epsilon and weights
files = sorted(
    glob.glob(str(SERVICES_DIR / "services_*.xlsx")),
    key=lambda p: int(re.search(r"services_(\d+)_", p).group(1)),
)
claim_counts = []
for path in files:
    df = pd.read_excel(path)
    claim_counts.append(len(df))

total_claims = sum(claim_counts)
weights      = [c / total_claims for c in claim_counts]
epsilons     = [min(MAX_EPS, K_EPSILON / np.sqrt(c)) for c in claim_counts]
original_limits = [s["limit"] for s in optimization_inputs]

# ── Solver helper ──────────────────────────────────────────────────────────────
def solve_miqp(lambda_penalty: float, epsilons: list, weights: list) -> dict | None:
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError:
        print("ERROR: gurobipy not available. Skipping solver.")
        return None

    model = gp.Model("MIQP_Scenario")
    model.setParam("OutputFlag", 0)
    model.setParam("Presolve", 0)
    model.setParam("Heuristics", 0)
    model.setParam("Cuts", 0)
    model.setParam("MIPFocus", 1)

    delta  = model.addVars(n, lb=-GRB.INFINITY, name="delta")
    m_vars = {}
    z_vars = {}

    for i, service in enumerate(optimization_inputs):
        m_vars[i] = []
        z_vars[i] = []
        for j in range(len(service["c_ij"])):
            m_vars[i].append(model.addVar(lb=0.0, name=f"m_{i}_{j}"))
            z_vars[i].append(model.addVar(vtype=GRB.BINARY, name=f"z_{i}_{j}"))

    model.update()
    model.addConstr(gp.quicksum(delta[i] for i in range(n)) == 0, name="budget_neutral")

    for i, service in enumerate(optimization_inputs):
        lim  = service["limit"]
        c_ij = service["c_ij"]
        T_i  = lim + delta[i]
        eps  = epsilons[i]
        model.addConstr(delta[i] <= eps * lim)
        model.addConstr(delta[i] >= -eps * lim)
        for j, c in enumerate(c_ij):
            m = m_vars[i][j]; z = z_vars[i][j]
            model.addConstr(m <= T_i)
            model.addConstr(m <= c)
            model.addConstr(m >= T_i - M_BIG * (1 - z))
            model.addConstr(m >= c - M_BIG * z)

    quad_obj = gp.QuadExpr()
    for i, service in enumerate(optimization_inputs):
        p_ij = service["p_ij"]
        m_i  = m_vars[i]
        w_i  = weights[i]
        expected_i    = gp.LinExpr(sum(p_ij[j] * m_i[j] for j in range(len(p_ij))))
        expected_sq   = gp.QuadExpr()
        squared_exp   = gp.QuadExpr()
        for j in range(len(p_ij)):
            expected_sq += p_ij[j] * m_i[j] * m_i[j]
        for j in range(len(p_ij)):
            for k in range(len(p_ij)):
                squared_exp += p_ij[j] * p_ij[k] * m_i[j] * m_i[k]
        variance_i = expected_sq - squared_exp
        quad_obj  += w_i * (expected_i + lambda_penalty * variance_i)

    model.setObjective(quad_obj, GRB.MINIMIZE)
    model.optimize()

    if model.status != GRB.OPTIMAL:
        return None

    adj_limits, deltas = [], []
    expected_by, variance_by = [], []
    for i, service in enumerate(optimization_inputs):
        d      = delta[i].X
        new_lim = service["limit"] + d
        adj_limits.append(float(new_lim))
        deltas.append(float(d))
        c_ij, p_ij = service["c_ij"], service["p_ij"]
        exp_i  = sum(p_ij[j] * min(new_lim, c_ij[j]) for j in range(len(p_ij)))
        exp_sq = sum(p_ij[j] * min(new_lim, c_ij[j])**2 for j in range(len(p_ij)))
        var_i  = exp_sq - exp_i ** 2
        expected_by.append(float(exp_i))
        variance_by.append(float(var_i))

    return {
        "lambda":               lambda_penalty,
        "adjusted_limits":      adj_limits,
        "original_limits":      [float(s["limit"]) for s in optimization_inputs],
        "deltas":               deltas,
        "expected_payout_total": float(sum(expected_by)),
        "variance_total":        float(sum(variance_by)),
        "expected_by_service":  expected_by,
        "variance_by_service":  variance_by,
        "objective":            float(model.ObjVal),
    }


# ── Lambda sweep ───────────────────────────────────────────────────────────────
LAMBDA_VALUES = [1e-7, 1e-6, 1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 1e0]

print(f"\nRunning lambda sweep across {len(LAMBDA_VALUES)} values …")
sweep_results = []
for lam in tqdm(LAMBDA_VALUES):
    res = solve_miqp(lam, epsilons, weights)
    if res:
        sweep_results.append(res)
    else:
        print(f"  ⚠ λ={lam:.1e} — no optimal solution, skipped.")

named = {}
for scenario_name, cfg in {
    "Cost-Focused":      1e-5,
    "Balanced":          1e-2,
    "Stability-Focused": 1e-1,
}.items():
    match = min(sweep_results, key=lambda r: abs(np.log10(r["lambda"]) - np.log10(cfg)), default=None)
    if match:
        named[scenario_name] = match

scenarios_data = {"lambda_sweep": sweep_results, "named": named}
out_path = PRECOMPUTED / "scenarios.json"
with open(out_path, "w") as f:
    json.dump(scenarios_data, f, indent=2)
print(f"✅  Scenarios saved → {out_path}")


# ── Monte Carlo ────────────────────────────────────────────────────────────────
from src.config import OPTIMIZED_LIMITS, ORIGINAL_LIMITS

print("\nRunning Monte Carlo simulation (100 runs) …")
orig_lims = [ORIGINAL_LIMITS[i]  for i in sorted(ORIGINAL_LIMITS)]
opt_lims  = [OPTIMIZED_LIMITS[i] for i in sorted(OPTIMIZED_LIMITS)]
rng       = np.random.default_rng(42)

orig_totals, adj_totals = [], []
for _ in tqdm(range(100)):
    ot = at = 0.0
    for i, service in enumerate(optimization_inputs):
        c_ij, p_ij = service["c_ij"], service["p_ij"]
        n_obs       = claim_counts[i]
        sampled     = rng.choice(c_ij, size=n_obs, p=p_ij)
        ot += np.clip(sampled, None, orig_lims[i]).sum()
        at += np.clip(sampled, None, opt_lims[i]).sum()
    orig_totals.append(float(ot))
    adj_totals.append(float(at))

diffs = [a - o for a, o in zip(adj_totals, orig_totals)]
mc_data = {
    "n_simulations":   100,
    "original_totals": orig_totals,
    "adjusted_totals": adj_totals,
    "differences":     diffs,
    "mean_difference": float(np.mean(diffs)),
    "std_difference":  float(np.std(diffs)),
}
mc_path = PRECOMPUTED / "monte_carlo.json"
with open(mc_path, "w") as f:
    json.dump(mc_data, f, indent=2)
print(f"✅  Monte Carlo saved → {mc_path}")
print("\nAll done. You can now run the Streamlit app.")
