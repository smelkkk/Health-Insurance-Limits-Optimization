"""Helpers for generating downloadable content."""

import io
from datetime import date

import pandas as pd


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(dfs: dict[str, pd.DataFrame]) -> bytes:
    """Write multiple DataFrames into one Excel workbook (one sheet each)."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet[:31], index=False)
    return buf.getvalue()


def generate_text_summary(kpis: dict, summary: pd.DataFrame) -> str:
    today = date.today().isoformat()
    lines = [
        "=" * 60,
        "HEALTH INSURANCE LIMIT OPTIMISATION - EXECUTIVE SUMMARY",
        f"Generated: {today}",
        "=" * 60,
        "",
        f"Total services analysed:          {kpis['n_services']}",
        f"Total historical claims:          {kpis['total_claims']:,}",
        f"Total reimbursement (original):   {kpis['total_current_reimb']:,.0f} AMD",
        f"Total reimbursement (optimised):  {kpis['total_opt_reimb']:,.0f} AMD",
        f"Expected saving:                  {kpis['saving_amd']:,.0f} AMD ({kpis['saving_pct']:.2f}%)",
        f"Budget-neutral:                   {'Yes' if kpis['budget_neutral'] else 'No'}",
        f"Risk-aversion parameter (λ):      {kpis['lambda_used']}",
        "",
        "-" * 60,
        "PER-SERVICE SUMMARY",
        "-" * 60,
    ]

    display_cols = [
        "service_name", "original_limit", "optimized_limit",
        "delta", "delta_pct", "n_claims", "binding_rate",
    ]
    col_headers = [
        "Service", "Original Limit", "Optimised Limit",
        "Δ AMD", "Δ%", "# Claims", "Binding Rate%",
    ]
    lines.append("  ".join(f"{h:<28}" if i == 0 else f"{h:>14}" for i, h in enumerate(col_headers)))
    for _, row in summary.iterrows():
        lines.append(
            f"  {row['service_name']:<26}  "
            f"  {int(row['original_limit']):>14,}"
            f"  {int(row['optimized_limit']):>14,}"
            f"  {int(row['delta']):>+14,}"
            f"  {row['delta_pct']:>13.2f}%"
            f"  {int(row['n_claims']):>10,}"
            f"  {row['binding_rate']:>13.0f}%"
        )

    lines += [
        "",
        "-" * 60,
        "METHODOLOGY NOTE",
        "-" * 60,
        "Model: Mixed Integer Quadratic Programme (MIQP) - Gurobi 13",
        f"Objective: minimise Σ wᵢ [E[rᵢ(Tᵢ)] + λ · Var[rᵢ(Tᵢ)]]",
        f"Constraint: Σ δᵢ = 0 (budget-neutral)",
        f"Adaptive ε: εᵢ = min({0.05}, 0.4 / √nᵢ)",
        "",
        "Results are based on historical claim distributions and",
        "should be reviewed by qualified actuaries before implementation.",
        "=" * 60,
    ]
    return "\n".join(lines)
