"""
Loads precomputed optimization scenarios produced by precompute_scenarios.py.
Falls back gracefully when precomputed files are absent (shows setup instructions).
"""

import numpy as np
import pandas as pd

from src.config import NAMED_SCENARIOS, OPTIMIZED_LIMITS, ORIGINAL_LIMITS, SERVICE_NAMES


def get_named_scenario(scenarios: dict, name: str) -> dict | None:
    if scenarios is None:
        return None
    named = scenarios.get("named", {})
    return named.get(name)


def get_scenario_for_lambda(scenarios: dict, target_lambda: float) -> dict | None:
    """Return the precomputed scenario closest to target_lambda."""
    if scenarios is None:
        return None
    sweep = scenarios.get("lambda_sweep", [])
    if not sweep:
        return None
    lambdas = np.array([s["lambda"] for s in sweep])
    idx     = int(np.argmin(np.abs(np.log10(lambdas) - np.log10(target_lambda))))
    return sweep[idx]


def scenario_to_dataframe(scenario: dict) -> pd.DataFrame:
    """Convert a scenario dict into a per-service comparison DataFrame."""
    n = len(scenario["adjusted_limits"])
    rows = []
    for i in range(n):
        svc_id = i + 1
        orig   = ORIGINAL_LIMITS.get(svc_id, scenario.get("original_limits", [None] * n)[i])
        adj    = scenario["adjusted_limits"][i]
        rows.append(
            {
                "service_id":      svc_id,
                "service_name":    SERVICE_NAMES.get(svc_id, f"Service {svc_id}"),
                "original_limit":  orig,
                "adjusted_limit":  adj,
                "delta":           adj - orig,
                "delta_pct":       (adj - orig) / orig * 100 if orig else 0,
            }
        )
    return pd.DataFrame(rows)


def fallback_balanced_dataframe() -> pd.DataFrame:
    """Return the known optimised result (λ=0.01) as a DataFrame when no precomputed file exists."""
    rows = []
    for svc_id, orig in ORIGINAL_LIMITS.items():
        adj = OPTIMIZED_LIMITS[svc_id]
        rows.append(
            {
                "service_id":     svc_id,
                "service_name":   SERVICE_NAMES[svc_id],
                "original_limit": orig,
                "adjusted_limit": adj,
                "delta":          adj - orig,
                "delta_pct":      (adj - orig) / orig * 100,
            }
        )
    return pd.DataFrame(rows)


def lambda_sweep_dataframe(scenarios: dict) -> pd.DataFrame | None:
    """Convert lambda_sweep list to a tidy DataFrame for charting."""
    if scenarios is None:
        return None
    sweep = scenarios.get("lambda_sweep", [])
    if not sweep:
        return None
    rows = []
    for s in sweep:
        rows.append(
            {
                "lambda":               s["lambda"],
                "expected_payout_total": s.get("expected_payout_total", np.nan),
                "variance_total":        s.get("variance_total", np.nan),
            }
        )
    df = pd.DataFrame(rows).sort_values("lambda").reset_index(drop=True)
    # Normalise for display
    df["expected_M"] = df["expected_payout_total"] / 1e6
    df["variance_M"] = df["variance_total"] / 1e6
    return df
