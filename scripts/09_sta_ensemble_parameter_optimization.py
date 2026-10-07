"""Tier 4: research prototype for ensemble STA parameter optimization.

IMPORTANT:
    This is NOT the paper's current experimental result and is NOT full OCT.
    It is a future-work prototype that optimizes only three pulse parameters:
        Omega0, Delta_max, and tau.

The objective averages inversion loss over a small B1/off-resonance ensemble
and adds soft penalties for peak RF-control and pulse duration.

Outputs:
    results/ensemble_optimization_history.csv
    results/ensemble_optimization_best.json
    figures/figure_T4_ensemble_optimization_convergence.png

Run from the scripts directory or any directory because paths are resolved
relative to this file.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution

from common_model import Params, simulate, simulate_final, inversion_fidelity, rf_metrics

OUT = Path(__file__).resolve().parents[1]
FIG = OUT / "figures"
RES = OUT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)

# Small ensemble for a laptop-friendly prototype.
B1_VALUES = np.array([0.85, 1.00, 1.15])
OFF_VALUES_KHZ = np.array([-2.0, 0.0, 2.0])
ENSEMBLE = [(b1, off) for b1 in B1_VALUES for off in OFF_VALUES_KHZ]

# Optimization weights. They are dimensionless and intentionally modest.
W_FID = 1.0
W_TAU = 0.03
W_PEAK = 0.03
W_JRF = 0.005

history: list[dict[str, float]] = []


def objective(x: np.ndarray) -> float:
    omega0_khz, delta_max_khz, tau_ms = map(float, x)
    p = Params(
        omega0=2.0 * np.pi * omega0_khz * 1000.0,
        delta_max=2.0 * np.pi * delta_max_khz * 1000.0,
    )
    tau = tau_ms / 1000.0

    fidelity_values = []
    for b1, off_khz in ENSEMBLE:
        traj = simulate_final(
            tau=tau,
            p=p,
            sta=True,
            b1_scale=b1,
            off_res_hz=off_khz * 1000.0,
            rtol=1e-7,
            atol=1e-9,
        )
        fidelity_values.append(inversion_fidelity(float(traj[2]), p))

    mean_fid = float(np.mean(fidelity_values))
    cost = rf_metrics(tau=tau, p=p, sta=True, n_points=3001)
    # Normalize costs against simple reference scales.
    peak_norm = cost["peak_total_omega"] / (2.0 * np.pi * 1000.0)
    j_norm = cost["J_RF"] / (2.0 * np.pi * 1000.0) ** 2 / 0.01

    value = (
        W_FID * (1.0 - mean_fid)
        + W_TAU * (tau_ms / 20.0)
        + W_PEAK * peak_norm
        + W_JRF * j_norm
    )
    history.append({
        "omega0_kHz": omega0_khz,
        "delta_max_kHz": delta_max_khz,
        "tau_ms": tau_ms,
        "mean_fidelity": mean_fid,
        "peak_control_normalized": peak_norm,
        "J_RF_normalized": j_norm,
        "objective": value,
    })
    return value


bounds = [
    (0.5, 2.0),   # Omega0 in kHz
    (2.0, 8.0),   # Delta_max in kHz
    (1.0, 10.0),  # tau in ms
]

result = differential_evolution(
    objective,
    bounds=bounds,
    seed=7,
    maxiter=int(os.getenv("STA_OPT_MAXITER", "12")),
    popsize=int(os.getenv("STA_OPT_POPSIZE", "6")),
    tol=1e-3,
    polish=True,
    updating="immediate",
    workers=1,
)

history_df = pd.DataFrame(history)
history_df.to_csv(RES / "ensemble_optimization_history.csv", index=False)

best = {
    "omega0_kHz": float(result.x[0]),
    "delta_max_kHz": float(result.x[1]),
    "tau_ms": float(result.x[2]),
    "objective": float(result.fun),
    "success": bool(result.success),
    "message": str(result.message),
    "warning": "Research prototype only. Not full optimal control and not a hardware/clinical result.",
}
(RES / "ensemble_optimization_best.json").write_text(json.dumps(best, indent=2))

# Plot running best objective.
history_df["running_best"] = history_df["objective"].cummin()
plt.figure(figsize=(8.5, 5.5))
plt.plot(np.arange(len(history_df)), history_df["running_best"])
plt.xlabel("Objective-function evaluations")
plt.ylabel("Best objective so far")
plt.title("Prototype Ensemble STA Optimization")
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.savefig(FIG / "figure_T4_ensemble_optimization_convergence.png", dpi=300, bbox_inches="tight")
plt.show()

print(json.dumps(best, indent=2))
