"""Tier 3: joint RF-amplitude and off-resonance robustness map at 2 ms.

The RF-amplitude scale multiplies BOTH RF quadratures in the STA case.
The static off-resonance is applied only to the actual dynamics; the nominal
CD waveform is not redesigned. This makes the map a true robustness test of
a fixed analytic pulse.

Outputs:
    results/B1_offresonance_2D.csv
    figures/figure_T3_conventional_B1_offresonance.png
    figures/figure_T3_STA_B1_offresonance.png
    figures/figure_T3_STA_minus_conventional.png
"""
from pathlib import Path
import os
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
b1_points = int(os.getenv("STA_B1_POINTS", "15"))
off_points = int(os.getenv("STA_OFF_POINTS", "31"))
b1_scales = np.linspace(0.80, 1.20, b1_points)
off_khz = np.linspace(-5.0, 5.0, off_points)

rows = []
for b1 in b1_scales:
    for off in off_khz:
        for label, sta in [("Conventional", False), ("STA_CD", True)]:
            traj = simulate_final(tau=tau, p=p, sta=sta, b1_scale=b1, off_res_hz=off * 1000.0)
            mz = float(traj[2])
            rows.append({
                "B1_scale": b1,
                "off_resonance_kHz": off,
                "pulse": label,
                "final_Mz": mz,
                "inversion_fidelity": inversion_fidelity(mz, p),
            })

df = pd.DataFrame(rows)
df.to_csv(RES / "B1_offresonance_2D.csv", index=False)

for label, filename, title in [
    ("Conventional", "figure_T3_conventional_B1_offresonance.png", "Conventional 2-ms Pulse: RF-Amplitude / Off-Resonance Map"),
    ("STA_CD", "figure_T3_STA_B1_offresonance.png", "STA/CD 2-ms Pulse: RF-Amplitude / Off-Resonance Map"),
]:
    part = df[df["pulse"] == label]
    grid = part.pivot(index="B1_scale", columns="off_resonance_kHz", values="inversion_fidelity").values
    plt.figure(figsize=(8.5, 5.5))
    plt.imshow(
        grid,
        origin="lower",
        aspect="auto",
        extent=[off_khz.min(), off_khz.max(), b1_scales.min(), b1_scales.max()],
        vmin=0.0,
        vmax=1.0,
    )
    plt.colorbar(label="Inversion fidelity")
    plt.xlabel("Static off-resonance (kHz)")
    plt.ylabel("RF amplitude scale, B1/B1$_0$")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(FIG / filename, dpi=300, bbox_inches="tight")
    plt.show()

conv = df[df["pulse"] == "Conventional"].pivot(index="B1_scale", columns="off_resonance_kHz", values="inversion_fidelity")
sta = df[df["pulse"] == "STA_CD"].pivot(index="B1_scale", columns="off_resonance_kHz", values="inversion_fidelity")
difference = sta.values - conv.values

plt.figure(figsize=(8.5, 5.5))
plt.imshow(
    difference,
    origin="lower",
    aspect="auto",
    extent=[off_khz.min(), off_khz.max(), b1_scales.min(), b1_scales.max()],
)
plt.colorbar(label="STA/CD minus conventional fidelity")
plt.xlabel("Static off-resonance (kHz)")
plt.ylabel("RF amplitude scale, B1/B1$_0$")
plt.title("Where Does STA/CD Improve the Conventional Pulse?")
plt.tight_layout()
plt.savefig(FIG / "figure_T3_STA_minus_conventional.png", dpi=300, bbox_inches="tight")
plt.show()
