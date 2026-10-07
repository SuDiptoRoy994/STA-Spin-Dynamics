"""Tier 2: off-resonance robustness at 2 ms.

Outputs:
    results/off_resonance_2ms.csv
    figures/figure_T2_off_resonance_2ms.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common_model import Params, simulate, simulate_final, inversion_fidelity

OUT = Path(__file__).resolve().parents[1]
FIG = OUT / "figures"
RES = OUT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)

p = Params()
tau = 2e-3
offsets = np.linspace(-5.0, 5.0, 201)  # kHz

rows = []
for off_khz in offsets:
    off_hz = off_khz * 1000.0
    for label, sta in [("Conventional", False), ("STA_CD", True)]:
        traj = simulate_final(tau=tau, p=p, sta=sta, off_res_hz=off_hz)
        mz = float(traj[2])
        rows.append({
            "off_resonance_kHz": off_khz,
            "pulse": label,
            "final_Mz": mz,
            "inversion_fidelity": inversion_fidelity(mz, p),
        })

df = pd.DataFrame(rows)
df.to_csv(RES / "off_resonance_2ms.csv", index=False)

plt.figure(figsize=(8.5, 5.5))
for label in ["Conventional", "STA_CD"]:
    part = df[df["pulse"] == label]
    plt.plot(part["off_resonance_kHz"], part["inversion_fidelity"], label=label)
plt.axhline(0.90, linestyle="--", linewidth=1, label="0.90 target")
plt.xlabel("Static off-resonance (kHz)")
plt.ylabel("Target-state inversion fidelity")
plt.title("2-ms Off-Resonance Robustness")
plt.grid(True, alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_T2_off_resonance_2ms.png", dpi=300, bbox_inches="tight")
plt.show()

print(df.groupby("pulse")["inversion_fidelity"].agg(["min", "max", "mean"]))
