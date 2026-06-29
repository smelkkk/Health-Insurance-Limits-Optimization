import streamlit as st

from src.data_loader import build_service_summary, load_optimization_inputs, load_service_claims
from src.recommendations import CATEGORY_COLOURS, CATEGORY_ICONS, generate_recommendations

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Recommendations", page_icon=str(_ASSETS / "Kinetix_symbol_green.ico"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("💡 Business Recommendations")
st.caption("Prioritised, plain-language action items based on optimisation output.")
st.divider()

claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
summary    = build_service_summary(claims, opt_inputs)
recs       = generate_recommendations(summary)

# ── priority legend ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.error(  "🔴 Review Immediately")
c2.warning("🟡 Monitor")
c3.success("🟢 Low-Risk Adjustment")
c4.info(   "⚪ Needs More Data")

st.divider()

# ── filter ─────────────────────────────────────────────────────────────────────
categories = recs["category"].unique().tolist()
selected_cats = st.multiselect(
    "Filter by category", options=categories, default=categories,
)
filtered = recs[recs["category"].isin(selected_cats)]

st.markdown(f"Showing **{len(filtered)}** of {len(recs)} recommendations.")
st.divider()

# ── cards ──────────────────────────────────────────────────────────────────────
for _, row in filtered.iterrows():
    icon   = CATEGORY_ICONS.get(row["category"], "•")
    colour = CATEGORY_COLOURS.get(row["category"], "#6B7280")

    with st.container():
        st.markdown(
            f"""
<div style="border-left: 4px solid {colour}; padding: 20px 24px; margin-bottom: 16px;
            background: rgb(13,13,13); border: 1px solid rgba(84,84,84,0.5);
            border-radius: 12px; font-family: Inter, sans-serif;">
  <span style="font-size:11px; font-weight:600; color:{colour}; text-transform:uppercase;
               letter-spacing:0.08em;">
    {icon} {row['category']}
  </span><br/>
  <span style="font-size:16px; font-weight:700; color:rgb(255,255,255);
               display:inline-block; margin-top:8px;">{row['service_name']}</span><br/>
  <span style="font-size:14px; color:rgb(161,161,161);
               display:inline-block; margin-top:4px;">{row['headline']}</span><br/>
  <span style="font-size:13px; color:rgb(128,128,128);
               display:inline-block; margin-top:12px; line-height:1.5;">{row['detail']}</span>
</div>
""",
            unsafe_allow_html=True,
        )

st.divider()

# ── summary table ──────────────────────────────────────────────────────────────
st.markdown("""
    <div style="color:rgb(64,242,154); font-size:12px; font-weight:600;
                text-transform:uppercase; letter-spacing:0.08em;
                margin:16px 0 12px; font-family:Inter,sans-serif;">
      📋 Summary table
    </div>
""", unsafe_allow_html=True)
st.dataframe(
    recs[["service_name", "category", "headline"]].rename(columns={
        "service_name": "Service",
        "category":     "Category",
        "headline":     "Headline",
    }),
    use_container_width=True,
    hide_index=True,
)

# ── caution note ───────────────────────────────────────────────────────────────
st.warning(
    "**Caution:** These recommendations are generated automatically from statistical "
    "patterns in historical data. They should be reviewed by qualified actuaries "
    "before any changes are made to insurance contracts or product limits. "
    "Services with fewer than 10 claims are flagged as low-confidence."
)
