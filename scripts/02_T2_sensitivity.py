"""Tier 2: sensitivity to transverse relaxation time T2.

Outputs:
    results/T2_sensitivity.csv
    figures/figure_T2_T2_sensitivity.png
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

T2_values_ms = np.linspace(20.0, 160.0, 71)
rows = []

for T2_ms in T2_values_ms:
    p = Params(T2=T2_ms / 1000.0)
    for tau_ms, label, sta in [
        (20.0, "Conventional_20ms", False),
        (2.0, "Conventional_2ms", False),
        (2.0, "STA_CD_2ms", True),
    ]:
        traj = simulate_final(tau=tau_ms / 1000.0, p=p, sta=sta)
        mz = float(traj[2])
        rows.append({
            "T2_ms": T2_ms,
            "case": label,
            "final_Mz": mz,
            "inversion_fidelity": inversion_fidelity(mz, p),
        })

df = pd.DataFrame(rows)
df.to_csv(RES / "T2_sensitivity.csv", index=False)

plt.figure(figsize=(8.5, 5.5))
for label in ["Conventional_20ms", "Conventional_2ms", "STA_CD_2ms"]:
    part = df[df["case"] == label]
    plt.plot(part["T2_ms"], part["inversion_fidelity"], label=label.replace("_", " "))
plt.xlabel("T2 (ms)")
plt.ylabel("Target-state inversion fidelity")
plt.title("Sensitivity to Transverse Relaxation Time")
plt.grid(True, alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_T2_T2_sensitivity.png", dpi=300, bbox_inches="tight")
plt.show()
