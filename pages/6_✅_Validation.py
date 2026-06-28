import numpy as np
import streamlit as st

from src.config import CURRENCY, OPTIMIZED_LIMITS, ORIGINAL_LIMITS
from src.data_loader import load_monte_carlo, load_optimization_inputs, load_service_claims
from src.visualizations import monte_carlo_distribution, monte_carlo_scatter

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Validation", page_icon=str(_ASSETS / "favicon.png"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("✅ Validation & Simulation")
st.caption("Evidence that optimised limits outperform original limits under simulated uncertainty.")
st.divider()

st.info(
    "**Interpretation note:** The following validation uses Monte Carlo simulation - "
    "randomly drawing claim samples from the empirical distributions. "
    "This provides *evidence in favour of* the optimised limits, not a guarantee. "
    "Results depend on the quality and representativeness of historical claim data."
)

claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
mc_data    = load_monte_carlo()

# ── run or load Monte Carlo ────────────────────────────────────────────────────
@st.cache_data(show_spinner="Running Monte Carlo simulation…")
def run_monte_carlo(n_sims: int = 100, seed: int = 42) -> dict:
    rng        = np.random.default_rng(seed)
    orig_lims  = [ORIGINAL_LIMITS[i]   for i in sorted(ORIGINAL_LIMITS)]
    opt_lims   = [OPTIMIZED_LIMITS[i]  for i in sorted(OPTIMIZED_LIMITS)]
    inputs     = opt_inputs  # from outer scope via closure

    orig_totals, adj_totals = [], []

    for _ in range(n_sims):
        orig_total = adj_total = 0.0
        for i, service in enumerate(inputs):
            c_ij  = service["c_ij"]
            p_ij  = service["p_ij"]
            n_obs = len(list(claims.values())[i])
            sampled = rng.choice(c_ij, size=n_obs, p=p_ij)
            orig_total += np.clip(sampled, None, orig_lims[i]).sum()
            adj_total  += np.clip(sampled, None, opt_lims[i]).sum()
        orig_totals.append(float(orig_total))
        adj_totals.append(float(adj_total))

    diffs = [a - o for a, o in zip(adj_totals, orig_totals)]
    return {
        "n_simulations":    n_sims,
        "original_totals":  orig_totals,
        "adjusted_totals":  adj_totals,
        "differences":      diffs,
        "mean_difference":  float(np.mean(diffs)),
        "std_difference":   float(np.std(diffs)),
    }


# ── controls ───────────────────────────────────────────────────────────────────
col_ctrl, col_info = st.columns([1, 2])
with col_ctrl:
    n_sims  = st.slider("Number of simulations", 50, 500, 100, 50)
    run_btn = st.button("▶  Run simulation", type="primary")

if mc_data and not run_btn:
    result = mc_data
    st.caption("Loaded from precomputed file (data/precomputed/monte_carlo.json).")
else:
    result = run_monte_carlo(n_sims=n_sims)

# ── KPI summary ────────────────────────────────────────────────────────────────
mean_d = result["mean_difference"]
std_d  = result["std_difference"]
orig_m = np.mean(result["original_totals"])
adj_m  = np.mean(result["adjusted_totals"])

with col_info:
    c1, c2, c3 = st.columns(3)
    c1.metric("Mean Δ Reimb.",
              f"{mean_d:,.0f}",
              delta=f"{mean_d/orig_m*100:.2f}%")
    c2.metric("Std Deviation", f"{std_d:,.0f}")
    c3.metric("Simulations",   f"{result['n_simulations']}")

pct_favourable = sum(1 for d in result["differences"] if d <= 0) / len(result["differences"]) * 100
st.success(
    f"✅  In **{pct_favourable:.0f}%** of simulations, optimised limits resulted in equal or lower "
    f"total reimbursement than original limits. Mean saving: **{abs(mean_d):,.0f} {CURRENCY}** per period."
)

st.divider()

# ── charts ─────────────────────────────────────────────────────────────────────
st.subheader("Simulation Results")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        monte_carlo_distribution(result["differences"]),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        monte_carlo_scatter(result["original_totals"], result["adjusted_totals"]),
        use_container_width=True,
    )

st.divider()

# ── methodology note ───────────────────────────────────────────────────────────
from src.components import info_block
info_block("Simulation methodology",
    "<strong>How the Monte Carlo simulation works:</strong><br><br>"
    "1. For each simulation run, claims are sampled randomly from the empirical "
    "distribution (bin centres and probabilities) for each service.<br>"
    "2. Total reimbursement is computed under both the <strong>original limits</strong> "
    "and the <strong>optimised limits</strong> using a simple min(claim, limit) rule.<br>"
    "3. The <strong>difference</strong> (optimised − original) is recorded for each run.<br>"
    f"4. After {result['n_simulations']} runs, the distribution of differences is analysed.<br><br>"
    "<strong>What this tells us:</strong><br>"
    "A distribution centred below zero provides evidence that the optimised limits "
    "reduce total reimbursement across a range of claim scenarios - not just the observed "
    "historical data.<br><br>"
    "<strong>Limitations:</strong><br>"
    "• Simulation assumes claim amounts are drawn independently per service.<br>"
    "• Correlation between services is not modelled.<br>"
    "• Results depend on future claim distributions resembling historical ones."
)
