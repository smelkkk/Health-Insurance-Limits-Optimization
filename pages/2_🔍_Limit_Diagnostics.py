import streamlit as st

from src.config import CURRENCY
from src.data_loader import build_service_summary, load_optimization_inputs, load_service_claims
from src.metrics import limit_diagnostics
from src.visualizations import binding_rate_chart, claim_distribution_vs_limit

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Limit Diagnostics", page_icon=str(_ASSETS / "favicon.png"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("🔍 Current Limit Diagnostics")
st.caption("Analyse whether existing limits are binding, underused, or well-calibrated.")
st.divider()

claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
summary    = build_service_summary(claims, opt_inputs)
diag       = limit_diagnostics(summary)

# ── diagnostic legend ──────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; gap:12px; margin-bottom:8px; flex-wrap:wrap;">
  <div style="flex:1; min-width:140px; background:rgba(220,80,80,0.1); border:1px solid rgba(220,80,80,0.3);
              border-radius:10px; padding:16px; font-family:Inter,sans-serif;">
    <div style="color:rgb(220,80,80); font-weight:600; font-size:13px; margin-bottom:4px;">🔴 Highly Binding</div>
    <div style="color:rgb(161,161,161); font-size:12px;">&gt;70% of claims reach the limit.</div>
  </div>
  <div style="flex:1; min-width:140px; background:rgba(240,190,0,0.08); border:1px solid rgba(240,190,0,0.3);
              border-radius:10px; padding:16px; font-family:Inter,sans-serif;">
    <div style="color:rgb(240,190,0); font-weight:600; font-size:13px; margin-bottom:4px;">🟡 Moderately Binding</div>
    <div style="color:rgb(161,161,161); font-size:12px;">40–70% of claims reach the limit.</div>
  </div>
  <div style="flex:1; min-width:140px; background:rgba(128,128,128,0.08); border:1px solid rgba(128,128,128,0.3);
              border-radius:10px; padding:16px; font-family:Inter,sans-serif;">
    <div style="color:rgb(161,161,161); font-weight:600; font-size:13px; margin-bottom:4px;">⚪ Underused Limit</div>
    <div style="color:rgb(128,128,128); font-size:12px;">Mean claim &lt;30% of limit.</div>
  </div>
  <div style="flex:1; min-width:140px; background:rgba(64,242,154,0.06); border:1px solid rgba(64,242,154,0.3);
              border-radius:10px; padding:16px; font-family:Inter,sans-serif;">
    <div style="color:rgb(64,242,154); font-weight:600; font-size:13px; margin-bottom:4px;">🟢 Well Calibrated</div>
    <div style="color:rgb(161,161,161); font-size:12px;">Appropriate binding and distribution.</div>
  </div>
  <div style="flex:1; min-width:140px; background:rgba(51,51,51,0.3); border:1px solid rgba(84,84,84,0.5);
              border-radius:10px; padding:16px; font-family:Inter,sans-serif;">
    <div style="color:rgb(209,209,209); font-weight:600; font-size:13px; margin-bottom:4px;">⬜ Insufficient Data</div>
    <div style="color:rgb(128,128,128); font-size:12px;">&lt;5 claims. Unreliable.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── binding rate chart ─────────────────────────────────────────────────────────
st.subheader("Binding Rate by Service")
st.plotly_chart(binding_rate_chart(diag), use_container_width=True)

# ── diagnostics table ──────────────────────────────────────────────────────────
st.subheader("Detailed Diagnostics")
display = diag[[
    "service_name", "diagnostic", "n_claims", "original_limit",
    "mean_claim", "binding_rate", "pct_below_limit", "epsilon",
]].rename(columns={
    "service_name":    "Service",
    "diagnostic":      "Status",
    "n_claims":        "# Claims",
    "original_limit":  f"Current Limit ({CURRENCY})",
    "mean_claim":      f"Mean Claim ({CURRENCY})",
    "binding_rate":    "Binding Rate%",
    "pct_below_limit": "% Below Limit",
    "epsilon":         "Adaptive ε",
})

COLOUR_MAP = {
    "Highly Binding":    "background-color: rgba(220,80,80,0.12); color: rgb(220,80,80)",
    "Moderately Binding": "background-color: rgba(240,190,0,0.12); color: rgb(240,190,0)",
    "Underused Limit":   "background-color: rgba(128,128,128,0.1); color: rgb(161,161,161)",
    "Well Calibrated":   "background-color: rgba(64,242,154,0.1); color: rgb(64,242,154)",
    "Insufficient Data": "background-color: rgba(51,51,51,0.3); color: rgb(128,128,128)",
}

def _row_colour(row):
    colour = COLOUR_MAP.get(row["Status"], "")
    return [colour] * len(row)

st.dataframe(
    display.style
        .apply(_row_colour, axis=1)
        .format({
            f"Current Limit ({CURRENCY})": "{:,.0f}",
            f"Mean Claim ({CURRENCY})":    "{:,.0f}",
            "Binding Rate%":               "{:.0f}%",
            "% Below Limit":               "{:.0f}%",
            "Adaptive ε":                  "{:.3f}",
        }),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "**Adaptive ε** is the maximum allowed adjustment as a fraction of the current limit. "
    "It decreases as claim count increases, reflecting greater statistical confidence in the data."
)

st.divider()

# ── per-service claim distributions ───────────────────────────────────────────
st.subheader("Claim Distributions vs Current Limits")
st.markdown("Select services to inspect their claim histogram relative to the current limit.")

selected = st.multiselect(
    "Choose services",
    options=list(claims.keys()),
    default=list(claims.keys())[:3],
    format_func=lambda i: f"Service {i} - {claims[i]['service_name'].iloc[0]}",
)

for idx in selected:
    df      = claims[idx]
    name    = df["service_name"].iloc[0]
    limit   = int(df["limit"].iloc[0])
    n       = len(df)
    binding = (df["ClaimedAmount"] >= limit).mean() * 100

    with st.container():
        st.plotly_chart(
            claim_distribution_vs_limit(df, limit, name),
            use_container_width=True,
        )
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Claims",       f"{n}")
        m2.metric("Binding",      f"{binding:.0f}%")
        m3.metric("Mean Claim",   f"{df['ClaimedAmount'].mean():,.0f}")
        m4.metric("Max Claim",    f"{df['ClaimedAmount'].max():,.0f}")
        if binding > 70:
            m5.error("Highly binding")
        elif binding > 40:
            m5.warning("Moderate")
        else:
            m5.success("Low binding")
    st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
