import glob
import json
import pickle
import re

import numpy as np
import pandas as pd
import streamlit as st

from src.config import (
    K_EPSILON, MAX_EPSILON, OPT_INPUTS_PATH, OPT_LIMITS_PATH,
    OPTIMIZED_LIMITS, ORIGINAL_LIMITS, PRECOMPUTED_DIR, SERVICE_NAMES,
    SERVICES_DIR,
)


@st.cache_data
def load_service_claims() -> dict[int, pd.DataFrame]:
    """Return {service_id: DataFrame} for all 11 services."""
    files = sorted(
        glob.glob(str(SERVICES_DIR / "services_*.xlsx")),
        key=lambda f: int(re.search(r"services_(\d+)_", f).group(1)),
    )
    result = {}
    for path in files:
        idx   = int(re.search(r"services_(\d+)_", path).group(1))
        limit = int(re.search(r"services_\d+_(\d+)", path).group(1))
        df    = pd.read_excel(path)
        df["service_id"]   = idx
        df["limit"]        = limit
        df["service_name"] = SERVICE_NAMES.get(idx, f"Service {idx}")
        result[idx] = df
    return result


@st.cache_data
def load_optimization_inputs() -> list[dict]:
    with open(OPT_INPUTS_PATH, "rb") as f:
        return pickle.load(f)


@st.cache_data
def load_optimized_limits() -> pd.DataFrame:
    df = pd.read_csv(OPT_LIMITS_PATH)
    df["ServiceName"] = df["ServiceIndex"].map(SERVICE_NAMES)
    return df


@st.cache_data
def load_precomputed_scenarios() -> dict | None:
    path = PRECOMPUTED_DIR / "scenarios.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


@st.cache_data
def load_lambda_sweep() -> list[dict] | None:
    path = PRECOMPUTED_DIR / "lambda_sweep.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


@st.cache_data
def load_monte_carlo() -> dict | None:
    path = PRECOMPUTED_DIR / "monte_carlo.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def build_service_summary(
    claims: dict[int, pd.DataFrame],
    opt_inputs: list[dict],
) -> pd.DataFrame:
    """Aggregate per-service statistics into a single summary DataFrame."""
    rows = []
    for idx, df in claims.items():
        c       = df["ClaimedAmount"]
        r       = df["TotalApprovedAmount"]
        limit   = ORIGINAL_LIMITS[idx]
        opt_lim = OPTIMIZED_LIMITS[idx]
        n       = len(df)

        # Use min(ClaimedAmount, limit) for both - matches comparison.ipynb methodology
        reimb_orig = np.minimum(c.values, limit).sum()
        reimb_opt  = np.minimum(c.values, opt_lim).sum()

        pct_below = (c < limit).mean() * 100
        pct_at    = (c >= limit).mean() * 100   # claims that hit or exceeded the limit

        rows.append(
            {
                "service_id":       idx,
                "service_name":     SERVICE_NAMES.get(idx, f"Service {idx}"),
                "original_limit":   limit,
                "optimized_limit":  opt_lim,
                "delta":            opt_lim - limit,
                "delta_pct":        (opt_lim - limit) / limit * 100,
                "n_claims":         n,
                "mean_claim":       c.mean(),
                "median_claim":     c.median(),
                "max_claim":        c.max(),
                "total_claimed":    c.sum(),
                "total_reimbursed_original":  reimb_orig,
                "total_reimbursed_optimized": reimb_opt,
                "pct_below_limit":  pct_below,
                "pct_at_or_above":  pct_at,
                "binding_rate":     pct_at,
                "epsilon":          min(MAX_EPSILON, K_EPSILON / np.sqrt(n)),
            }
        )

    summary = pd.DataFrame(rows).sort_values("service_id").reset_index(drop=True)
    total_claims  = summary["n_claims"].sum()
    total_claimed = summary["total_claimed"].sum()
    summary["claim_share"]        = summary["n_claims"]        / total_claims  * 100
    summary["reimbursement_share"]= summary["total_reimbursed_original"] / summary["total_reimbursed_original"].sum() * 100
    return summary
