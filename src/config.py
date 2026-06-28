from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

SERVICES_DIR      = BASE_DIR / "services"
PRECOMPUTED_DIR   = BASE_DIR / "data" / "precomputed"
OPT_INPUTS_PATH   = BASE_DIR / "optimization_inputs.pkl"
OPT_LIMITS_PATH   = BASE_DIR / "optimized_limits.csv"

# Human-readable service names inferred from clause codes and limit/volume patterns
SERVICE_NAMES = {
    1:  "Major Inpatient Surgery",
    2:  "Complex Hospital Treatment",
    3:  "Specialist Inpatient Care",
    4:  "Chronic Disease Management",
    5:  "Outpatient Therapy Services",
    6:  "Multispecialty Consultations",
    7:  "Diagnostics & Lab Tests",
    8:  "General Ambulatory Care",
    9:  "Rehabilitation Services",
    10: "Advanced Clinical Procedures",
    11: "Dental & Preventive Care",
}

ORIGINAL_LIMITS = {
    1: 400_000, 2: 1_500_000, 3: 600_000, 4: 200_000,  5:  30_000,
    6: 300_000, 7:   100_000, 8: 100_000, 9: 100_000, 10: 500_000, 11: 60_000,
}

OPTIMIZED_LIMITS = {
    1: 420_000, 2: 1_436_109, 3: 630_000, 4: 210_000,  5:  31_500,
    6: 313_856, 7:   103_536, 8:  98_710, 9: 105_000, 10: 483_275, 11: 58_014,
}

LAMBDA_DEFAULT = 0.01
K_EPSILON = 0.4      # adaptive epsilon coefficient
MAX_EPSILON = 0.05

NAMED_SCENARIOS = {
    "Cost-Focused":       {"lambda": 1e-5,  "description": "Minimises expected payout. Accepts higher variance."},
    "Balanced":           {"lambda": 1e-2,  "description": "Balances cost and stability. Recommended default."},
    "Stability-Focused":  {"lambda": 1e-1,  "description": "Prioritises variance reduction. Accepts higher cost."},
}

CURRENCY = "AMD"

# Colour palette - KinetiX dark theme
C_PRIMARY   = "rgb(64,242,154)"       # KinetiX green accent
C_SECONDARY = "rgb(149,245,71)"       # secondary green
C_DARK      = "rgb(13,13,13)"         # card surfaces
C_BG        = "rgb(0,0,0)"            # page background
C_BORDER    = "rgba(84,84,84,0.5)"    # borders
C_OPTIMIZED = "rgb(64,242,154)"       # positive / optimised
C_NEGATIVE  = "rgb(220,80,80)"        # negative / error
C_WARNING   = "rgb(240,190,0)"        # warning
C_NEUTRAL   = "rgb(128,128,128)"      # muted text
C_LIGHT     = "rgb(161,161,161)"      # body text
C_TEXT      = "rgb(255,255,255)"      # primary text
C_DARK_GREEN= "rgb(30,59,12)"        # badge background
C_CHART_1   = "rgb(64,242,154)"
C_CHART_2   = "rgb(149,245,71)"
C_CHART_3   = "rgba(64,242,154,0.5)"
C_CHART_4   = "rgba(149,245,71,0.4)"
C_CHART_5   = "rgb(51,51,51)"

# Dark Plotly layout applied to every chart
PLOTLY_TEMPLATE = "plotly_dark"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgb(0,0,0)",
    plot_bgcolor="rgb(13,13,13)",
    font=dict(family="Inter, sans-serif", color="rgb(161,161,161)"),
    title_font=dict(family="Inter, sans-serif", color="rgb(255,255,255)", size=16),
    xaxis=dict(
        gridcolor="rgba(84,84,84,0.3)",
        tickfont=dict(color="rgb(128,128,128)"),
        linecolor="rgba(84,84,84,0.5)",
    ),
    yaxis=dict(
        gridcolor="rgba(84,84,84,0.3)",
        tickfont=dict(color="rgb(128,128,128)"),
        linecolor="rgba(84,84,84,0.5)",
    ),
    legend=dict(
        bgcolor="rgba(13,13,13,0.8)",
        bordercolor="rgba(84,84,84,0.5)",
        borderwidth=1,
        font=dict(color="rgb(161,161,161)"),
    ),
    hoverlabel=dict(
        bgcolor="rgb(13,13,13)",
        bordercolor="rgba(64,242,154,0.5)",
        font=dict(family="Inter, sans-serif", color="rgb(255,255,255)"),
    ),
    margin=dict(l=40, r=20, t=80, b=40),
)
