"""
Health Insurance Limit Optimisation Dashboard
ESADE MiBA Capstone | In collaboration with KinetiX
"""

from pathlib import Path

import streamlit as st

from src.config import CURRENCY
from src.data_loader import (
    build_service_summary,
    load_optimization_inputs,
    load_optimized_limits,
    load_service_claims,
)
from src.metrics import portfolio_kpis
from src.components import (
    ICONS, divider, page_header, section_header, render_kpi_row,
    render_sidebar_brand, render_sidebar_footer, render_metadata_bar,
)

ASSETS = Path(__file__).parent / "assets"

st.set_page_config(
    page_title="KinetiX · Insurance Limit Optimiser",
    page_icon=str(ASSETS / "favicon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── inject CSS ────────────────────────────────────────────────────────────────
css_path = ASSETS / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_brand()
    render_sidebar_footer()

# ── load data ─────────────────────────────────────────────────────────────────
claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
opt_limits = load_optimized_limits()
summary    = build_service_summary(claims, opt_inputs)
kpis       = portfolio_kpis(summary)

# ── hero header ───────────────────────────────────────────────────────────────
page_header(
    "Health Insurance Limit Optimisation",
    "Data-driven reimbursement limit optimisation across medical service groups",
    "Dashboard",
)
render_metadata_bar()

# ── executive KPIs ────────────────────────────────────────────────────────────
section_header("OVERVIEW", "Executive Summary",
               "Key performance indicators from the optimisation engine")

render_kpi_row([
    {"icon": ICONS["services"],  "label": "Services Analysed",
     "value": f"{kpis['n_services']}"},
    {"icon": ICONS["chart"],     "label": "Total Claims",
     "value": f"{kpis['total_claims']:,}"},
    {"icon": ICONS["money"],     "label": "Current Reimbursement",
     "value": f"{kpis['total_current_reimb']/1e6:.2f}M"},
    {"icon": ICONS["check"],     "label": "Optimised Reimbursement",
     "value": f"{kpis['total_opt_reimb']/1e6:.2f}M",
     "delta": f"-{kpis['saving_amd']/1e6:.3f}M", "positive": True},
    {"icon": ICONS["target"],    "label": "Expected Saving",
     "value": f"{kpis['saving_amd']:,.0f}",
     "delta": f"{kpis['saving_pct']:.2f}%", "positive": True},
])

divider()

# ── what this tool does ───────────────────────────────────────────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown("""
        <h3 style="color:rgb(255,255,255); font-family:Inter,sans-serif;
                   font-weight:500; margin-bottom:16px;">
          What this tool helps with
        </h3>
    """, unsafe_allow_html=True)
    st.markdown(
        """
This dashboard supports insurance actuaries, pricing teams, and management in making
data-driven decisions about reimbursement limits across medical service groups.

**Key capabilities:**

- **Data Overview** — understand claim volumes and cost concentration across services
- **Limit Diagnostics** — identify where current limits are over-funded, binding, or misaligned
- **Scenario Runner** — explore how different risk-aversion levels change the optimised limits
- **Before vs After** — compare original and optimised limits with plain-language explanations
- **Risk / Cost Tradeoff** — understand the λ "risk dial" and the efficient frontier
- **Monte Carlo Validation** — evidence that results hold under simulated claim uncertainty
- **Service Drilldown** — deep-dive into any single service
- **Recommendations** — prioritised, plain-language action items for each service
- **Export** — download results in CSV, Excel, or text summary format
        """
    )

with col_b:
    st.markdown("""
        <h3 style="color:rgb(255,255,255); font-family:Inter,sans-serif;
                   font-weight:500; margin-bottom:16px;">
          Model at a glance
        </h3>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div style="
          background: rgb(13,13,13);
          border: 1px solid rgba(84,84,84,0.5);
          border-radius: 12px;
          padding: 24px;
          font-family: Inter, sans-serif;
          margin-bottom: 16px;
        ">
          <div style="color:rgb(161,161,161); font-size:14px; line-height:2;">
            <strong style="color:rgb(255,255,255);">Model:</strong> MIQP (Gurobi 13)<br/>
            <strong style="color:rgb(255,255,255);">Objective:</strong> E[reimb] + λ × Var<br/>
            <strong style="color:rgb(255,255,255);">Constraint:</strong> Σ δᵢ = 0 (budget-neutral)<br/>
            <strong style="color:rgb(255,255,255);">Bounds:</strong> εᵢ = min(5%, 0.4/√n)<br/>
            <strong style="color:rgb(255,255,255);">λ:</strong> 0.01 (Balanced)
          </div>
        </div>
        <div style="
          background: rgb(30,59,12);
          border: 1px solid rgba(64,242,154,0.3);
          border-radius: 12px;
          padding: 16px 20px;
          font-family: Inter, sans-serif;
          color: rgb(64,242,154);
          font-size: 14px;
          font-weight: 500;
        ">
          Budget-neutral adjustment achieved a {kpis['saving_pct']:.2f}% saving
          ({kpis['saving_amd']:,.0f} {CURRENCY}) with no change to total limit budget.
        </div>
    """, unsafe_allow_html=True)

divider()

# ── portfolio snapshot ────────────────────────────────────────────────────────
section_header("PORTFOLIO", "Portfolio Snapshot",
               "Per-service limits, adjustments, and binding rates")

display = summary[[
    "service_name", "original_limit", "optimized_limit",
    "delta", "delta_pct", "n_claims", "binding_rate",
]].rename(columns={
    "service_name":    "Service",
    "original_limit":  f"Original Limit ({CURRENCY})",
    "optimized_limit": f"Optimised Limit ({CURRENCY})",
    "delta":           f"Δ ({CURRENCY})",
    "delta_pct":       "Δ%",
    "n_claims":        "# Claims",
    "binding_rate":    "Binding Rate%",
})


def _colour_delta(val):
    if isinstance(val, (float, int)):
        c = "rgb(64,242,154)" if val > 0 else ("rgb(220,80,80)" if val < 0 else "rgb(128,128,128)")
        return f"color: {c}"
    return ""


st.dataframe(
    display.style
        .format({
            f"Original Limit ({CURRENCY})":  "{:,.0f}",
            f"Optimised Limit ({CURRENCY})": "{:,.0f}",
            f"Δ ({CURRENCY})":               "{:+,.0f}",
            "Δ%":                            "{:+.2f}%",
            "Binding Rate%":                 "{:.0f}%",
        })
        .map(_colour_delta, subset=[f"Δ ({CURRENCY})", "Δ%"]),
    use_container_width=True,
    hide_index=True,
)

st.markdown("""
    <p style="color:rgb(128,128,128); font-size:12px; font-family:Inter,sans-serif;
              margin-top:8px;">
      Binding Rate = % of historical claims that reached or exceeded the current limit.
      Higher binding rate → limit is a real constraint for policyholders.
    </p>
""", unsafe_allow_html=True)
