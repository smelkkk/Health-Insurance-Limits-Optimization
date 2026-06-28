import streamlit as st

from src.config import CURRENCY
from src.data_loader import build_service_summary, load_optimization_inputs, load_service_claims
from src.metrics import pareto_table
from src.visualizations import claims_by_service_bar, pareto_chart, reimbursement_by_service_bar

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Data Overview", page_icon=str(_ASSETS / "favicon.png"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("📊 Data Overview")
st.caption("Claim volumes, cost concentration, and data quality by service group.")
st.divider()

claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
summary    = build_service_summary(claims, opt_inputs)

# ── service-level table ────────────────────────────────────────────────────────
st.subheader("Service-Level Summary Table")

display = summary[[
    "service_id", "service_name", "original_limit", "n_claims",
    "mean_claim", "median_claim", "max_claim", "total_claimed",
    "total_reimbursed_original", "claim_share", "binding_rate",
]].rename(columns={
    "service_id":               "ID",
    "service_name":             "Service",
    "original_limit":           f"Limit ({CURRENCY})",
    "n_claims":                 "# Claims",
    "mean_claim":               f"Mean Claim ({CURRENCY})",
    "median_claim":             f"Median Claim ({CURRENCY})",
    "max_claim":                f"Max Claim ({CURRENCY})",
    "total_claimed":            f"Total Claimed ({CURRENCY})",
    "total_reimbursed_original": f"Total Reimbursed ({CURRENCY})",
    "claim_share":              "Claim Share%",
    "binding_rate":             "Binding Rate%",
})

st.dataframe(
    display.style.format({
        f"Limit ({CURRENCY})":            "{:,.0f}",
        f"Mean Claim ({CURRENCY})":       "{:,.0f}",
        f"Median Claim ({CURRENCY})":     "{:,.0f}",
        f"Max Claim ({CURRENCY})":        "{:,.0f}",
        f"Total Claimed ({CURRENCY})":    "{:,.0f}",
        f"Total Reimbursed ({CURRENCY})": "{:,.0f}",
        "Claim Share%":                   "{:.1f}%",
        "Binding Rate%":                  "{:.0f}%",
    }),
    use_container_width=True,
    hide_index=True,
)

# ── data quality flags ─────────────────────────────────────────────────────────
low_data = summary[summary["n_claims"] < 10]
if not low_data.empty:
    st.warning(
        f"⚠️  **Low-data services** (fewer than 10 claims): "
        + ", ".join(f"**{r['service_name']}** ({int(r['n_claims'])} claims)"
                    for _, r in low_data.iterrows())
        + ". Model results for these services should be interpreted cautiously."
    )

high_conc = summary[summary["reimbursement_share"] > 30]
if not high_conc.empty:
    for _, r in high_conc.iterrows():
        st.info(
            f"📌  **{r['service_name']}** accounts for **{r['reimbursement_share']:.1f}%** "
            "of total reimbursements - a dominant cost driver in the portfolio."
        )

st.divider()

# ── charts ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(claims_by_service_bar(summary), use_container_width=True)

with col2:
    st.plotly_chart(reimbursement_by_service_bar(summary), use_container_width=True)

st.plotly_chart(
    pareto_chart(pareto_table(summary)),
    use_container_width=True,
)

from src.components import info_block
info_block("How to read the Pareto chart",
    "The <strong>Pareto chart</strong> ranks services by their share of total reimbursements. "
    "The line shows the <strong>cumulative</strong> share.<br><br>"
    "In most insurance portfolios, a small number of service groups drive the majority of cost. "
    "In this portfolio, <strong>General Ambulatory Care</strong> alone accounts for the largest single share - "
    "making it the most important service to calibrate correctly.<br><br>"
    "This view helps pricing teams focus attention on cost drivers rather than treating all services equally."
)
