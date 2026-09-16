# 🧲 STA-Spin-Dynamics

**Bloch Equation Simulations: Shortcuts to Adiabaticity for MRI RF Pulse Design**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-1.10%2B-8CAAE6?style=flat&logo=scipy&logoColor=white)](https://scipy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-11557C?style=flat)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This project simulates nuclear spin dynamics under MRI radiofrequency (RF) pulses, building progressively from basic Larmor precession to a full demonstration of **Shortcuts to Adiabaticity (STA)** via counterdiabatic (CD) driving.

**The central problem:** Conventional adiabatic RF pulses face a fundamental contradiction in biological tissue. Slowing the pulse to satisfy the adiabatic condition increases the duration of noise exposure, degrading fidelity through T₂ relaxation. Making the pulse fast violates the adiabatic condition, causing diabatic transitions that collapse inversion fidelity.

**The STA solution:** Counterdiabatic driving adds an analytically derived quadrature component ω_y(t) to the standard RF waveform. This exactly cancels diabatic transitions by construction — restoring high-fidelity inversion at fast timescales, with no exotic hardware required.

> This simulation supports the accompanying review paper:  
> *"Can Shortcuts to Adiabaticity Overcome the Speed–Fidelity Trade-off in Neural Stimulation fMRI?"*  
> — Sudipto Roy (2025, manuscript in preparation)

---

## Physical Model

A spin-½ nucleus in the rotating frame, with T₁/T₂ relaxation representing biological tissue:

$$\frac{dM_x}{dt} = \delta(t)\,M_y - \omega_y(t)\,M_z - \frac{M_x}{T_2}$$

$$\frac{dM_y}{dt} = -\delta(t)\,M_x + \omega_x(t)\,M_z - \frac{M_y}{T_2}$$

$$\frac{dM_z}{dt} = \omega_y(t)\,M_x - \omega_x(t)\,M_y - \frac{M_z - M_0}{T_1}$$

| Parameter | Value | Meaning |
|-----------|-------|---------|
| T₁ | 1.500 s | Longitudinal relaxation — grey matter, 3T |
| T₂ | 0.080 s | Transverse relaxation — grey matter, 3T |
| Ω₀ | 2π × 1000 rad/s | Rabi (RF) frequency |
| Δ_max | 2π × 5000 rad/s | Chirp sweep range |
| τ_slow | 20 ms | Slow adiabatic pulse duration |
| τ_fast | 2 ms | Fast pulse duration (STA target) |

---

## Repository Structure

```
STA-Spin-Dynamics/
│
├── day1_larmor_precession.py   ← Spin precession, T1/T2 relaxation, FID
├── day2_hard_pulse.py          ← Rectangular π pulse and off-resonance failure
├── day3_adiabatic_pulse.py     ← Linear-chirp adiabatic pulse, adiabatic condition
├── day4_sta_cd_driving.py      ← STA counterdiabatic driving — the main result
│
├── figures/                    ← Output figures (auto-generated on run)
│   ├── day1_larmor_precession.png
│   ├── day2_hard_pulse.png
│   ├── day3_adiabatic_pulse.png
│   └── day4_sta_cd_driving.png
│
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Simulation Results

### Day 1 — Larmor Precession and Relaxation

![Day 1](figures/day1_larmor_precession.png)

A spin tipped 90° into the transverse plane precesses at the off-resonance frequency (100 Hz) while Mx, My decay with T₂ = 80 ms and Mz recovers with T₁ = 1.5 s. The FID envelope matches the analytical e⁻ᵗ/T₂ curve to 4 decimal places — verifying solver accuracy.

---

### Day 2 — Hard π Pulse: On-Resonance vs Off-Resonance

![Day 2](figures/day2_hard_pulse.png)

A rectangular π pulse (τ = 0.5 ms, Ω₀ = 1 kHz) achieves near-perfect inversion on-resonance (Mz = −0.997) but fails rapidly off-resonance. At ±1 kHz offset, Mz becomes positive — complete inversion failure. This is the fundamental limitation motivating adiabatic and STA approaches.

---

### Day 3 — Adiabatic Pulse and the Adiabatic Condition

![Day 3](figures/day3_adiabatic_pulse.png)

The linear-chirp adiabatic pulse succeeds when the **adiabatic condition** is satisfied:

$$\left|\frac{d\theta}{dt}\right| \ll \omega_\text{eff}, \quad \theta(t) = \arctan\!\left(\frac{\Omega_0}{\delta(t)}\right)$$

| Pulse | τ | Adiabaticity ratio | Final M_z |
|-------|---|--------------------|-----------|
| Slow  | 20 ms | 0.080 ✓ satisfied | −0.911 |
| Fast  | 2 ms  | 0.796 ✗ **violated** | −0.603 |

The slow pulse achieves broad bandwidth (robust across ±3 kHz). The fast pulse is both low-fidelity and bandwidth-limited. This is the **adiabatic paradox** that STA resolves.

---

### Day 4 — Shortcuts to Adiabaticity: Counterdiabatic Driving

![Day 4](figures/day4_sta_cd_driving.png)

The CD correction term for a linear-chirp sweep is derived analytically:

$$\omega_y(t) = -\frac{d\theta}{dt} = -\frac{2\,\Omega_0\,\Delta_\text{max}}{\tau\,\bigl(\delta(t)^2 + \Omega_0^2\bigr)}$$

This is implemented as a phase-modulated quadrature component of the existing RF channel — **no exotic hardware required**, compatible with standard clinical MRI scanners.

#### Key Result

| Pulse | Duration | Final M_z | Fidelity |
|-------|----------|-----------|----------|
| Slow adiabatic | 20 ms | −0.911 | Limited by T₂ decay |
| Fast conventional | 2 ms | −0.603 | ✗ Diabatic failure |
| **Fast STA/CD** | **2 ms** | **−0.988** | **✓ Near-perfect** |

**The STA pulse achieves a 10× speed-up while matching the fidelity of the slow adiabatic pulse.**

#### B₁ Robustness

Across ±20% B₁ field variation (realistic for clinical scanners):

| Pulse | Mean Final M_z | Std Dev |
|-------|----------------|---------|
| Slow adiabatic | −0.908 | 0.009 |
| Fast conventional | −0.588 | 0.037 |
| **Fast STA/CD** | **−0.986** | **0.004** |

STA is both faster and more robust to hardware imperfections than the conventional fast pulse.

---

## How to Run

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Run each simulation**
```bash
python day1_larmor_precession.py
python day2_hard_pulse.py
python day3_adiabatic_pulse.py
python day4_sta_cd_driving.py
```

Each script saves its figure to `figures/` and prints self-verification values to the terminal.

> **Note:** Scripts must be run from inside the `STA-Spin-Dynamics/` directory so the `figures/` subfolder path resolves correctly.

---

## The Physics Argument in One Paragraph

In fMRI applications involving neural stimulation (TMS-fMRI, DBS-fMRI), RF pulse duration directly determines the contamination of BOLD signal by stimulation artifacts. Shorter pulses reduce artifact overlap windows — but conventional adiabatic pulses cannot be shortened without violating the adiabatic condition and losing inversion fidelity. Counterdiabatic driving sidesteps this contradiction entirely: by adding a quadrature RF component whose time dependence is dictated by the geometry of the instantaneous Hamiltonian eigenstate, diabatic transitions are cancelled by construction rather than by slowing the pulse. The simulation here provides a direct numerical demonstration of this principle using a realistic biological tissue model (grey matter, 3T MRI).

---

## Author

**Sudipto Roy**  
MSc in Applied Physics and Electronics  
Jahangirnagar University, Bangladesh  
Research interests: medical physics, MRI pulse design, quantum control  
📧 diptoroy994@gmail.com  
🐙 [github.com/SuDiptoRoy994](https://github.com/SuDiptoRoy994)

---

## License

MIT — see [LICENSE](LICENSE)
