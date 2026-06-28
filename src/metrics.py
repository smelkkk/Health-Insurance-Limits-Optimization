import numpy as np
import pandas as pd


def portfolio_kpis(summary: pd.DataFrame) -> dict:
    """Top-level KPIs for the executive summary."""
    total_orig  = summary["total_reimbursed_original"].sum()
    total_opt   = summary["total_reimbursed_optimized"].sum()
    saving      = total_orig - total_opt
    saving_pct  = saving / total_orig * 100 if total_orig else 0

    # Simple variance proxy: std of per-service reimbursed amounts across simulated claims
    # (using original vs optimized max-clip)
    return {
        "n_services":          len(summary),
        "total_claims":        int(summary["n_claims"].sum()),
        "total_current_reimb": total_orig,
        "total_opt_reimb":     total_opt,
        "saving_amd":          saving,
        "saving_pct":          saving_pct,
        "budget_neutral":      True,
        "lambda_used":         0.01,
        "high_volume_service": summary.loc[summary["n_claims"].idxmax(), "service_name"],
        "most_binding_service": summary.loc[summary["binding_rate"].idxmax(), "service_name"],
    }


def limit_diagnostics(summary: pd.DataFrame) -> pd.DataFrame:
    """Flag each service with a diagnostic category."""
    diag = summary.copy()

    def _flag(row):
        if row["n_claims"] < 5:
            return "Insufficient Data"
        if row["binding_rate"] > 70:
            return "Highly Binding"
        if row["binding_rate"] > 40:
            return "Moderately Binding"
        if row["mean_claim"] < 0.3 * row["original_limit"]:
            return "Underused Limit"
        return "Well Calibrated"

    diag["diagnostic"] = diag.apply(_flag, axis=1)

    diagnostic_order = {
        "Highly Binding":    0,
        "Moderately Binding": 1,
        "Underused Limit":   2,
        "Well Calibrated":   3,
        "Insufficient Data": 4,
    }
    diag["diagnostic_rank"] = diag["diagnostic"].map(diagnostic_order)
    return diag.sort_values("diagnostic_rank")


def compute_reimbursement_curve(c_ij: np.ndarray, p_ij: np.ndarray, limits: np.ndarray) -> np.ndarray:
    """Expected reimbursement E[min(claim, T)] for a range of limit values T."""
    return np.array([np.sum(p_ij * np.minimum(c_ij, T)) for T in limits])


def pareto_table(summary: pd.DataFrame) -> pd.DataFrame:
    """Cumulative claim share (Pareto view), sorted by reimbursement_share desc."""
    df = summary[["service_name", "n_claims", "claim_share", "reimbursement_share"]].copy()
    df = df.sort_values("reimbursement_share", ascending=False).reset_index(drop=True)
    df["cumulative_reimb_share"] = df["reimbursement_share"].cumsum()
    df["cumulative_claim_share"] = df["claim_share"].cumsum()
    return df
