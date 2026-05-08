# Health Insurance Limit Optimization — ESADE MiBA Capstone

**ESADE MiBA Capstone | In collaboration with KinetiX**

This project develops a data-driven optimization engine for health insurance reimbursement limits. Using Mixed Integer Quadratic Programming (MIQP), it redistributes coverage limits across 11 medical services in a way that is budget-neutral, reduces financial variance (actuarial risk), and maximizes expected reimbursement fairness across the portfolio.

---

## Table of Contents

1. [Business Context](#business-context)
2. [Problem Formulation](#problem-formulation)
3. [Project Structure](#project-structure)
4. [Data](#data)
5. [Pipeline Overview](#pipeline-overview)
6. [Optimization Model](#optimization-model)
7. [Results & Business Interpretation](#results--business-interpretation)
8. [Validation](#validation)
9. [Dependencies](#dependencies)

---

## Business Context

A health insurer covers a portfolio of medical services — from low-frequency, high-cost procedures (e.g., major surgery) to high-frequency, lower-cost services (e.g., outpatient consultations). Each service has a **reimbursement limit**: the maximum amount paid out per claim.

**The business problem**: Are the current limits set optimally? Could an insurer reduce its total expected payout or variance *without* changing its total limit budget — simply by redistributing limits across services?

**Why this matters**:
- **For the insurer**: Lower variance means more predictable cash flow, reduced reserve requirements, and better actuarial stability.
- **For policyholders**: Fair limits mean high-claim services are not capped too aggressively, and low-claim services are not over-funded at the expense of others.
- **Regulatory**: Budget neutrality ensures no net change in total liability — making the adjustment defensible to regulators and actuaries.

---

## Problem Formulation

### Objective

Minimize a weighted combination of **expected total reimbursement** and **variance of reimbursement** across all services:

```
minimize  Σᵢ wᵢ · [E[rᵢ(Tᵢ)] + λ · Var[rᵢ(Tᵢ)]]
```

Where:
- `rᵢ(Tᵢ) = min(claimᵢ, Tᵢ)` — reimbursed amount for service `i` under limit `Tᵢ`
- `Tᵢ = Lᵢ + δᵢ` — adjusted limit (original limit + delta)
- `wᵢ` — weight proportional to service claim volume
- `λ` — risk-aversion parameter (set to 0.01 after sensitivity analysis)

### Constraints

| Constraint | Formula | Meaning |
|-----------|---------|---------|
| Budget neutrality | `Σ δᵢ = 0` | Total limit budget unchanged |
| Adaptive bounds | `\|δᵢ\| ≤ εᵢ · Lᵢ` | Limit adjustments capped per service |
| Non-negativity | `mᵢⱼ ≥ 0` | Reimbursements are non-negative |

### Adaptive Epsilon

Adjustment bounds are calibrated to claim data volume:

```
εᵢ = min(0.05, 0.4 / √nᵢ)
```

Services with fewer historical claims get tighter bounds (more conservative adjustments), reflecting statistical uncertainty. Services with many claims (e.g., Service 8 with 962 claims) are trusted more and allowed proportionally larger adjustments.

### Linearization of min()

The `min(claimᵢⱼ, Tᵢ)` operator is non-linear. It is linearized using binary variables `zᵢⱼ ∈ {0,1}` and auxiliary continuous variables `mᵢⱼ`, converting the problem to a MIQP solvable by Gurobi.

---

## Project Structure

```
Capstone/
│
├── data_process.ipynb          # Step 1: Load raw data, bin distributions, export optimization_inputs.pkl
├── solver.ipynb                # Step 2: Core MIQP optimization model (main result)
├── experiments.ipynb           # Step 3: Lambda sensitivity analysis (λ sweep + fine-grained zoom)
├── comparison.ipynb            # Step 4: Before/after reimbursement comparison on real claims
├── monte_carlo_simulation.ipynb # Step 5: Monte Carlo validation (100 simulation runs)
│
├── services/                   # Raw input data: 11 Excel files, one per service
│   ├── services_1_400000.xlsx  # Service index _ original limit
│   ├── services_2_1500000.xlsx
│   └── ...                     # (11 files total)
│
├── optimization_inputs.pkl     # Preprocessed data: bin centers (c_ij), probabilities (p_ij), limits
├── optimized_limits.csv        # Final optimization output (CSV)
├── optimized_limits2.xlsx      # Final optimization output (Excel, with chart)
├── limits_comparison_plot.png  # Bar chart: original vs. adjusted limits per service
│
```

---

## Data

The `services/` directory contains 11 Excel files, one per medical service. Each file follows the naming convention:

```
services_{index}_{original_limit}.xlsx
```

Each file contains one column: `ClaimedAmount` — the amount each patient claimed for that service.

### Service Summary

| Service | Original Limit (AMD) | Claims |
|---------|---------------------|--------|
| 1 | 400,000 | 2 |
| 2 | 1,500,000 | 7 |
| 3 | 600,000 | 18 |
| 4 | 200,000 | 19 |
| 5 | 30,000 | 41 |
| 6 | 300,000 | 75 |
| 7 | 100,000 | 128 |
| 8 | 100,000 | 962 |
| 9 | 100,000 | 36 |
| 10 | 500,000 | 143 |
| 11 | 60,000 | 146 |

**Note**: AMD = Armenian Dram. Service 8 accounts for ~61% of all claims and dominates the weighted objective.

---

## Pipeline Overview

```
services/*.xlsx
      │
      ▼
data_process.ipynb
  - Load Excel files
  - Bin claim distributions (14 bins, 0–200% of limit)
  - Compute bin centers c_ij and probabilities p_ij
  - Export: optimization_inputs.pkl
      │
      ▼
solver.ipynb
  - Load optimization_inputs.pkl
  - Build MIQP model in Gurobi
  - Solve with λ=0.01, adaptive ε, weighted objective
  - Export: optimized_limits.csv, optimized_limits2.xlsx, limits_comparison_plot.png
      │
      ├──▶ experiments.ipynb     (lambda sensitivity: what if λ were different?)
      ├──▶ comparison.ipynb      (apply optimized limits to real claims, measure savings)
      └──▶ monte_carlo_simulation.ipynb  (statistical robustness over 100 random scenarios)
```

---

## Optimization Model

The model is implemented in `solver.ipynb` using **Gurobi 13** (`gurobipy`).

### Model Statistics (at λ=0.01)
- **392 constraints**, **195 variables** (103 continuous + 92 binary)
- Solves to **optimality in ~0.02 seconds** (gap = 0.00%)
- Objective value: **39,223,106.71**

### Lambda Selection

`experiments.ipynb` sweeps λ across 9 orders of magnitude (10⁻⁷ to 10¹) and performs a fine-grained zoom in [10⁻⁶, 10⁻⁴]. Key finding: the model transitions from pure cost minimization (low λ) to pure variance minimization (high λ) around λ ≈ 10⁻⁵. **λ = 0.01** was selected as a balanced operating point.

---

## Results & Business Interpretation

### Optimized Limits

| Service | Original (AMD) | Adjusted (AMD) | Δ | Δ% |
|---------|---------------|----------------|---|-----|
| 1 | 400,000 | 420,000 | +20,000 | +5.00% |
| 2 | 1,500,000 | 1,436,109 | −63,891 | −4.26% |
| 3 | 600,000 | 630,000 | +30,000 | +5.00% |
| 4 | 200,000 | 210,000 | +10,000 | +5.00% |
| 5 | 30,000 | 31,500 | +1,500 | +5.00% |
| 6 | 300,000 | 313,856 | +13,856 | +4.62% |
| 7 | 100,000 | 103,536 | +3,536 | +3.54% |
| 8 | 100,000 | 98,710 | −1,290 | −1.29% |
| 9 | 100,000 | 105,000 | +5,000 | +5.00% |
| 10 | 500,000 | 483,275 | −16,725 | −3.34% |
| 11 | 60,000 | 58,014 | −1,986 | −3.31% |

### Business Interpretation

**Why do some limits go up and others go down?**

The model simultaneously pursues two goals: reduce the total expected payout and reduce its variance. The key insight is that adjusting limits is not uniformly beneficial — the impact depends on where claims tend to fall relative to the current limit.

- **Services where limits increase (1, 3, 4, 5, 6, 7, 9)**: These services have claim distributions concentrated *below* the current limit. The limit is already not binding in most cases, so raising it costs little in expected payout but signals better coverage. The model pushes these to their maximum allowed increase (+5%) because the marginal cost is low.

- **Service 2 (−4.26%, biggest cut in absolute terms)**: High original limit (1.5M AMD) with only 7 historical claims. The model finds that this limit is significantly over-funded relative to actual claim patterns. Reducing it by ~64,000 AMD frees budget while barely affecting expected reimbursements.

- **Service 8 (−1.29%, 962 claims)**: The highest-volume service. Even a small percentage reduction in its limit has a large budget impact. The model trims it slightly to redistribute to smaller services, while keeping the cut minimal to protect the majority of claimants.

- **Services 10 and 11 (−3.34%, −3.31%)**: Medium-volume services with claim patterns that show room for reduction. The model captures budget from these to fund increases elsewhere.

**Bottom line**: The optimizer acts like a rational portfolio manager — it over-funds high-certainty, low-cost services to absorb risk, and trims high-limit, low-utilization services where the budget is inefficiently deployed.

### Reimbursement Impact (from `comparison.ipynb`)

Applied to real claims data:

| | Total Reimbursed (AMD) |
|---|---|
| Original limits | 107,165,638 |
| Optimized limits | 106,931,133 |
| **Reduction** | **234,506 (−0.22%)** |

A **234,506 AMD saving** with a budget-neutral limit restructuring — no premiums changed, no benefits eliminated. The saving comes purely from more efficient limit placement.

---

## Validation

`monte_carlo_simulation.ipynb` runs 100 independent simulations, each time drawing random claim samples from the empirical distributions and computing total reimbursements under both original and optimized limits.

This confirms that the savings observed on actual claims generalize across random scenarios — the optimized limits are not overfit to the specific observed claims.

---

## Environment Setup

This project uses a dedicated conda environment (`capstone`) with **Python 3.11**.

### Option A — Conda (recommended)

```bash
conda env create -f environment.yml
conda activate capstone
```

### Option B — pip only

```bash
pip install -r requirements.txt
```

### Gurobi License

`gurobipy` is installed via pip in both options, but **a valid Gurobi license is required to run the solver**. Without it, `solver.ipynb` and `experiments.ipynb` will fail at `model.optimize()`.

- **Academic license** (free): [gurobi.com/academia](https://www.gurobi.com/academia/academic-program-and-licenses/)
- Once issued, activate it with: `grbgetkey <your-key>`

The data processing (`data_process.ipynb`), comparison (`comparison.ipynb`), and Monte Carlo (`monte_carlo_simulation.ipynb`) notebooks do **not** require Gurobi — they can run on any machine with the pip/conda dependencies above.
