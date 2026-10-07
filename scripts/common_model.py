"""Shared Bloch/STA model used by the Tier 2-4 simulations.

Model convention:
    dM/dt = M x Omega + relaxation
    Omega = (omega_x, omega_y, delta)

The CD waveform is designed from the nominal linear chirp. Robustness
perturbations (B1 scaling and static off-resonance) are applied to the
actual dynamics without redesigning the nominal CD waveform.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class Params:
    T1: float = 1.5
    T2: float = 0.080
    M0: float = 1.0
    omega0: float = 2.0 * np.pi * 1000.0
    delta_max: float = 2.0 * np.pi * 5000.0


def linear_delta(t: np.ndarray | float, tau: float, p: Params) -> np.ndarray | float:
    """Nominal linear chirp detuning in rad/s."""
    return p.delta_max * (1.0 - 2.0 * np.asarray(t) / tau)


def actual_delta(
    t: np.ndarray | float,
    tau: float,
    p: Params,
    off_res_hz: float = 0.0,
) -> np.ndarray | float:
    """Actual detuning = designed chirp + static frequency offset."""
    return linear_delta(t, tau, p) + 2.0 * np.pi * off_res_hz


def theta_nominal(t: np.ndarray | float, tau: float, p: Params) -> np.ndarray | float:
    """Nominal effective-field angle used to construct the CD waveform."""
    d = linear_delta(t, tau, p)
    return np.arctan2(p.omega0, d)


def theta_dot_nominal(t: np.ndarray | float, tau: float, p: Params) -> np.ndarray | float:
    """Analytic derivative dtheta/dt for the nominal linear chirp."""
    d = linear_delta(t, tau, p)
    return 2.0 * p.omega0 * p.delta_max / (tau * (d**2 + p.omega0**2))


def cd_omega_y(t: np.ndarray | float, tau: float, p: Params) -> np.ndarray | float:
    """Counterdiabatic quadrature component for the nominal pulse."""
    return -theta_dot_nominal(t, tau, p)


def effective_omega(t: np.ndarray | float, tau: float, p: Params) -> np.ndarray | float:
    """Magnitude of the nominal effective field for the conventional chirp."""
    d = linear_delta(t, tau, p)
    return np.sqrt(p.omega0**2 + d**2)


def adiabaticity_ratio(tau: float, p: Params) -> float:
    """Maximum model-specific |theta_dot|/omega_eff for the linear chirp."""
    return 2.0 * p.delta_max / (tau * p.omega0**2)


def inversion_fidelity(mz_final: float, p: Params) -> float:
    """Target-state inversion overlap for target Bloch vector (0,0,-1)."""
    return 0.5 * (1.0 - mz_final / p.M0)


def control_components(
    t: np.ndarray | float,
    tau: float,
    p: Params,
    sta: bool,
    b1_scale: float = 1.0,
) -> Tuple[np.ndarray | float, np.ndarray | float]:
    """Return actual RF control components used by the simulation.

    The same B1 scale multiplies both quadratures in the robustness studies.
    """
    omega_x = b1_scale * p.omega0
    omega_y = b1_scale * cd_omega_y(t, tau, p) if sta else np.zeros_like(np.asarray(t, dtype=float))
    if np.ndim(t) == 0:
        omega_y = float(omega_y)
    return omega_x, omega_y


def bloch_rhs(
    t: float,
    M: np.ndarray,
    tau: float,
    p: Params,
    sta: bool,
    b1_scale: float = 1.0,
    off_res_hz: float = 0.0,
    relaxation: bool = True,
) -> np.ndarray:
    """Right-hand side of the dissipative rotating-frame Bloch equations."""
    mx, my, mz = M
    d = float(actual_delta(t, tau, p, off_res_hz))
    omega_x, omega_y = control_components(t, tau, p, sta, b1_scale)

    dmx = d * my - omega_y * mz
    dmy = -d * mx + omega_x * mz
    dmz = omega_y * mx - omega_x * my

    if relaxation:
        dmx -= mx / p.T2
        dmy -= my / p.T2
        dmz -= (mz - p.M0) / p.T1

    return np.array([dmx, dmy, dmz], dtype=float)


def simulate(
    tau: float,
    p: Params,
    sta: bool,
    b1_scale: float = 1.0,
    off_res_hz: float = 0.0,
    relaxation: bool = True,
    n_points: int = 2001,
    rtol: float = 1e-9,
    atol: float = 1e-11,
    method: str = "DOP853",
) -> tuple[np.ndarray, np.ndarray]:
    """Integrate the Bloch equations and return time points and magnetization."""
    if tau <= 0:
        raise ValueError("Pulse duration tau must be positive.")
    if n_points < 2:
        raise ValueError("n_points must be at least 2.")
    t = np.linspace(0.0, tau, n_points)
    y0 = np.array([0.0, 0.0, p.M0], dtype=float)
    sol = solve_ivp(
        bloch_rhs,
        (0.0, tau),
        y0,
        t_eval=t,
        args=(tau, p, sta, b1_scale, off_res_hz, relaxation),
        method=method,
        rtol=rtol,
        atol=atol,
    )
    if not sol.success:
        raise RuntimeError(f"ODE integration failed: {sol.message}")
    return sol.t, sol.y.T


def simulate_final(
    tau: float,
    p: Params,
    sta: bool,
    b1_scale: float = 1.0,
    off_res_hz: float = 0.0,
    relaxation: bool = True,
    rtol: float = 1e-9,
    atol: float = 1e-11,
    method: str = "DOP853",
) -> np.ndarray:
    """Integrate the model but request only the final state for fast sweeps."""
    if tau <= 0:
        raise ValueError("Pulse duration tau must be positive.")
    y0 = np.array([0.0, 0.0, p.M0], dtype=float)
    sol = solve_ivp(
        bloch_rhs,
        (0.0, tau),
        y0,
        args=(tau, p, sta, b1_scale, off_res_hz, relaxation),
        method=method,
        rtol=rtol,
        atol=atol,
    )
    if not sol.success:
        raise RuntimeError(f"ODE integration failed: {sol.message}")
    return sol.y[:, -1].copy()


def final_state(**kwargs) -> np.ndarray:
    """Convenience wrapper returning the final magnetization only."""
    _, traj = simulate(**kwargs)
    return traj[-1]


def rf_metrics(
    tau: float,
    p: Params,
    sta: bool,
    b1_scale: float = 1.0,
    n_points: int = 10001,
) -> dict[str, float]:
    """Calculate simple RF-control cost proxies for a pulse."""
    t = np.linspace(0.0, tau, n_points)
    omega_x, omega_y = control_components(t, tau, p, sta, b1_scale)
    total = np.sqrt(np.asarray(omega_x) ** 2 + np.asarray(omega_y) ** 2)
    j_rf = float(np.trapezoid(total**2, t))
    return {
        "peak_omega_x": float(np.max(np.abs(omega_x))),
        "peak_omega_y": float(np.max(np.abs(omega_y))),
        "peak_total_omega": float(np.max(total)),
        "J_RF": j_rf,
    }
