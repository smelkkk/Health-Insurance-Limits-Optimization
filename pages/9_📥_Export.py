from datetime import date

import streamlit as st

from src.config import CURRENCY
from src.data_loader import build_service_summary, load_optimization_inputs, load_service_claims
from src.export import generate_text_summary, to_csv_bytes, to_excel_bytes
from src.metrics import portfolio_kpis
from src.optimization import fallback_balanced_dataframe
from src.recommendations import generate_recommendations

from pathlib import Path as _Path
_ASSETS = _Path(__file__).parent.parent / "assets"
st.set_page_config(page_title="KinetiX · Export", page_icon=str(_ASSETS / "Kinetix_symbol_green.ico"), layout="wide")

# inject CSS
_css = _ASSETS / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)
st.title("📥 Export Centre")
st.caption("Download optimisation results, comparison tables, and reports.")
st.divider()

claims     = load_service_claims()
opt_inputs = load_optimization_inputs()
summary    = build_service_summary(claims, opt_inputs)
kpis       = portfolio_kpis(summary)
df_bva     = fallback_balanced_dataframe()
recs       = generate_recommendations(summary)
today      = date.today().isoformat()

# ── export 1: optimised limits CSV ────────────────────────────────────────────
st.subheader("1. Optimised Limits")
st.caption("Clean table of original and optimised limits per service.")

limits_export = df_bva[[
    "service_id", "service_name", "original_limit", "adjusted_limit", "delta", "delta_pct"
]].rename(columns={
    "service_id":      "Service ID",
    "service_name":    "Service Name",
    "original_limit":  f"Original Limit ({CURRENCY})",
    "adjusted_limit":  f"Optimised Limit ({CURRENCY})",
    "delta":           f"Adjustment ({CURRENCY})",
    "delta_pct":       "Adjustment (%)",
})

st.download_button(
    label="⬇ Download Optimised Limits (CSV)",
    data=to_csv_bytes(limits_export),
    file_name=f"optimised_limits_{today}.csv",
    mime="text/csv",
)

# ── export 2: full comparison Excel ───────────────────────────────────────────
st.divider()
st.subheader("2. Full Comparison Report (Excel)")
st.caption("Multi-sheet Excel workbook with limits, diagnostics, and recommendations.")

merged = df_bva.merge(
    summary[[
        "service_id", "n_claims", "mean_claim", "median_claim", "max_claim",
        "binding_rate", "total_reimbursed_original", "total_reimbursed_optimized",
    ]],
    on="service_id",
)

excel_data = to_excel_bytes({
    "Optimised Limits":   limits_export,
    "Full Comparison":    merged.rename(columns={
        "service_id":                 "Service ID",
        "service_name":               "Service Name",
        "original_limit":             f"Original Limit ({CURRENCY})",
        "adjusted_limit":             f"Optimised Limit ({CURRENCY})",
        "delta":                      f"Adjustment ({CURRENCY})",
        "delta_pct":                  "Adjustment (%)",
        "n_claims":                   "# Claims",
        "mean_claim":                 f"Mean Claim ({CURRENCY})",
        "median_claim":               f"Median Claim ({CURRENCY})",
        "max_claim":                  f"Max Claim ({CURRENCY})",
        "binding_rate":               "Binding Rate (%)",
        "total_reimbursed_original":  f"Reimbursed Original ({CURRENCY})",
        "total_reimbursed_optimized": f"Reimbursed Optimised ({CURRENCY})",
    }),
    "Recommendations": recs[["service_name", "category", "headline", "detail"]].rename(columns={
        "service_name": "Service",
        "category":     "Category",
        "headline":     "Headline",
        "detail":       "Detail",
    }),
})

st.download_button(
    label="⬇ Download Full Report (Excel)",
    data=excel_data,
    file_name=f"insurance_limit_optimisation_{today}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# ── export 3: text summary ─────────────────────────────────────────────────────
st.divider()
st.subheader("3. Executive Text Summary")
st.caption("Plain-text summary suitable for email or presentation notes.")

text_summary = generate_text_summary(kpis, summary)

st.code(text_summary, language=None)
st.download_button(
    label="⬇ Download (.txt)",
    data=text_summary.encode("utf-8"),
    file_name=f"executive_summary_{today}.txt",
    mime="text/plain",
)

# ── export 4: recommendations ──────────────────────────────────────────────────
st.divider()
st.subheader("4. Recommendations Table")
st.caption("Actionable recommendations in CSV for easy sharing with stakeholders.")

st.download_button(
    label="⬇ Download Recommendations (CSV)",
    data=to_csv_bytes(
        recs[["service_name", "category", "headline", "detail"]].rename(columns={
            "service_name": "Service",
            "category":     "Category",
            "headline":     "Headline",
            "detail":       "Detail",
        })
    ),
    file_name=f"recommendations_{today}.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "All exports reflect the Balanced scenario (λ = 0.01) using historical claim data "
    f"from March 2024 – March 2025. Generated on {today}."
)
