import streamlit as st

from src.config import CURRENCY
from src.data_loader import build_service_summary, load_optimization_inputs, load_service_claims
from src.optimization import fallback_balanced_dataframe
from src.visualizations import delta_pct_bar, delta_waterfall, limits_comparison_bar

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Before vs After", page_icon=str(_ASSETS / "favicon.png"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("📈 Before vs After Comparison")
st.caption("Compare original and optimised limits — with plain-language explanations.")
st.divider()

claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
summary    = build_service_summary(claims, opt_inputs)
df         = fallback_balanced_dataframe()

# ── top-level metrics ──────────────────────────────────────────────────────────
total_orig  = summary["total_reimbursed_original"].sum()
total_opt   = summary["total_reimbursed_optimized"].sum()
saving      = total_orig - total_opt

c1, c2, c3, c4 = st.columns(4)
c1.metric("Original Total Reimbursement",  f"{total_orig/1e6:.3f} M {CURRENCY}")
c2.metric("Optimised Total Reimbursement", f"{total_opt/1e6:.3f} M {CURRENCY}",
          delta=f"-{saving/1e6:.3f} M {CURRENCY}")
c3.metric("Saving",                        f"{saving:,.0f} {CURRENCY}")
c4.metric("Saving %",                      f"{saving/total_orig*100:.2f}%")

st.divider()

# ── charts ─────────────────────────────────────────────────────────────────────
tab_charts, tab_table, tab_interp = st.tabs(["📈 Charts", "📋 Full Table", "💬 Interpretation"])

with tab_charts:
    st.plotly_chart(limits_comparison_bar(df), use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(delta_waterfall(df), use_container_width=True)
    with col2:
        st.plotly_chart(delta_pct_bar(df), use_container_width=True)

with tab_table:
    merged = df.merge(
        summary[["service_id", "n_claims", "binding_rate",
                 "total_reimbursed_original", "total_reimbursed_optimized"]],
        on="service_id",
    )
    merged["reimb_delta"] = merged["total_reimbursed_optimized"] - merged["total_reimbursed_original"]

    display = merged[[
        "service_name", "original_limit", "adjusted_limit", "delta", "delta_pct",
        "n_claims", "binding_rate", "total_reimbursed_original",
        "total_reimbursed_optimized", "reimb_delta",
    ]].rename(columns={
        "service_name":              "Service",
        "original_limit":            f"Original Limit",
        "adjusted_limit":            f"Optimised Limit",
        "delta":                     f"Limit Δ ({CURRENCY})",
        "delta_pct":                 "Limit Δ%",
        "n_claims":                  "# Claims",
        "binding_rate":              "Binding%",
        "total_reimbursed_original": f"Reimbursed Original ({CURRENCY})",
        "total_reimbursed_optimized":f"Reimbursed Optimised ({CURRENCY})",
        "reimb_delta":               f"Reimbursement Δ ({CURRENCY})",
    })

    def _delta_colour(val):
        if isinstance(val, (int, float)):
            return f"color: {'rgb(64,242,154)' if val > 0 else 'rgb(220,80,80)' if val < 0 else 'rgb(128,128,128)'}"
        return ""

    st.dataframe(
        display.style
            .format({
                "Original Limit":              "{:,.0f}",
                "Optimised Limit":             "{:,.0f}",
                f"Limit Δ ({CURRENCY})":       "{:+,.0f}",
                "Limit Δ%":                    "{:+.2f}%",
                "Binding%":                    "{:.0f}%",
                f"Reimbursed Original ({CURRENCY})":  "{:,.0f}",
                f"Reimbursed Optimised ({CURRENCY})": "{:,.0f}",
                f"Reimbursement Δ ({CURRENCY})":      "{:+,.0f}",
            })
            .map(_delta_colour, subset=[f"Limit Δ ({CURRENCY})", "Limit Δ%", f"Reimbursement Δ ({CURRENCY})"]),
        use_container_width=True,
        hide_index=True,
    )

with tab_interp:
    st.subheader("Why does each limit go up or down?")
    st.markdown(
        """
The optimiser simultaneously pursues two goals: **reduce expected payout** and
**reduce variance** of reimbursements. The direction of each adjustment reflects
where claims fall relative to the current limit.
        """
    )

    increases = df[df["delta"] > 0].sort_values("delta", ascending=False)
    decreases = df[df["delta"] < 0].sort_values("delta")

    col_up, col_down = st.columns(2)
    with col_up:
        st.markdown("### ↑ Limit increases")
        for _, row in increases.iterrows():
            s = summary[summary["service_id"] == row["service_id"]].iloc[0]
            st.success(
                f"**{row['service_name']}** → {int(row['adjusted_limit']):,} {CURRENCY} "
                f"({row['delta_pct']:+.1f}%)\n\n"
                f"Claims average {int(s['mean_claim']):,} AMD with a {s['binding_rate']:.0f}% binding rate. "
                "The limit is not frequently reached, so raising it costs little in expected payout "
                "while improving coverage quality."
            )

    with col_down:
        st.markdown("### ↓ Limit decreases")
        for _, row in decreases.iterrows():
            s = summary[summary["service_id"] == row["service_id"]].iloc[0]
            st.error(
                f"**{row['service_name']}** → {int(row['adjusted_limit']):,} {CURRENCY} "
                f"({row['delta_pct']:+.1f}%)\n\n"
                f"This service has {int(s['n_claims'])} claims averaging "
                f"{int(s['mean_claim']):,} AMD. "
                "Reducing its limit frees budget for more binding services "
                "while minimally impacting actual reimbursements."
            )

    st.divider()
    st.info(
        "**Bottom line:** The optimiser acts like a portfolio manager — it reallocates "
        "budget from over-funded, low-utilisation services toward those where the limit "
        "is a genuine constraint. The total limit pool is unchanged."
    )
