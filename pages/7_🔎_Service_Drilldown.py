import numpy as np
import streamlit as st

from src.config import CURRENCY, OPTIMIZED_LIMITS, ORIGINAL_LIMITS, SERVICE_NAMES
from src.data_loader import build_service_summary, load_optimization_inputs, load_service_claims
from src.metrics import compute_reimbursement_curve
from src.visualizations import claim_distribution_vs_limit, service_reimbursement_curve

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Service Drilldown", page_icon=str(_ASSETS / "favicon.png"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("🔎 Service Drilldown")
st.caption("Deep-dive into any single service: distribution, diagnostics, and model rationale.")
st.divider()

claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
summary    = build_service_summary(claims, opt_inputs)

# ── service selector ───────────────────────────────────────────────────────────
service_options = {i: f"Service {i} - {SERVICE_NAMES[i]}" for i in sorted(claims.keys())}
selected_id = st.selectbox(
    "Select a service",
    options=list(service_options.keys()),
    format_func=lambda i: service_options[i],
    index=7,  # default to Service 8 (highest volume)
)

df      = claims[selected_id]
s       = summary[summary["service_id"] == selected_id].iloc[0]
inp     = opt_inputs[selected_id - 1]
orig    = ORIGINAL_LIMITS[selected_id]
opt     = OPTIMIZED_LIMITS[selected_id]
name    = SERVICE_NAMES[selected_id]

st.divider()

# ── header metrics ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Original",     f"{orig/1e3:,.0f}K")
c2.metric("Optimised",    f"{opt/1e3:,.0f}K",
          delta=f"{opt-orig:+,.0f}", delta_color="normal")
c3.metric("Claims",       f"{int(s['n_claims'])}")
c4.metric("Binding",      f"{s['binding_rate']:.0f}%")
c5.metric("Mean",   f"{s['mean_claim']/1e3:,.0f}K")
c6.metric("Max",    f"{s['max_claim']/1e3:,.0f}K")

# ── diagnostic badge ───────────────────────────────────────────────────────────
binding = s["binding_rate"]
if s["n_claims"] < 5:
    st.warning("⚠️ Insufficient data - fewer than 5 claims. Treat results with caution.")
elif binding > 70:
    st.error(f"🔴 **Highly Binding** - {binding:.0f}% of claims hit the current limit.")
elif binding > 40:
    st.warning(f"🟡 **Moderately Binding** - {binding:.0f}% of claims hit the current limit.")
elif s["mean_claim"] < 0.3 * orig:
    st.info(f"⚪ **Underused Limit** - mean claim is only {s['mean_claim']/orig*100:.0f}% of the limit.")
else:
    st.success("🟢 **Well Calibrated** - binding rate and claim distribution look appropriate.")

st.divider()

# ── main charts ────────────────────────────────────────────────────────────────
col_hist, col_curve = st.columns(2)

with col_hist:
    st.subheader("Claim Distribution vs Current Limit")
    st.plotly_chart(
        claim_distribution_vs_limit(df, orig, name),
        use_container_width=True,
    )

with col_curve:
    st.subheader("Expected Reimbursement Curve")
    st.plotly_chart(
        service_reimbursement_curve(inp["c_ij"], inp["p_ij"], orig, opt, name),
        use_container_width=True,
    )
    st.caption(
        "The curve shows expected reimbursement E[min(claim, T)] as a function of limit T. "
        "The red dashed line = current limit. Green dotted = optimised limit."
    )

st.divider()

# ── distribution stats ─────────────────────────────────────────────────────────
st.subheader("Claim Statistics")
claims_series = df["ClaimedAmount"]
col_s1, col_s2 = st.columns(2)

with col_s1:
    stats = {
        "Mean":      f"{claims_series.mean():,.0f}",
        "Median":    f"{claims_series.median():,.0f}",
        "Std dev":   f"{claims_series.std():,.0f}",
        "Min":       f"{claims_series.min():,.0f}",
        "Max":       f"{claims_series.max():,.0f}",
        "P25":       f"{claims_series.quantile(0.25):,.0f}",
        "P75":       f"{claims_series.quantile(0.75):,.0f}",
        "P90":       f"{claims_series.quantile(0.90):,.0f}",
    }
    for k, v in stats.items():
        st.markdown(f"**{k}:** {v} {CURRENCY}")

with col_s2:
    pct_below = (claims_series < orig).mean() * 100
    pct_above = (claims_series > orig).mean() * 100
    pct_at    = 100 - pct_below - pct_above

    st.markdown(f"**% claims below limit:** {pct_below:.0f}%")
    st.markdown(f"**% claims at limit:**    {pct_at:.0f}%")
    st.markdown(f"**% claims above limit:** {pct_above:.0f}%")
    st.divider()
    expected_orig = compute_reimbursement_curve(inp["c_ij"], inp["p_ij"], np.array([orig]))[0]
    expected_opt  = compute_reimbursement_curve(inp["c_ij"], inp["p_ij"], np.array([opt]))[0]
    st.markdown(f"**E[reimb] at original limit:**  {expected_orig:,.0f} {CURRENCY}")
    st.markdown(f"**E[reimb] at optimised limit:** {expected_opt:,.0f} {CURRENCY}")
    st.markdown(f"**Change in E[reimb]:** {expected_opt - expected_orig:+,.0f} {CURRENCY}")

st.divider()

# ── raw data ───────────────────────────────────────────────────────────────────
st.markdown("""
    <div style="color:rgb(64,242,154); font-size:12px; font-weight:600;
                text-transform:uppercase; letter-spacing:0.08em;
                margin:16px 0 12px; font-family:Inter,sans-serif;">
      📋 Raw claim data
    </div>
""", unsafe_allow_html=True)
st.dataframe(
    df[["Personid", "ClaimedAmount", "TotalApprovedAmount"]].rename(columns={
        "Personid":           "Person ID",
        "ClaimedAmount":      f"Claimed ({CURRENCY})",
        "TotalApprovedAmount": f"Approved ({CURRENCY})",
    }).style.format({
        f"Claimed ({CURRENCY})":  "{:,.0f}",
        f"Approved ({CURRENCY})": "{:,.0f}",
    }),
    use_container_width=True,
    hide_index=True,
)
