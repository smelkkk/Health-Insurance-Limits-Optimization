"""Rule-based recommendation engine for the Business Recommendations page."""

import pandas as pd


_THRESHOLDS = {
    "highly_binding":    70,   # % of claims at/above limit
    "moderately_binding": 40,
    "low_data":           5,   # minimum n_claims for reliable insight
    "underused":         0.30, # mean_claim / limit ratio
}


def generate_recommendations(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame of plain-language recommendations, one row per service,
    with columns: service_name, category, headline, detail, priority.
    """
    rows = []
    for _, row in summary.iterrows():
        name    = row["service_name"]
        n       = row["n_claims"]
        binding = row["binding_rate"]
        ratio   = row["mean_claim"] / row["original_limit"] if row["original_limit"] else 0
        delta   = row["delta_pct"]
        limit   = row["original_limit"]
        opt_lim = row["optimized_limit"]

        if n < _THRESHOLDS["low_data"]:
            rows.append({
                "service_name": name,
                "category":     "Needs More Data",
                "headline":     f"Only {n} historical claims — results unreliable.",
                "detail":       (
                    f"With fewer than {_THRESHOLDS['low_data']} claims, the distribution estimate "
                    "is statistically weak. Collect more data before acting on model output for this service."
                ),
                "priority": 4,
            })
            continue

        if binding > _THRESHOLDS["highly_binding"]:
            rows.append({
                "service_name": name,
                "category":     "Review Immediately",
                "headline":     f"Limit is highly binding: {binding:.0f}% of claims hit the cap.",
                "detail":       (
                    f"The current limit of {int(limit):,} {_currency()} is frequently reached, "
                    f"suggesting significant out-of-pocket exposure for policyholders. "
                    f"The model recommends adjusting to {int(opt_lim):,} AMD ({delta:+.1f}%)."
                ),
                "priority": 1,
            })

        elif binding > _THRESHOLDS["moderately_binding"]:
            rows.append({
                "service_name": name,
                "category":     "Monitor",
                "headline":     f"Limit is moderately binding ({binding:.0f}% hit the cap).",
                "detail":       (
                    f"A notable share of claims reaches the current limit. "
                    f"The model suggests a {delta:+.1f}% adjustment to {int(opt_lim):,} AMD. "
                    "Worth monitoring as claim volume grows."
                ),
                "priority": 2,
            })

        elif ratio < _THRESHOLDS["underused"]:
            rows.append({
                "service_name": name,
                "category":     "Low-Risk Adjustment",
                "headline":     f"Limit appears over-funded (mean claim is {ratio*100:.0f}% of limit).",
                "detail":       (
                    f"Claims average only {int(row['mean_claim']):,} AMD against a limit of "
                    f"{int(limit):,} AMD. The model reduces the limit to {int(opt_lim):,} AMD ({delta:+.1f}%), "
                    "freeing budget for more binding services at low actuarial risk."
                ),
                "priority": 3,
            })

        else:
            rows.append({
                "service_name": name,
                "category":     "Monitor",
                "headline":     "Limit appears reasonably calibrated.",
                "detail":       (
                    f"Claim patterns are broadly aligned with the current limit of {int(limit):,} AMD. "
                    f"The model recommends a modest {delta:+.1f}% adjustment for portfolio balance. "
                    "No urgent action required."
                ),
                "priority": 2,
            })

    return (
        pd.DataFrame(rows)
        .sort_values("priority")
        .reset_index(drop=True)
    )


def _currency() -> str:
    from src.config import CURRENCY
    return CURRENCY


CATEGORY_COLOURS = {
    "Review Immediately": "#EF4444",
    "Monitor":            "#F59E0B",
    "Low-Risk Adjustment": "#10B981",
    "Needs More Data":    "#6B7280",
}

CATEGORY_ICONS = {
    "Review Immediately": "🔴",
    "Monitor":            "🟡",
    "Low-Risk Adjustment": "🟢",
    "Needs More Data":    "⚪",
}
