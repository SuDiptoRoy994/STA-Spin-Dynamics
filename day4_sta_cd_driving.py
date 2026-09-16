"""
Day 4 — Shortcuts to Adiabaticity: Counterdiabatic (CD) Driving
================================================================
Author: Sudipto Roy

Adds the counterdiabatic correction to the fast adiabatic pulse.
This is the STA technique: an analytically derived quadrature RF component
that exactly cancels diabatic transitions, restoring high-fidelity
inversion at fast timescales.

The CD correction for a linear-chirp sweep delta(t) = Delta_max*(1 - 2t/tau):

    omega_y(t) = -d(theta)/dt
               = -2*Omega_0*Delta_max / (tau * (delta(t)^2 + Omega_0^2))

Key properties:
  (1) Analytically computable — no iterative optimisation
  (2) Hardware-realizable — phase-modulated component of existing RF channel
  (3) Mathematically guaranteed — exactly cancels diabatic transitions by construction

Results (grey matter 3T, tau_fast = 2ms):
  Slow adiabatic (20ms):  Mz = -0.911
  Fast conventional (2ms): Mz = -0.603   <- diabatic failure
  Fast STA/CD (2ms):       Mz = -0.988   <- fidelity fully restored
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.integrate import solve_ivp

T1, T2, M0   = 1.500, 0.080, 1.0
OMEGA_0       = 2*np.pi*1000
DELTA_MAX     = 2*np.pi*5000
TAU_SLOW      = 0.020
TAU_FAST      = 0.002

def delta(t, tau):
    return DELTA_MAX*(1 - 2*t/tau)

def cd_term(t, tau):
    d = delta(t, tau)
    return -2*OMEGA_0*DELTA_MAX / (tau*(d**2 + OMEGA_0**2))

def bloch(t, M, tau, with_cd):
    Mx, My, Mz = M
    d  = delta(t, tau)
    ox = OMEGA_0
    oy = cd_term(t, tau) if with_cd else 0.0
    return [d*My-oy*Mz-Mx/T2, -d*Mx+ox*Mz-My/T2, oy*Mx-ox*My-(Mz-M0)/T1]

def run(tau, with_cd, n=800):
    sol = solve_ivp(bloch,(0,tau),[0.,0.,M0],t_eval=np.linspace(0,tau,n),
                    args=(tau,with_cd),method='RK45',rtol=1e-9,atol=1e-11)
    return sol.t, sol.y

t_slow,M_slow = run(TAU_SLOW, False)
t_fast,M_fast = run(TAU_FAST, False)
t_sta, M_sta  = run(TAU_FAST, True)

b1_scales = np.linspace(0.80, 1.20, 80)
def rob_b1(tau, with_cd, b1):
    def ode(t,M):
        Mx,My,Mz=M; d=delta(t,tau); ox=OMEGA_0*b1
        oy=cd_term(t,tau) if with_cd else 0.
        return [d*My-oy*Mz-Mx/T2,-d*Mx+ox*Mz-My/T2,oy*Mx-ox*My-(Mz-M0)/T1]
    return solve_ivp(ode,(0,tau),[0.,0.,M0],t_eval=[0,tau],
                     method='RK45',rtol=1e-8,atol=1e-10).y[2,-1]

Mz_b1_slow = [rob_b1(TAU_SLOW,False,b) for b in b1_scales]
Mz_b1_fast = [rob_b1(TAU_FAST,False,b) for b in b1_scales]
Mz_b1_sta  = [rob_b1(TAU_FAST,True, b) for b in b1_scales]

t_wave  = np.linspace(1e-6, TAU_FAST-1e-6, 500)
oy_wave = np.array([cd_term(t,TAU_FAST) for t in t_wave])
d_wave  = np.array([delta(t,TAU_FAST)   for t in t_wave])

fig = plt.figure(figsize=(13, 9))
fig.suptitle('Day 4 — Shortcuts to Adiabaticity: Counterdiabatic Driving\n'
             r'$\Omega_0$=1kHz, $\Delta_{max}$=5kHz, $\tau_{fast}$=2ms, grey matter 3T',
             fontsize=11, fontweight='bold')
gs = gridspec.GridSpec(2,2,figure=fig,hspace=0.48,wspace=0.35)

ax = fig.add_subplot(gs[0,0])
ax.plot(t_wave*1e3, np.full_like(t_wave,OMEGA_0)/(2*np.pi*1e3), '#2C7BB6', lw=2.0,
        label=r'$\omega_x(t)$ (Rabi, both pulses)')
ax.plot(t_wave*1e3, np.abs(oy_wave)/(2*np.pi*1e3), '#1A9641', lw=2.0,
        label=r'$|\omega_y(t)|$ (CD correction, STA)')
ax.plot(t_wave*1e3, np.abs(d_wave)/(2*np.pi*1e3), '#D7191C', lw=1.5, ls='--', alpha=0.7,
        label=r'$|\delta(t)|$ (chirp)')
ax.set(xlabel='Time (ms)', ylabel='Frequency (kHz)',
       title='(A) RF waveforms\nCD correction = phase-modulated RF component')
ax.legend(fontsize=8); ax.grid(True,alpha=0.25)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax = fig.add_subplot(gs[0,1])
ax.plot(t_slow*1e3,M_slow[2],'#2C7BB6',lw=2.0,label=f'Slow ({int(TAU_SLOW*1e3)}ms)  Mz={M_slow[2,-1]:+.3f}')
ax.plot(t_fast*1e3,M_fast[2],'#D7191C',lw=2.0,ls='--',label=f'Fast conv. ({int(TAU_FAST*1e3)}ms)  Mz={M_fast[2,-1]:+.3f}')
ax.plot(t_sta*1e3, M_sta[2], '#1A9641',lw=2.5,label=f'Fast STA/CD ({int(TAU_FAST*1e3)}ms)  Mz={M_sta[2,-1]:+.3f} ✓')
ax.axhline(-1.0,color='gray',lw=0.8,ls=':',alpha=0.6)
ax.set(xlabel='Time (ms)', ylabel=r'$M_z$', title='(B) KEY RESULT: Mz(t)\nSTA restores full inversion at 10x speed')
ax.legend(fontsize=8.5); ax.set_ylim(-1.15,1.10); ax.grid(True,alpha=0.25)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

ax = fig.add_subplot(gs[1,:])
b1_pct = (b1_scales-1)*100
ax.plot(b1_pct,Mz_b1_slow,'#2C7BB6',lw=2.0,label=f'Slow adiabatic ({int(TAU_SLOW*1e3)}ms)')
ax.plot(b1_pct,Mz_b1_fast,'#D7191C',lw=2.0,ls='--',label=f'Fast conventional ({int(TAU_FAST*1e3)}ms)')
ax.plot(b1_pct,Mz_b1_sta, '#1A9641',lw=2.5,label=f'Fast STA/CD ({int(TAU_FAST*1e3)}ms)')
ax.axhline(-1.0,color='gray',lw=0.8,ls=':',alpha=0.6,label='Perfect inversion')
ax.set(xlabel=r'$B_1$ field deviation from nominal (%)', ylabel=r'Final $M_z$',
       title=r'(C) $B_1$ Inhomogeneity Robustness (±20% RF variation)'
             '\nSTA maintains near-perfect inversion across the full range')
ax.legend(fontsize=9.5); ax.set_ylim(-1.15,0.2); ax.grid(True,alpha=0.25)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

plt.savefig('figures/day4_sta_cd_driving.png', dpi=200, bbox_inches='tight')
print("Saved: figures/day4_sta_cd_driving.png")
print(f"\nFinal results:")
print(f"  Slow adiabatic  (20ms): Mz = {M_slow[2,-1]:+.4f}")
print(f"  Fast conv.       (2ms): Mz = {M_fast[2,-1]:+.4f}")
print(f"  Fast STA/CD      (2ms): Mz = {M_sta[2,-1]:+.4f}")
print(f"\n  B1 robustness STA: mean={np.mean(Mz_b1_sta):.4f}, std={np.std(Mz_b1_sta):.4f}")
