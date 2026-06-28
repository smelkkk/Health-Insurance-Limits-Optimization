"""All Plotly chart functions - KinetiX dark theme."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import (
    C_CHART_1, C_CHART_2, C_CHART_3, C_CHART_4, C_CHART_5,
    C_DARK, C_BG, C_LIGHT, C_NEGATIVE, C_NEUTRAL,
    C_OPTIMIZED, C_PRIMARY, C_SECONDARY, C_WARNING,
    CURRENCY, PLOTLY_LAYOUT,
)


def _dark(fig: go.Figure, **overrides) -> go.Figure:
    """Apply the global dark layout to any figure."""
    layout = {**PLOTLY_LAYOUT, **overrides}
    fig.update_layout(**layout)
    return fig


def _fmt(val: float) -> str:
    if val >= 1_000_000:
        return f"{val/1_000_000:.2f}M"
    if val >= 1_000:
        return f"{val/1_000:.0f}K"
    return f"{val:,.0f}"


# ── Data Overview ──────────────────────────────────────────────────────────────

def claims_by_service_bar(summary: pd.DataFrame) -> go.Figure:
    df = summary.sort_values("n_claims", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["n_claims"], y=df["service_name"], orientation="h",
        text=df["n_claims"], textposition="outside",
        marker_color=C_PRIMARY,
        textfont=dict(color=C_LIGHT),
    ))
    return _dark(fig, title="Claim Volume by Service",
                 xaxis_title="Number of Claims", yaxis_title="",
                 height=400, showlegend=False)


def reimbursement_by_service_bar(summary: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary["service_name"], y=summary["total_claimed"],
        name="Total Claimed", marker_color=C_CHART_5,
    ))
    fig.add_trace(go.Bar(
        x=summary["service_name"], y=summary["total_reimbursed_original"],
        name="Total Reimbursed", marker_color=C_PRIMARY,
    ))
    return _dark(fig, barmode="group",
                 title="Claimed vs Reimbursed Amount by Service",
                 xaxis_tickangle=-30, yaxis_title=f"Amount ({CURRENCY})",
                 height=420, legend=dict(orientation="h", y=1.12))


def pareto_chart(pareto: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=pareto["service_name"], y=pareto["reimbursement_share"],
        name="Reimbursement Share (%)", marker_color=C_PRIMARY,
    ))
    fig.add_trace(go.Scatter(
        x=pareto["service_name"], y=pareto["cumulative_reimb_share"],
        name="Cumulative %", yaxis="y2",
        mode="lines+markers",
        line=dict(color=C_SECONDARY, width=2),
        marker=dict(color=C_SECONDARY, size=6),
    ))
    return _dark(fig, title="Cost Concentration - Pareto View",
                 yaxis=dict(title="Share of Total Reimbursement (%)",
                            gridcolor="rgba(84,84,84,0.3)",
                            tickfont=dict(color=C_NEUTRAL),
                            linecolor="rgba(84,84,84,0.5)"),
                 yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                             range=[0, 105],
                             gridcolor="rgba(84,84,84,0.3)",
                             tickfont=dict(color=C_NEUTRAL),
                             linecolor="rgba(84,84,84,0.5)"),
                 xaxis_tickangle=-30, height=420,
                 legend=dict(orientation="h", y=1.12))


# ── Limit Diagnostics ─────────────────────────────────────────────────────────

def binding_rate_chart(diag: pd.DataFrame) -> go.Figure:
    colour_map = {
        "Highly Binding":    C_NEGATIVE,
        "Moderately Binding": C_WARNING,
        "Underused Limit":   C_NEUTRAL,
        "Well Calibrated":   C_OPTIMIZED,
        "Insufficient Data": C_CHART_5,
    }
    colours = diag["diagnostic"].map(colour_map).fillna(C_NEUTRAL)
    fig = go.Figure(go.Bar(
        x=diag["binding_rate"], y=diag["service_name"], orientation="h",
        marker_color=colours,
        text=[f"{v:.0f}%" for v in diag["binding_rate"]],
        textposition="outside",
        textfont=dict(color=C_LIGHT),
    ))
    fig.add_vline(x=40, line_dash="dash", line_color=C_WARNING,
                  annotation_text="Moderate", annotation_font_color=C_WARNING)
    fig.add_vline(x=70, line_dash="dash", line_color=C_NEGATIVE,
                  annotation_text="High", annotation_font_color=C_NEGATIVE)
    return _dark(fig, title="Binding Rate by Service (% claims at or above limit)",
                 xaxis=dict(title="Binding Rate (%)", range=[0, 110],
                            gridcolor="rgba(84,84,84,0.3)",
                            tickfont=dict(color=C_NEUTRAL),
                            linecolor="rgba(84,84,84,0.5)"),
                 yaxis_title="", height=400)


def claim_distribution_vs_limit(df: pd.DataFrame, limit: int, service_name: str) -> go.Figure:
    claims = df["ClaimedAmount"].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=claims, nbinsx=20, name="Claim Amount",
        marker_color=C_PRIMARY, opacity=0.8,
    ))
    fig.add_vline(x=limit, line_dash="dash", line_color=C_NEGATIVE,
                  annotation_text=f"Limit ({_fmt(limit)} {CURRENCY})",
                  annotation_position="top right",
                  annotation_font_color=C_NEGATIVE)
    return _dark(fig, title=f"Claim Distribution - {service_name}",
                 xaxis_title=f"Claimed Amount ({CURRENCY})",
                 yaxis_title="Number of Claims", height=350)


# ── Before vs After ───────────────────────────────────────────────────────────

def limits_comparison_bar(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["service_name"], y=df["original_limit"],
        name="Original Limit", marker_color=C_CHART_5,
    ))
    fig.add_trace(go.Bar(
        x=df["service_name"], y=df["adjusted_limit"],
        name="Optimised Limit", marker_color=C_PRIMARY,
    ))
    return _dark(fig, barmode="group",
                 title="Original vs Optimised Limits by Service",
                 xaxis_tickangle=-30, yaxis_title=f"Limit ({CURRENCY})",
                 height=420, legend=dict(orientation="h", y=1.12))


def delta_waterfall(df: pd.DataFrame) -> go.Figure:
    sorted_df = df.sort_values("delta", ascending=False)
    colours = [C_OPTIMIZED if d >= 0 else C_NEGATIVE for d in sorted_df["delta"]]
    fig = go.Figure(go.Bar(
        x=sorted_df["service_name"], y=sorted_df["delta"],
        marker_color=colours,
        text=[f"{_fmt(d)}" for d in sorted_df["delta"]],
        textposition="outside",
        textfont=dict(color=C_LIGHT),
    ))
    fig.add_hline(y=0, line_color="rgba(84,84,84,0.5)")
    return _dark(fig, title="Budget Redistribution - Limit Adjustments (Δ AMD)",
                 xaxis_tickangle=-30, yaxis_title=f"Adjustment ({CURRENCY})",
                 height=400)


def delta_pct_bar(df: pd.DataFrame) -> go.Figure:
    sorted_df = df.sort_values("delta_pct")
    colours = [C_OPTIMIZED if d >= 0 else C_NEGATIVE for d in sorted_df["delta_pct"]]
    fig = go.Figure(go.Bar(
        x=sorted_df["delta_pct"], y=sorted_df["service_name"], orientation="h",
        marker_color=colours,
        text=[f"{d:+.2f}%" for d in sorted_df["delta_pct"]],
        textposition="outside",
        textfont=dict(color=C_LIGHT),
    ))
    fig.add_vline(x=0, line_color="rgba(84,84,84,0.5)")
    return _dark(fig, title="Percentage Change in Limits",
                 xaxis=dict(title="Δ%", range=[-8, 8],
                            gridcolor="rgba(84,84,84,0.3)",
                            tickfont=dict(color=C_NEUTRAL),
                            linecolor="rgba(84,84,84,0.5)"),
                 yaxis_title="", height=400)


# ── Risk / Cost Tradeoff ──────────────────────────────────────────────────────

def lambda_sweep_chart(sweep_df: pd.DataFrame, selected_lambda: float = 0.01) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sweep_df["lambda"], y=sweep_df["expected_M"],
        mode="lines+markers", name="Expected Payout (M AMD)",
        line=dict(color=C_PRIMARY, width=2),
        marker=dict(size=7, color=C_PRIMARY),
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=sweep_df["lambda"], y=sweep_df["variance_M"],
        mode="lines+markers", name="Variance (M AMD)",
        line=dict(color=C_SECONDARY, width=2, dash="dash"),
        marker=dict(size=7, color=C_SECONDARY),
        yaxis="y2",
    ))
    fig.add_vline(
        x=selected_lambda, line_dash="dot", line_color=C_OPTIMIZED,
        annotation_text=f"λ={selected_lambda}",
        annotation_font_color=C_OPTIMIZED,
    )
    return _dark(fig,
                 title="Expected Payout & Variance vs Risk-Aversion Parameter (λ)",
                 xaxis=dict(title="Lambda (λ)", type="log",
                            gridcolor="rgba(84,84,84,0.3)",
                            tickfont=dict(color=C_NEUTRAL),
                            linecolor="rgba(84,84,84,0.5)"),
                 yaxis=dict(title="Expected Payout (M AMD)",
                            title_font=dict(color=C_PRIMARY),
                            gridcolor="rgba(84,84,84,0.3)",
                            tickfont=dict(color=C_NEUTRAL),
                            linecolor="rgba(84,84,84,0.5)"),
                 yaxis2=dict(title="Variance (M AMD)",
                             title_font=dict(color=C_SECONDARY),
                             overlaying="y", side="right",
                             gridcolor="rgba(84,84,84,0.3)",
                             tickfont=dict(color=C_NEUTRAL),
                             linecolor="rgba(84,84,84,0.5)"),
                 height=420, legend=dict(orientation="h", y=1.12))


def efficient_frontier_chart(sweep_df: pd.DataFrame, selected_lambda: float = 0.01) -> go.Figure:
    sel_row = sweep_df.iloc[(np.abs(np.log10(sweep_df["lambda"]) - np.log10(selected_lambda))).argmin()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sweep_df["variance_M"], y=sweep_df["expected_M"],
        mode="lines+markers",
        marker=dict(size=10, color=sweep_df["lambda"],
                    colorscale=[[0, C_PRIMARY], [1, C_CHART_5]],
                    showscale=True,
                    colorbar=dict(title=dict(text="λ", font=dict(color=C_LIGHT)),
                                  tickfont=dict(color=C_NEUTRAL))),
        line=dict(color="rgba(64,242,154,0.3)", width=1),
        name="Scenarios",
        hovertemplate="λ=%{marker.color:.2e}<br>Payout=%{y:.3f}M<br>Var=%{x:.3f}M",
    ))
    fig.add_trace(go.Scatter(
        x=[sel_row["variance_M"]], y=[sel_row["expected_M"]],
        mode="markers", name="Selected λ",
        marker=dict(color=C_OPTIMIZED, size=16, symbol="star",
                    line=dict(color=C_BG, width=2)),
    ))
    return _dark(fig, title="Efficient Frontier: Cost vs Risk",
                 xaxis_title="Variance (M AMD)",
                 yaxis_title="Expected Payout (M AMD)",
                 height=420)


# ── Validation ────────────────────────────────────────────────────────────────

def monte_carlo_distribution(differences: list[float]) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=differences, nbinsx=20, marker_color=C_PRIMARY, opacity=0.8,
        name="Simulation outcomes",
    ))
    mean_d = np.mean(differences)
    fig.add_vline(x=0, line_dash="dash", line_color=C_CHART_5,
                  annotation_text="No change", annotation_font_color=C_NEUTRAL)
    fig.add_vline(x=mean_d, line_dash="dot", line_color=C_OPTIMIZED,
                  annotation_text=f"Mean Δ={_fmt(mean_d)} {CURRENCY}",
                  annotation_font_color=C_OPTIMIZED)
    return _dark(fig, title="Distribution of Reimbursement Change Across 100 Simulations",
                 xaxis_title=f"Change in Reimbursement ({CURRENCY})",
                 yaxis_title="Frequency", height=380)


def monte_carlo_scatter(orig: list[float], adj: list[float]) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Box(y=orig, name="Original Limits",
                         marker_color=C_CHART_5, line_color=C_NEUTRAL))
    fig.add_trace(go.Box(y=adj,  name="Optimised Limits",
                         marker_color=C_PRIMARY, line_color=C_PRIMARY))
    return _dark(fig, title="Total Reimbursement Distribution Across 100 Simulations",
                 yaxis_title=f"Total Reimbursement ({CURRENCY})", height=380)


# ── Service Drilldown ─────────────────────────────────────────────────────────

def service_reimbursement_curve(
    c_ij: np.ndarray, p_ij: np.ndarray,
    original_limit: float, optimized_limit: float,
    service_name: str,
) -> go.Figure:
    T_vals = np.linspace(c_ij.min() * 0.5, c_ij.max() * 1.1, 200)
    curve  = np.array([np.sum(p_ij * np.minimum(c_ij, T)) for T in T_vals])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=T_vals, y=curve, mode="lines", name="E[min(claim, T)]",
        line=dict(color=C_PRIMARY, width=2),
        fill="tozeroy", fillcolor="rgba(64,242,154,0.08)",
    ))
    fig.add_vline(x=original_limit, line_dash="dash", line_color=C_NEGATIVE,
                  annotation_text=f"Original ({_fmt(original_limit)})",
                  annotation_font_color=C_NEGATIVE)
    fig.add_vline(x=optimized_limit, line_dash="dot", line_color=C_OPTIMIZED,
                  annotation_text=f"Optimised ({_fmt(optimized_limit)})",
                  annotation_font_color=C_OPTIMIZED)
    return _dark(fig, title=f"Expected Reimbursement Curve - {service_name}",
                 xaxis_title=f"Limit T ({CURRENCY})",
                 yaxis_title=f"Expected Reimbursement ({CURRENCY})", height=350)
