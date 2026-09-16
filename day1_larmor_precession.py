"""
Day 1 — Larmor Precession and the Bloch Equations
===================================================
Author: Sudipto Roy

Simulates a single nuclear spin (proton) placed in a static magnetic field B0.
With no RF pulse applied, the spin precesses around B0 at the Larmor frequency.

Physical model — Bloch equations in the rotating frame (T1/T2 relaxation):
    dMx/dt =  delta*My            - Mx/T2
    dMy/dt = -delta*Mx + Omega*Mz - My/T2
    dMz/dt =           -Omega*My  - (Mz - M0)/T1

Today: Omega=0 (no RF). Spin starts tilted 90 deg. Watch precession and decay.
Tissue parameters: grey matter at 3T (T1=1.5s, T2=80ms).
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

T1, T2, M0 = 1.500, 0.080, 1.0
delta = 2 * np.pi * 100   # 100 Hz off-resonance

def bloch(t, M):
    Mx, My, Mz = M
    return [
        delta*My - Mx/T2,
        -delta*Mx - My/T2,
        -(Mz - M0)/T1
    ]

t_eval = np.linspace(0, 0.300, 3000)
sol = solve_ivp(bloch, (0, 0.300), [M0, 0.0, 0.0],
                t_eval=t_eval, method='RK45', rtol=1e-9, atol=1e-11)
t, Mx, My, Mz = sol.t, sol.y[0], sol.y[1], sol.y[2]
M_transverse = np.sqrt(Mx**2 + My**2)

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
fig.suptitle('Day 1 — Larmor Precession and Bloch Equation Relaxation\n'
             r'Off-resonance spin ($\delta$=100 Hz), grey matter 3T: '
             r'$T_1$=1.5s, $T_2$=80ms', fontsize=12, fontweight='bold')
t_ms = t * 1e3

ax = axes[0,0]
ax.plot(t_ms, Mx, '#E74C3C', lw=1.5, label=r'$M_x$')
ax.plot(t_ms, My, '#3498DB', lw=1.5, label=r'$M_y$')
ax.set(xlabel='Time (ms)', ylabel='Magnetisation', title=r'(A) $M_x$, $M_y$ — precession and T2 decay')
ax.legend(); ax.grid(True, alpha=0.25); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax = axes[0,1]
ax.plot(t_ms, M_transverse, '#8E44AD', lw=2.0)
ax.plot(t_ms, np.exp(-t/T2), 'k--', lw=1.2, alpha=0.6, label=r'$e^{-t/T_2}$ theory')
ax.set(xlabel='Time (ms)', ylabel=r'$|M_{xy}|$', title=r'(B) FID signal envelope')
ax.legend(fontsize=9); ax.grid(True, alpha=0.25); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax = axes[1,0]
ax.plot(t_ms, Mz, '#27AE60', lw=2.0)
ax.plot(t_ms, M0*(1-np.exp(-t/T1)), 'k--', lw=1.2, alpha=0.6, label=r'$M_0(1-e^{-t/T_1})$ theory')
ax.set(xlabel='Time (ms)', ylabel=r'$M_z$', title=r'(C) Longitudinal T1 recovery')
ax.legend(fontsize=9); ax.grid(True, alpha=0.25); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax3d = fig.add_subplot(2, 2, 4, projection='3d')
idx = t <= 0.050
ax3d.plot(Mx[idx], My[idx], Mz[idx], '#2C3E50', lw=1.5, alpha=0.85)
ax3d.scatter([Mx[0]], [My[0]], [Mz[0]], color='#E74C3C', s=50, label='Start')
ax3d.scatter([Mx[idx][-1]], [My[idx][-1]], [Mz[idx][-1]], color='#27AE60', s=50, label='50ms')
ax3d.set(xlabel=r'$M_x$', ylabel=r'$M_y$', zlabel=r'$M_z$', title='(D) Bloch sphere (50ms)')
ax3d.legend(fontsize=8)

plt.tight_layout()
plt.savefig('figures/day1_larmor_precession.png', dpi=200, bbox_inches='tight')
print("Saved: figures/day1_larmor_precession.png")
idx_T2 = np.argmin(np.abs(t - T2))
print(f"Self-check — |M_xy| at t=T2: {M_transverse[idx_T2]:.4f} (theory e^-1 = {np.exp(-1):.4f})")
