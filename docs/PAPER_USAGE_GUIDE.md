# How to use each simulation in the paper

## Tier 2: scientific validation

**01_off_resonance_sweep.py**
- Question: Does the fixed 2-ms analytic pulse remain effective under static frequency offsets?
- Main figure: `figure_T2_off_resonance_2ms.png`
- Paper section: Results / robustness; Discussion / design-point limitation.
- Do not claim STA is better at every offset.

**02_T2_sensitivity.py**
- Question: Does the main result survive plausible changes in T2?
- Figure: `figure_T2_T2_sensitivity.png`
- Paper section: Results / sensitivity analysis.

**03_T1_sensitivity.py**
- Question: Does the result depend strongly on T1?
- Figure: `figure_T2_T1_sensitivity.png`
- Paper section: Secondary sensitivity analysis.

**04_closed_vs_dissipative.py**
- Question: Which part of the 2-ms performance difference comes from nonadiabatic dynamics versus relaxation?
- Figure: `figure_T2_closed_vs_dissipative.png`
- Paper section: Results / ablation; Discussion / error mechanisms.

**05_numerical_convergence.py**
- Question: Are the numerical results stable with respect to solver tolerance?
- Figure: `figure_T2_numerical_convergence.png`
- Paper section: Methods / numerical verification or Supplementary Information.

## Tier 3: RF-pulse-design engineering analysis

**06_B1_offresonance_map.py**
- Question: Over what joint RF-amplitude and off-resonance region does the fixed pulse maintain performance?
- Figures: conventional map, STA map, and STA-minus-conventional map.
- Paper section: Robustness / limitations.
- This is especially useful for explaining why a fixed analytic STA pulse should eventually be optimized over an ensemble.

**07_rf_control_cost.py**
- Question: What RF-control cost is paid for the STA benefit?
- Metric 1: peak total control `max(sqrt(omega_x^2+omega_y^2))`.
- Metric 2: `J_RF = integral(omega_x^2+omega_y^2) dt`.
- **J_RF is NOT SAR.**
- Figure: `figure_T3_control_cost.png`.

**08_speed_performance_cost.py**
- Compact presentation figure for explaining speed/performance trade-offs.
- Figure: `figure_T3_speed_performance_cost.png`.

## Tier 4: future-research prototypes

**09_sta_ensemble_parameter_optimization.py**
- This is a prototype parameter optimizer, NOT full OCT.
- It optimizes Omega0, Delta_max, and tau over a small B1/off-resonance ensemble with soft penalties.
- Use it in a research presentation as a next-step demonstration, not as a final paper result until independently reviewed.

**10_bloch_vs_lindblad.py**
- Same 2-ms pulse, but the spin is simulated with a density-matrix Lindblad model.
- The current implementation matches the Bloch result to numerical precision after matching the Hamiltonian sign convention and T1 equilibrium convention.
- Use this as a model-validation exercise and future-method extension.

## Recommended GitHub structure

```text
STA-Spin-Dynamics/
├── day1_larmor_relaxation.py
├── day2_hard_pulse.py
├── day3_adiabatic_pulse.py
├── day4_sta_cd_driving.py
├── scripts/
│   ├── common_model.py
│   ├── 01_off_resonance_sweep.py
│   ├── 02_T2_sensitivity.py
│   ├── 03_T1_sensitivity.py
│   ├── 04_closed_vs_dissipative.py
│   ├── 05_numerical_convergence.py
│   ├── 06_B1_offresonance_map.py
│   ├── 07_rf_control_cost.py
│   ├── 08_speed_performance_cost.py
│   ├── 09_sta_ensemble_parameter_optimization.py
│   └── 10_bloch_vs_lindblad.py
├── figures/
├── results/
├── requirements.txt
├── PAPER_USAGE_GUIDE.md
└── README.md
```

## Environment overrides

For a quick test of the 2-D map:

```bash
STA_B1_POINTS=7 STA_OFF_POINTS=9 python scripts/06_B1_offresonance_map.py
```

For a quicker optimization test:

```bash
STA_OPT_MAXITER=3 STA_OPT_POPSIZE=4 python scripts/09_sta_ensemble_parameter_optimization.py
```

Use the defaults for final runs.
