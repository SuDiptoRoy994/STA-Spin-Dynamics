"""Tier 4: Bloch-vs-Lindblad validation prototype for a spin-1/2 system.

Purpose:
    Test whether the phenomenological Bloch model gives similar final
    inversion to a density-matrix Lindblad model for the same Hamiltonian.

IMPORTANT:
    This is a future-method validation exercise, not a replacement for the
    paper's present dissipative Bloch result.

Outputs:
    results/bloch_vs_lindblad.csv
    figures/figure_T4_bloch_vs_lindblad.png

Requires only NumPy, SciPy, and Matplotlib.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

from common_model import Params, simulate, cd_omega_y, actual_delta, inversion_fidelity

OUT = Path(__file__).resolve().parents[1]
FIG = OUT / "figures"
RES = OUT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)

I2 = np.eye(2, dtype=complex)
sx = np.array([[0, 1], [1, 0]], dtype=complex)
sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
sz = np.array([[1, 0], [0, -1]], dtype=complex)
splus = np.array([[0, 1], [0, 0]], dtype=complex)


def lindblad_rhs(t, y, tau, p, sta, b1_scale):
    rho = y[:4].reshape(2, 2)
    rho = rho.reshape(2, 2)
    d = actual_delta(t, tau, p, 0.0)
    ox = b1_scale * p.omega0
    oy = b1_scale * cd_omega_y(t, tau, p) if sta else 0.0
    # The Bloch convention used here is dM/dt = M x Omega.
    # For H=(h·sigma)/2, quantum mechanics gives dr/dt = h x r,
    # so use h=-Omega to match the Bloch sign convention.
    H = -0.5 * (ox * sx + oy * sy + d * sz)

    # The Bloch model relaxes Mz toward +M0. With our Hamiltonian sign
    # convention, use sigma_+ as the longitudinal relaxation jump.
    gamma1 = 1.0 / p.T1
    gamma_phi = max(0.0, 1.0 / p.T2 - 0.5 / p.T1)

    c1 = np.sqrt(gamma1) * splus
    cp = np.sqrt(gamma_phi / 2.0) * sz if gamma_phi > 0 else np.zeros((2, 2), complex)

    drho = -1j * (H @ rho - rho @ H)
    for c in (c1, cp):
        if np.any(c):
            cdagc = c.conj().T @ c
            drho += c @ rho @ c.conj().T - 0.5 * (cdagc @ rho + rho @ cdagc)

    return drho.reshape(-1)


def run_case(sta: bool) -> tuple[np.ndarray, np.ndarray]:
    p = Params()
    tau = 2e-3
    t = np.linspace(0.0, tau, 2001)
    rho0 = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    sol = solve_ivp(
        lindblad_rhs,
        (0.0, tau),
        rho0.reshape(-1),
        t_eval=t,
        args=(tau, p, sta, 1.0),
        method="RK45",
        rtol=1e-9,
        atol=1e-11,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    rhos = sol.y.T.reshape(-1, 2, 2)
    mz = np.real(np.trace(rhos @ sz, axis1=1, axis2=2))
    return t, mz

p = Params()
tau = 2e-3
rows = []

for label, sta in [("Conventional", False), ("STA_CD", True)]:
    _, bloch = simulate(tau=tau, p=p, sta=sta)
    _, lind = run_case(sta)
    rows.append({
        "pulse": label,
        "Bloch_final_Mz": float(bloch[-1, 2]),
        "Lindblad_final_Mz": float(lind[-1]),
        "absolute_difference": float(abs(bloch[-1, 2] - lind[-1])),
        "Lindblad_inversion_fidelity": inversion_fidelity(float(lind[-1]), p),
    })

df = pd.DataFrame(rows)
df.to_csv(RES / "bloch_vs_lindblad.csv", index=False)
print(df.to_string(index=False))

plt.figure(figsize=(8.5, 5.5))
for label, sta in [("Conventional", False), ("STA_CD", True)]:
    t, lind = run_case(sta)
    _, bloch = simulate(tau=tau, p=p, sta=sta)
    plt.plot(t * 1000.0, bloch[:, 2], label=f"{label} — Bloch")
    plt.plot(t * 1000.0, lind, linestyle="--", label=f"{label} — Lindblad")
plt.xlabel("Time (ms)")
plt.ylabel("Longitudinal magnetization Mz")
plt.title("Bloch and Lindblad Spin-Dynamics Comparison")
plt.grid(True, alpha=0.25)
plt.legend()
plt.tight_layout()
plt.savefig(FIG / "figure_T4_bloch_vs_lindblad.png", dpi=300, bbox_inches="tight")
plt.show()
