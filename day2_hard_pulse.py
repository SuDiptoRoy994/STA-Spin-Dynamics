"""
Day 2 — The Hard (Rectangular) pi Pulse
========================================
Author: Sudipto Roy

Applies a rectangular RF pulse for spin inversion (Mz: +1 -> -1).
Demonstrates that hard pulses work on-resonance but fail completely
off-resonance — directly motivating adiabatic and STA approaches.

Key physics: effective rotation axis tilts when delta != 0,
so the flip angle is not pi and inversion fails.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

T1, T2, M0 = 1.500, 0.080, 1.0
OMEGA = 2*np.pi*1000          # 1 kHz Rabi frequency
tau_pi = np.pi / OMEGA        # pi-pulse duration

def bloch_rf(t, M, delta):
    Mx, My, Mz = M
    return [
        delta*My - Mx/T2,
        -delta*Mx + OMEGA*Mz - My/T2,
        -OMEGA*My - (Mz-M0)/T1
    ]

def run(delta_off, n=500):
    sol = solve_ivp(bloch_rf, (0, tau_pi), [0., 0., M0],
                    t_eval=np.linspace(0, tau_pi, n), args=(delta_off,),
                    method='RK45', rtol=1e-9, atol=1e-11)
    return sol.t, sol.y

t_traj, M_traj = run(0.0)

offsets_hz = np.linspace(-2000, 2000, 200)
Mz_final = [run(o*2*np.pi)[1][2,-1] for o in offsets_hz]
omega_eff = np.sqrt(OMEGA**2 + (offsets_hz*2*np.pi)**2)
Mz_analytic = M0*(OMEGA/omega_eff)**2*np.cos(omega_eff*tau_pi) + M0*(offsets_hz*2*np.pi/omega_eff)**2

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
fig.suptitle(r'Day 2 — Hard $\pi$ Pulse: Inversion and Off-Resonance Sensitivity'
             f'\n$\\Omega_0$=1kHz, $\\tau_\\pi$={tau_pi*1e3:.2f}ms, grey matter 3T',
             fontsize=11, fontweight='bold')

ax = axes[0]
ax.plot(t_traj*1e3, M_traj[2], '#2C7BB6', lw=2.0, label=r'$M_z(t)$')
ax.plot(t_traj*1e3, M_traj[0], '#D7191C', lw=1.5, ls='--', alpha=0.7, label=r'$M_x(t)$')
ax.plot(t_traj*1e3, M_traj[1], '#1A9641', lw=1.5, ls=':', alpha=0.7, label=r'$M_y(t)$')
ax.axhline(-1.0, color='gray', lw=0.8, ls=':', alpha=0.6, label='Perfect inversion')
ax.set(xlabel='Time (ms)', ylabel='Magnetisation', title=r'(A) On-resonance: $M_z$ goes +1 to -1')
ax.legend(fontsize=9); ax.grid(True, alpha=0.25); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax = axes[1]
ax.plot(offsets_hz, Mz_final, '#2C7BB6', lw=2.0, label='Numerical (Bloch)')
ax.plot(offsets_hz, Mz_analytic, '#D7191C', lw=1.5, ls='--', alpha=0.8, label='Analytic')
ax.axhline(-1.0, color='gray', lw=0.8, ls=':', alpha=0.6, label='Perfect inversion')
ax.set(xlabel=r'$B_0$ off-resonance offset (Hz)', ylabel=r'Final $M_z$',
       title='(B) Off-resonance sensitivity\nFidelity collapses away from resonance')
ax.legend(fontsize=9); ax.grid(True, alpha=0.25); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('figures/day2_hard_pulse.png', dpi=200, bbox_inches='tight')
print(f"Saved: figures/day2_hard_pulse.png")
print(f"Final Mz (on-resonance): {M_traj[2,-1]:+.4f}  (perfect = -1.0000)")
