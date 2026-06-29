import streamlit as st

from src.data_loader import load_lambda_sweep, load_precomputed_scenarios
from src.optimization import lambda_sweep_dataframe
from src.visualizations import efficient_frontier_chart, lambda_sweep_chart

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Risk / Cost Tradeoff", page_icon=str(_ASSETS / "Kinetix_symbol_green.ico"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("⚖️ Risk / Cost Tradeoff")
st.caption("Understand the λ risk dial - how risk-aversion shapes the optimised limits.")
st.divider()

scenarios  = load_precomputed_scenarios()
sweep_df   = lambda_sweep_dataframe(scenarios)

# ── risk dial explanation ──────────────────────────────────────────────────────
col_exp, col_dial = st.columns([3, 2])

with col_exp:
    st.subheader("The Risk Dial")
    st.markdown(
        """
Think of **λ (lambda)** as a dial that controls what the model prioritises:

| λ setting | Actuarial posture | What changes |
|---|---|---|
| **Very low** (≤ 1e-5) | Pure cost minimisation | Model aggressively cuts limits to reduce average payout |
| **Low–medium** (~1e-3) | Cost-leaning balanced | Moderate savings, accepts some variance |
| **Medium** (~1e-2) | **Balanced** *(selected)* | Reduces both expected cost and variance proportionally |
| **High** (~1e-1) | Stability-leaning | Prioritises predictability; limits move less |
| **Very high** (≥ 1) | Pure variance minimisation | Model barely moves limits; maximises stability |

**For most insurers:** A balanced λ ≈ 0.01 is a reasonable starting point. It achieves
meaningful cost improvement while keeping reimbursement patterns stable - which matters
for reserve planning and regulatory reporting.
        """
    )

with col_dial:
    st.subheader("Selected scenario")
    selected_lambda = st.select_slider(
        "λ (risk-aversion)",
        options=[1e-7, 1e-6, 1e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 1e0],
        value=1e-2,
        format_func=lambda v: f"{v:.0e}",
    )
    if selected_lambda <= 1e-5:
        st.error("🔴 Cost-Focused")
        st.markdown("Maximises savings. Higher risk of variance.")
    elif selected_lambda <= 5e-3:
        st.warning("🟡 Balanced (cost-leaning)")
        st.markdown("Good savings with moderate stability.")
    elif selected_lambda <= 5e-2:
        st.success("🟢 Balanced")
        st.markdown("Recommended for most actuarial use cases.")
    else:
        st.info("🔵 Stability-Focused")
        st.markdown("Prioritises predictability over cost savings.")

st.divider()

# ── charts ─────────────────────────────────────────────────────────────────────
if sweep_df is not None:
    st.subheader("Lambda Sensitivity Analysis")
    st.plotly_chart(
        lambda_sweep_chart(sweep_df, selected_lambda=selected_lambda),
        use_container_width=True,
    )
    st.plotly_chart(
        efficient_frontier_chart(sweep_df, selected_lambda=selected_lambda),
        use_container_width=True,
    )

    from src.components import info_block
    info_block("How to read the efficient frontier",
        "Each point represents one λ value.<br><br>"
        "<strong>Moving left</strong> on the x-axis (lower variance) = more stability-focused.<br>"
        "<strong>Moving down</strong> on the y-axis (lower expected payout) = lower average cost.<br><br>"
        "The ideal point is the <strong>bottom-left</strong> - but there is always a trade-off. "
        "The selected λ is shown as a star ⭐."
    )
else:
    st.warning(
        "⚠️  Lambda sweep data not available. "
        "Run `python precompute_scenarios.py` to generate the sensitivity analysis data."
    )
    st.markdown(
        """
### What the sensitivity analysis shows (summary from notebook experiments)

From `experiments.ipynb`, running the solver across λ ∈ [10⁻⁷, 10¹] reveals:

- **Low λ regime** (≤ 10⁻⁵): Expected reimbursement decreases noticeably as the model
  aggressively cuts limits for underused services.
- **Transition zone** (~10⁻⁵ to 10⁻²): The model balances cost and variance. This is
  where the most practically useful solutions lie.
- **High λ regime** (≥ 10⁻¹): Variance is strongly suppressed; limit adjustments shrink
  toward zero as stability takes priority.

**Key finding from fine-grained analysis:** The transition point where variance starts
to dominate occurs around λ ≈ 10⁻⁵. Our selected λ = 0.01 lies well within the balanced
zone, achieving a meaningful 0.22% cost reduction with stable reimbursement patterns.
        """
    )
