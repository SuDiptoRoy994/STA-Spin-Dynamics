"""Tier 2: numerical convergence study.

Outputs:
    results/numerical_convergence.csv
    figures/figure_T2_numerical_convergence.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common_model import Params, simulate, simulate_final

OUT = Path(__file__).resolve().parents[1]
FIG = OUT / "figures"
RES = OUT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)

p = Params()
tau = 2e-3
rtols = [1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-11]
ref_rtol = 1e-12
ref_conv = simulate_final(tau=tau, p=p, sta=False, rtol=ref_rtol, atol=1e-14)
ref_sta = simulate_final(tau=tau, p=p, sta=True, rtol=ref_rtol, atol=1e-14)
ref_conv_mz = float(ref_conv[2])
ref_sta_mz = float(ref_sta[2])

rows = []
for rtol in rtols:
    atol = rtol * 1e-2
    conv = simulate_final(tau=tau, p=p, sta=False, rtol=rtol, atol=atol)
    sta = simulate_final(tau=tau, p=p, sta=True, rtol=rtol, atol=atol)
    conv_mz = float(conv[2])
    sta_mz = float(sta[2])
    rows.append({
        "rtol": rtol,
        "atol": atol,
        "abs_error_Mz_conventional": abs(conv_mz - ref_conv_mz),
        "abs_error_Mz_STA_CD": abs(sta_mz - ref_sta_mz),
        "final_Mz_conventional": conv_mz,
        "final_Mz_STA_CD": sta_mz,
    })

df = pd.DataFrame(rows)
df.to_csv(RES / "numerical_convergence.csv", index=False)

plt.figure(figsize=(8.5, 5.5))
plt.loglog(df["rtol"], df["abs_error_Mz_conventional"], marker="o", label="Conventional")
plt.loglog(df["rtol"], df["abs_error_Mz_STA_CD"], marker="o", label="STA/CD")
plt.xlabel("Relative tolerance (rtol)")
plt.ylabel("Absolute error in final Mz")
plt.title("Numerical Convergence at 2 ms")
plt.grid(True, which="both", alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_T2_numerical_convergence.png", dpi=300, bbox_inches="tight")
plt.show()

print(df.to_string(index=False, float_format=lambda x: f"{x:.3e}"))
