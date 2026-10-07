"""Tier 3: speed-performance-control-cost analysis.

Metrics:
    peak_total_omega = max sqrt(omega_x^2 + omega_y^2)
    J_RF = integral [omega_x^2 + omega_y^2] dt

J_RF is a control-cost proxy, NOT SAR.

Outputs:
    results/control_cost_sweep.csv
    figures/figure_T3_control_cost.png
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
    for label, sta in [("Conventional", False), ("STA_CD", True)]:
        traj = simulate_final(tau=tau, p=p, sta=sta)
        mz = float(traj[2])
        metrics = rf_metrics(tau=tau, p=p, sta=sta)
        rows.append({
            "pulse_duration_ms": tau_ms,
            "speedup_vs_20ms": 20.0 / tau_ms,
            "pulse": label,
            "final_Mz": mz,
            "inversion_fidelity": inversion_fidelity(mz, p),
            **metrics,
        })

df = pd.DataFrame(rows)
df.to_csv(RES / "control_cost_sweep.csv", index=False)

# Figure 1: peak control ratio relative to the conventional pulse at each duration.
conv = df[df["pulse"] == "Conventional"].set_index("pulse_duration_ms")
sta = df[df["pulse"] == "STA_CD"].set_index("pulse_duration_ms")
peak_ratio = sta["peak_total_omega"] / conv["peak_total_omega"]
j_ratio = sta["J_RF"] / conv["J_RF"]

plt.figure(figsize=(8.5, 5.5))
plt.plot(durations_ms, peak_ratio, label="STA/CD peak-control ratio")
plt.plot(durations_ms, j_ratio, label="STA/CD J_RF ratio")
plt.axhline(1.0, linestyle="--", linewidth=1)
plt.xlabel("Pulse duration (ms)")
plt.ylabel("STA/CD cost relative to conventional")
plt.title("Speed–Control-Cost Trade-off")
plt.grid(True, alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_T3_control_cost.png", dpi=300, bbox_inches="tight")
plt.show()

print("2 ms ratios:")
print(f"Peak control ratio = {peak_ratio.loc[2.0]:.4f}")
print(f"J_RF ratio = {j_ratio.loc[2.0]:.4f}")
