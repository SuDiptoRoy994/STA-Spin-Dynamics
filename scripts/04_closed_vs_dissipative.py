"""Tier 2: ablation of relaxation at 2 ms.

Compares closed/coherent dynamics with the dissipative Bloch model.
Outputs:
    results/closed_vs_dissipative.csv
    figures/figure_T2_closed_vs_dissipative.png
"""
from pathlib import Path
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
rows = []

for relaxation in [False, True]:
    regime = "Closed" if not relaxation else "Dissipative"
    for label, sta in [("Conventional", False), ("STA_CD", True)]:
        traj = simulate_final(tau=tau, p=p, sta=sta, relaxation=relaxation)
        mz = float(traj[2])
        rows.append({
            "regime": regime,
            "pulse": label,
            "final_Mz": mz,
            "inversion_fidelity": inversion_fidelity(mz, p),
        })

# Save summary
pd.DataFrame(rows).to_csv(RES / "closed_vs_dissipative.csv", index=False)
print(pd.DataFrame(rows).to_string(index=False))

# One figure: final fidelity bar-like point comparison without manual colors.
df = pd.DataFrame(rows)
plt.figure(figsize=(8.5, 5.5))
positions = range(len(df))
plt.scatter(list(positions), df["inversion_fidelity"])
plt.xticks(list(positions), [f"{r.regime}\n{r.pulse}" for r in df.itertuples()])
plt.ylabel("Target-state inversion fidelity")
plt.title("Effect of Removing Relaxation in the 2-ms Model")
plt.ylim(0.75, 1.02)
plt.grid(True, axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig(FIG / "figure_T2_closed_vs_dissipative.png", dpi=300, bbox_inches="tight")
plt.show()
