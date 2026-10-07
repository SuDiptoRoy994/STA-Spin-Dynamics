# New STA-Spin-Dynamics simulations: Tier 2–4

These scripts extend the original STA-Spin-Dynamics project without changing the core physical convention.

## Common model

- Rotating-frame Bloch equations
- `T1 = 1.5 s`
- `T2 = 80 ms`
- `M0 = 1`
- `Omega0 = 2*pi*1 kHz`
- `Delta_max = 2*pi*5 kHz`
- Linear chirp: `delta(t) = Delta_max*(1 - 2*t/tau)`
- Counterdiabatic term: `omega_y = -dtheta/dt`
- Initial state: `M(0) = (0,0,M0)`
- Solver: `scipy.integrate.solve_ivp`

The shared model is in `scripts/common_model.py`. Robustness tests apply the B1 scale to both RF quadratures in the STA case. Static off-resonance is added to the actual detuning while the nominal CD waveform is kept fixed. This is a true robustness test rather than a redesigned pulse.

## Tier 2 — strengthen the present paper

### 01_off_resonance_sweep.py
Question: How does the fixed 2-ms pulse behave when the spin has an additional static frequency offset?

Paper figure: `figure_T2_off_resonance_2ms.png`

Important interpretation: STA is not guaranteed to be better at every off-resonance value. Treat any crossover as a scientific result and motivation for ensemble optimization.

### 02_T2_sensitivity.py
Question: Does the conclusion survive changes in transverse relaxation time?

Paper figure: `figure_T2_T2_sensitivity.png`

Main metric: target-state inversion fidelity.

### 03_T1_sensitivity.py
Question: How sensitive are the results to longitudinal relaxation?

Paper figure: `figure_T2_T1_sensitivity.png`

This is a secondary sensitivity study because the pulse duration is much shorter than T1.

### 04_closed_vs_dissipative.py
Question: How much of the conventional-pulse loss comes from nonadiabatic dynamics rather than relaxation?

Paper figure: `figure_T2_closed_vs_dissipative.png`

This is an ablation study. It is especially useful in the Discussion section.

### 05_numerical_convergence.py
Question: Are the reported results numerical artifacts?

Paper figure: `figure_T2_numerical_convergence.png`

The comparison is against a tighter-tolerance reference solution.

## Tier 3 — make the paper more like RF-pulse research

### 06_B1_offresonance_map.py
Question: Over what joint range of RF amplitude and frequency offset does the fixed pulse maintain high inversion?

Outputs: two performance maps and one difference map.

Use the difference map to identify where STA really helps and where it does not.

### 07_rf_control_cost.py
Question: What control cost is paid for the STA speed/fidelity benefit?

Definitions:

`peak_total_omega = max(sqrt(omega_x^2 + omega_y^2))`

`J_RF = integral(omega_x^2 + omega_y^2) dt`

**J_RF is a control-cost proxy, not SAR.**

### 08_speed_performance_cost.py
A presentation-oriented summary of speed versus inversion performance. Use this to explain the trade-off to a professor.

## Tier 4 — future research prototypes

### 09_sta_ensemble_parameter_optimization.py
This is NOT full optimal control. It is a small research prototype that optimizes only three pulse parameters over a small B1/off-resonance ensemble.

Use it to demonstrate how your current analytic STA pulse can become the starting point for an ensemble-aware optimization problem.

Do not report the optimized numbers as a paper result until you have reviewed the objective function, bounds, numerical stability, and physical constraints.

### 10_bloch_vs_lindblad.py
This tests the same 2-ms pulse with a density-matrix Lindblad model.

Use it as a model-validation/future-work exercise. It helps you explain why the present Bloch model is useful and what a more explicit open-quantum-system treatment would add.

## Suggested GitHub structure

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
├── results/
├── figures/
├── requirements.txt
└── README.md
```

## Requirements

Python 3.10+

```bash
python -m pip install numpy scipy pandas matplotlib
```

## Recommended run order

1. 01 off-resonance
2. 02 T2 sensitivity
3. 03 T1 sensitivity
4. 04 closed vs dissipative
5. 05 numerical convergence
6. 06 joint B1/off-resonance map
7. 07 RF-control cost
8. 08 speed-performance summary
9. 09 ensemble optimization prototype
10. 10 Bloch-vs-Lindblad validation

For the paper, do not add Tier 4 numbers until you have independently reviewed and rerun them.


## Validation status
See `VALIDATION_REPORT.md` for which scripts were executed successfully in the current environment and which outputs are exploratory only.

The default joint B1/off-resonance map uses 15 RF-amplitude points x 31 off-resonance points to remain laptop-friendly. You can increase resolution with `STA_B1_POINTS` and `STA_OFF_POINTS`.
