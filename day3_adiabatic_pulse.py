"""
Day 3 — The Adiabatic Pulse and the Adiabatic Condition
=========================================================
Author: Sudipto Roy

Linear-chirp adiabatic inversion pulse. The RF frequency sweeps across
resonance, and the spin follows the effective field — IF the pulse is slow.

Adiabatic condition:  |d(theta)/dt| << omega_eff
    theta(t) = atan2(Omega_0, delta(t))   (eigenstate angle)

For a linear chirp, the critical ratio is:
    max|d(theta)/dt| / omega_eff = 2*Delta_max / (tau * Omega_0)

When tau is too short this ratio exceeds 1 -> diabatic transitions -> failure.
This is the adiabatic paradox: speed and fidelity are mutually exclusive.
STA resolves it in Day 4.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

T1, T2, M0 = 1.500, 0.080, 1.0
OMEGA_0   = 2*np.pi*1000
DELTA_MAX = 2*np.pi*5000
TAU_SLOW, TAU_FAST = 0.020, 0.002

for tau, label in [(TAU_SLOW,'Slow'),(TAU_FAST,'Fast')]:
    t_ = np.linspace(1e-7, tau-1e-7, 5000)
    d_ = DELTA_MAX*(1-2*t_/tau)
    oe = np.sqrt(d_**2+OMEGA_0**2)
    ratio = (2*OMEGA_0*DELTA_MAX/(tau*(d_**2+OMEGA_0**2)) / oe).max()
    print(f"{label} (tau={tau*1e3:.0f}ms): max|dtheta/dt|/omega_eff = {ratio:.4f}  "
          f"({'satisfied' if ratio<0.15 else 'VIOLATED'})")

def bloch_ad(t, M, tau):
    Mx, My, Mz = M
    d = DELTA_MAX*(1-2*t/tau)
    return [d*My-Mx/T2, -d*Mx+OMEGA_0*Mz-My/T2, -OMEGA_0*My-(Mz-M0)/T1]

def run(tau, n=800):
    sol = solve_ivp(bloch_ad,(0,tau),[0.,0.,M0],t_eval=np.linspace(0,tau,n),
                    args=(tau,),method='RK45',rtol=1e-9,atol=1e-11)
    return sol.t, sol.y

t_slow,M_slow = run(TAU_SLOW)
t_fast,M_fast = run(TAU_FAST)

offsets_hz = np.linspace(-3000,3000,100)
def rob(tau, off, n=400):
    def ode(t,M):
        Mx,My,Mz=M; d=DELTA_MAX*(1-2*t/tau)+off*2*np.pi
        return [d*My-Mx/T2,-d*Mx+OMEGA_0*Mz-My/T2,-OMEGA_0*My-(Mz-M0)/T1]
    return solve_ivp(ode,(0,tau),[0.,0.,M0],t_eval=[0,tau],
                     method='RK45',rtol=1e-8,atol=1e-10).y[2,-1]

Mz_rs = [rob(TAU_SLOW,o) for o in offsets_hz]
Mz_rf = [rob(TAU_FAST,o) for o in offsets_hz]

fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
fig.suptitle('Day 3 — Adiabatic Pulse: The Adiabatic Condition and Speed Limit\n'
             r'$\Omega_0$=1kHz, $\Delta_{max}$=5kHz, grey matter 3T', fontsize=11, fontweight='bold')

ax = axes[0]
ax.plot(t_slow*1e3,M_slow[2],'#2C7BB6',lw=2.0,label=f'Slow (tau={int(TAU_SLOW*1e3)}ms)  Mz={M_slow[2,-1]:+.3f}')
ax.plot(t_fast*1e3,M_fast[2],'#D7191C',lw=2.0,ls='--',label=f'Fast (tau={int(TAU_FAST*1e3)}ms)  Mz={M_fast[2,-1]:+.3f}')
ax.axhline(-1.0,color='gray',lw=0.8,ls=':',alpha=0.6,label='Perfect inversion')
ax.set(xlabel='Time (ms)',ylabel=r'$M_z$',title='(A) Mz(t): slow succeeds, fast fails (diabatic)')
ax.legend(fontsize=9); ax.set_ylim(-1.15,1.10); ax.grid(True,alpha=0.25)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax = axes[1]
ax.plot(offsets_hz,Mz_rs,'#2C7BB6',lw=2.0,label=f'Slow ({int(TAU_SLOW*1e3)}ms)')
ax.plot(offsets_hz,Mz_rf,'#D7191C',lw=2.0,ls='--',label=f'Fast ({int(TAU_FAST*1e3)}ms)')
ax.axhline(-1.0,color='gray',lw=0.8,ls=':',alpha=0.6)
ax.set(xlabel=r'$B_0$ offset (Hz)',ylabel=r'Final $M_z$',title='(B) Off-resonance robustness\nSlow=broadband; Fast=unreliable')
ax.legend(fontsize=9); ax.set_ylim(-1.15,0.3); ax.grid(True,alpha=0.25)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('figures/day3_adiabatic_pulse.png', dpi=200, bbox_inches='tight')
print(f"Saved: figures/day3_adiabatic_pulse.png")
