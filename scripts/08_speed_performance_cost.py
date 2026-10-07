"""Tier 3: combined speed-performance-cost summary figure.

Outputs:
    results/speed_performance_cost.csv
    figures/figure_T3_speed_performance_cost.png

This is a compact decision figure for presentations to a professor. It plots
inversion fidelity and the STA control-cost ratios against speedup.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common_model import Params, simulate, simulate_final, inversion_fidelity, rf_metrics

OUT = Path(__file__).resolve().parents[1]
FIG = OUT / "figures"
RES = OUT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)

p = Params()
durations_ms = np.arange(1.0, 20.0001, 0.25)
rows = []

for tau_ms in durations_ms:
    tau = tau_ms / 1000.0
    conv = simulate_final(tau=tau, p=p, sta=False)
    sta = simulate_final(tau=tau, p=p, sta=True)
    f_conv = inversion_fidelity(float(conv[2]), p)
    f_sta = inversion_fidelity(float(sta[2]), p)
    c_conv = rf_metrics(tau, p, False)
    c_sta = rf_metrics(tau, p, True)
    rows.append({
        "pulse_duration_ms": tau_ms,
        "speedup_vs_20ms": 20.0 / tau_ms,
        "fidelity_conventional": f_conv,
        "fidelity_STA_CD": f_sta,
        "peak_control_ratio_STA_CD": c_sta["peak_total_omega"] / c_conv["peak_total_omega"],
        "J_RF_ratio_STA_CD": c_sta["J_RF"] / c_conv["J_RF"],
    })

df = pd.DataFrame(rows)
df.to_csv(RES / "speed_performance_cost.csv", index=False)

plt.figure(figsize=(9.0, 5.8))
plt.plot(df["speedup_vs_20ms"], df["fidelity_conventional"], label="Conventional fidelity")
plt.plot(df["speedup_vs_20ms"], df["fidelity_STA_CD"], label="STA/CD fidelity")
plt.xlabel("Speedup relative to 20-ms reference")
plt.ylabel("Target-state inversion fidelity")
plt.title("Rapid Inversion: Speed and Performance")
plt.grid(True, alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_T3_speed_performance_cost.png", dpi=300, bbox_inches="tight")
plt.show()
