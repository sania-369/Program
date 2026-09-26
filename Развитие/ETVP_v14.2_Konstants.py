#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP v14.2 KONSTANTS TRACKER + ИТОГ
================================================================================
Прогон 10000 тактов, вывод каждые 1000.
В конце — средняя ошибка по каждой константе и общая средняя.
================================================================================
"""

import numpy as np
import time
from collections import deque
import sys

# =============================================================================
# 0. БАЗИС
# =============================================================================

GLOBAL_PHI = (1.0 + np.sqrt(5.0)) / 2.0
GLOBAL_PI  = np.pi
GLOBAL_SQ3 = np.sqrt(3.0)
GLOBAL_SQ2 = np.sqrt(2.0)

GLOBAL_C_MIN = 1.0 / (GLOBAL_PHI ** 10)
GLOBAL_C_MAX = 1.0 - 1.0 / (GLOBAL_PHI ** 20)

C_FFS = 1
S_cycle = 0.00000001
EPSILON_FFS = 0.01
K_HYPER = 30.0

W_ALPHA = (GLOBAL_PHI**12) * (GLOBAL_PI**-4) * (GLOBAL_SQ3**3) * 2
W_MASS  = (GLOBAL_PHI**5)  * (GLOBAL_PI**3)  * (GLOBAL_SQ3**4) * 0.5
W_G     = (GLOBAL_PHI**-43) * (GLOBAL_PI**-1) * (GLOBAL_SQ3**-5) * 2

IDX_ALPHA = 7
IDX_MASS  = 2
IDX_G     = 3

GAMMA = 1.0 / (GLOBAL_PHI ** 12)
ETA   = 1.0 / (GLOBAL_PHI ** 10)

NOISE_BASE = 0.001
E_VACUUM = 25.81  # МэВ

# =============================================================================
# 1. УПРУГОСТЬ
# =============================================================================

def etve_hyperbolic(C, c_min=GLOBAL_C_MIN, c_max=GLOBAL_C_MAX, k=K_HYPER):
    E = (C - c_min) / (c_max - c_min + 1e-12)
    E_norm = E / (1.0 + k * E) * (1.0 + k)
    return c_min + E_norm * (c_max - c_min)

# =============================================================================
# 2. 26 КОНСТАНТ
# =============================================================================

def compute_26_constants(alpha_inv, mass_ratio, C_op, S_op):
    PHI = GLOBAL_PHI; PI = GLOBAL_PI; SQ3 = GLOBAL_SQ3
    const = {}
    m_e_MeV = E_VACUUM * (2**12 - SQ3**4 * PI**3) / (PHI**20 * 2 * PI**2 + PI**5)
    
    const["m_e"] = m_e_MeV
    const["m_mu"] = m_e_MeV * (PI * PHI**3 * SQ3 + 1/(3*PHI))
    const["m_tau"] = m_e_MeV * ((alpha_inv/PI) * PHI**4 * SQ3 - PI**2/2)
    
    m_u = m_e_MeV * (2/3 * PI * PHI * SQ3)
    m_d = m_e_MeV * (1/3 * PI**2 * PHI**2 + SQ3/4)
    m_s = m_u * (PI * PHI**2 * SQ3 + alpha_inv/(2*PI**2))
    m_p_MeV = m_e_MeV * mass_ratio
    m_c = m_p_MeV * (PHI**4/PI + SQ3/(2*PI**2))
    m_b = m_e_MeV * (alpha_inv * PI * PHI**3 + SQ3**4 * PI**2)
    m_t = m_p_MeV * (alpha_inv/(PI*SQ3) * PHI**4 - SQ3**2)
    const.update({"m_u":m_u,"m_d":m_d,"m_s":m_s,"m_c":m_c,"m_b":m_b,"m_t":m_t})
    
    m_W_MeV = m_e_MeV * np.sqrt(alpha_inv/(PI*SQ3) * PHI**10)
    const["m_W"] = m_W_MeV / 1000
    const["m_Z"] = const["m_W"] * np.sqrt(1 + SQ3/(PI*PHI**4))
    v = 246.22
    const["m_H"] = v/np.sqrt(2) * (1 - 1/(PI*PHI**3*SQ3))
    
    const["sin_th12"] = SQ3/(PI*PHI**3) * (1 - 1/alpha_inv)
    const["sin_th23"] = SQ3/(PI*PHI**8)
    const["sin_th13"] = const["sin_th23"] / (alpha_inv * PHI)
    const["delta_CP"] = np.degrees(PI/2 * (1 + 1/(PHI**2*SQ3)))
    
    alpha_em = 1/alpha_inv
    const["alpha_inv"] = alpha_inv
    const["alpha_w"] = alpha_em * (1 + PI*PHI**4/SQ3)
    const["alpha_s"] = alpha_em / (1 - 4 * alpha_em * np.log(PHI**4*SQ3))
    
    const["sin2_th12_nu"] = 1/PHI**3 * (1 - SQ3/alpha_inv)
    const["sin2_th23_nu"] = 0.5 - 1/(PI*PHI**4)
    const["sin2_th13_nu"] = PI**2 / (alpha_inv/PHI)**2
    const["delta_CP_nu"] = -np.degrees(PI * (1 - 1/(PHI**3*SQ3)))
    
    m_H = const["m_H"]
    const["mu_sq"] = -(m_H/2 * (1 - 1/(PI*PHI**3*SQ3)))**2
    const["lambda_H"] = 1/4 * (1 - 1/(PI*PHI**3*SQ3))**2
    const["theta_QCD"] = (SQ3**2 - 3) / (PI*PHI**4)
    
    return const

# =============================================================================
# 3. CODATA
# =============================================================================

CODATA = {
    "m_e": 0.51099895, "m_mu": 105.6583755, "m_tau": 1776.86,
    "m_u": 2.16, "m_d": 4.67, "m_s": 93.4,
    "m_c": 1270.0, "m_b": 4180.0, "m_t": 172500.0,
    "m_W": 80.377, "m_Z": 91.1876, "m_H": 125.25,
    "sin_th12": 0.22500, "sin_th23": 0.04182, "sin_th13": 0.00360,
    "delta_CP": 69.2,
    "alpha_inv": 137.035999084, "alpha_w": 0.0338, "alpha_s": 0.1180,
    "sin2_th12_nu": 0.307, "sin2_th23_nu": 0.454, "sin2_th13_nu": 0.0220,
    "delta_CP_nu": -155.0,
    "mu_sq": -7825.0, "lambda_H": 0.1291, "theta_QCD": 0.0,
}

# Список всех 26 в порядке вывода
ALL_KEYS = [
    "m_e","m_mu","m_tau",
    "m_u","m_d","m_s","m_c","m_b","m_t",
    "m_W","m_Z","m_H",
    "sin_th12","sin_th23","sin_th13","delta_CP",
    "alpha_inv","alpha_w","alpha_s",
    "sin2_th12_nu","sin2_th23_nu","sin2_th13_nu","delta_CP_nu",
    "mu_sq","lambda_H","theta_QCD"
]

NAMES = {
    "m_e":"m_e","m_mu":"m_μ","m_tau":"m_τ",
    "m_u":"m_u","m_d":"m_d","m_s":"m_s","m_c":"m_c","m_b":"m_b","m_t":"m_t",
    "m_W":"m_W","m_Z":"m_Z","m_H":"m_H",
    "sin_th12":"sin θ_12","sin_th23":"sin θ_23","sin_th13":"sin θ_13","delta_CP":"δ_CP",
    "alpha_inv":"1/α","alpha_w":"α_w","alpha_s":"α_s",
    "sin2_th12_nu":"sin²θ_12^ν","sin2_th23_nu":"sin²θ_23^ν",
    "sin2_th13_nu":"sin²θ_13^ν","delta_CP_nu":"δ_CP^ν",
    "mu_sq":"μ²","lambda_H":"λ_H","theta_QCD":"θ_QCD"
}

# =============================================================================
# 4. ЯДРО
# =============================================================================

class ETVEComplexCoreV142:
    def __init__(self, memory_depth=100):
        self.C_E8 = np.zeros((11, 11), dtype=float)
        self.C_E8[0:8, 0:8] = np.array([
            [ 2, -1,  0,  0,  0,  0,  0,  0],
            [-1,  2, -1,  0,  0,  0,  0,  0],
            [ 0, -1,  2, -1,  0,  0,  0,  0],
            [ 0,  0, -1,  2, -1,  0,  0,  0],
            [ 0,  0,  0, -1,  2, -1,  0, -1],
            [ 0,  0,  0,  0, -1,  2, -1,  0],
            [ 0,  0,  0,  0,  0, -1,  2,  0],
            [ 0,  0,  0,  0, -1,  0,  0,  2]
        ], dtype=float)
        eigvals_8, eigvecs_8 = np.linalg.eigh(self.C_E8[0:8, 0:8])
        idx = np.argsort(eigvals_8)
        self.E8_eigvals = eigvals_8[idx]
        self.E8_eigvecs = eigvecs_8[:, idx]
        self.alpha_base = self.E8_eigvals[IDX_ALPHA] * W_ALPHA
        self.mass_base  = self.E8_eigvals[IDX_MASS]  * W_MASS
        self.G_base     = self.E8_eigvals[IDX_G]     * W_G
        self.C = GLOBAL_C_MAX
        self.S = 0.15
        self.step_counter = 0
        self.G = self.G_base
        self.alpha_inv = self.alpha_base
        self.mass_ratio = self.mass_base
        self.real_particles = []
        self.virtual_particles = []
        self.memory_matrices = deque(maxlen=memory_depth)
        self.history = {"C": [], "S": [], "alpha": [], "mass_ratio": [], "G": []}
        self._build_memory_kernel()

    def _build_memory_kernel(self):
        lam = np.array([2.0,1.5,1.0,0.8,0.6,0.4,0.3,0.2,0.1,0.05,0.01])
        lam = lam / np.sum(lam)
        def kernel(tau): return np.sum(lam * np.exp(-lam * tau))
        self.memory_kernel = kernel

    def _apply_memory(self, M):
        if len(self.memory_matrices) == 0: return M
        me = np.zeros_like(M, dtype=complex); tw = 0.0
        for i,(mat,_) in enumerate(self.memory_matrices):
            tau = len(self.memory_matrices)-i
            w = self.memory_kernel(tau)
            me += w*np.array(mat,dtype=complex); tw += w
        if tw>0:
            me/=tw; ms=(self.C-GLOBAL_C_MIN)/(GLOBAL_C_MAX-GLOBAL_C_MIN)
            ms=np.clip(ms,0.0,1.0)
            return (1.0-ms)*M + ms*me
        return M

    def _build_complex_matrix(self):
        M = self.C_E8.copy() * (1.0 + 0.1 * (self.C - C_FFS))
        M = M * (1.0 + EPSILON_FFS * (self.C - C_FFS))
        eigvals, eigvecs = np.linalg.eigh(M[0:8,0:8])
        md = eigvecs[:, np.argmin(eigvals)]
        for i in range(8):
            M[i,i] += abs(np.dot(eigvecs[:,i],md))*(GLOBAL_C_MAX-self.C)/(GLOBAL_C_MAX-GLOBAL_C_MIN)
        for i in range(4,11): M[i,i] += self.C*0.1
        M = self._apply_memory(M)
        self.phi = (GLOBAL_PI/2.0)*(1.0-(self.C-GLOBAL_C_MIN)/(GLOBAL_C_MAX-GLOBAL_C_MIN))
        Mi = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                Mi[i,j] = M[i,j]*np.tan(self.phi+0.1*(i-j))
        Mi = (Mi+Mi.T)/2.0
        Mi = Mi + M*0.05*np.sin(self.S*self.step_counter)
        return M + 1j*Mi

    def _update_particles(self):
        if self.C > GLOBAL_C_MIN+(GLOBAL_C_MAX-GLOBAL_C_MIN)*0.15 and len(self.real_particles)==0:
            self.real_particles.append({"mass":0.1,"charge":0.1,"alive":True})
        if self.C < GLOBAL_C_MIN+(GLOBAL_C_MAX-GLOBAL_C_MIN)*0.05 and len(self.real_particles)>0:
            self.real_particles=[]
        if self.C > GLOBAL_C_MIN+(GLOBAL_C_MAX-GLOBAL_C_MIN)*0.10:
            if np.random.random()<0.01 and len(self.virtual_particles)<10:
                self.virtual_particles.append({"energy":np.random.uniform(0.1,1.0),"age":0,"alive":True})
        for v in self.virtual_particles[:]:
            v["age"]+=1
            if v["age"]>5 or np.random.random()<0.02:
                self.virtual_particles.remove(v)

    def update_field(self, dt):
        self.step_counter += 1
        M = self._build_complex_matrix()
        ev = np.linalg.eigvals(M); ev = ev[np.argsort(np.abs(ev))[::-1]]
        dC = self.C - C_FFS; dS = self.S - S_cycle
        am = 1.0+0.1*dC-0.05*dS
        mm = 1.0+0.05*dC-0.02*dS
        gm = 1.0-0.2*dC+0.1*dS
        self.alpha_inv = self.alpha_base * am
        self.mass_ratio = self.mass_base * mm
        self.G = self.G_base * gm
        self.memory_matrices.append((M,time.time()))
        return {"alpha_inv":self.alpha_inv,"mass_ratio":self.mass_ratio,"G":self.G}

    def evolve(self, entropy_flux=0.0, time_step=1.0):
        noise = NOISE_BASE*np.random.randn()
        self.C = self.C*(1.0-GAMMA)+GAMMA*C_FFS+noise*0.1
        self.S = self.S*(1.0-ETA)+ETA*S_cycle+noise*0.01
        self.S = max(0.0,min(1.0,self.S))
        self.C = etve_hyperbolic(self.C)
        self._update_particles()
        r = self.update_field(time_step)
        self.history["C"].append(self.C)
        self.history["S"].append(self.S)
        self.history["alpha"].append(r["alpha_inv"])
        self.history["mass_ratio"].append(r["mass_ratio"])
        self.history["G"].append(r["G"])
        return r

# =============================================================================
# 5. ВЫВОД РЕЕСТРА
# =============================================================================

def print_registry(step, const, C_val, S_val):
    print("\n" + "=" * 80)
    print(f"📊 ТАКТ {step:,} | C = {C_val:.6f} | S = {S_val:.8f}")
    print("=" * 80)
    print(f"{'Константа':<18} {'Модель':<18} {'CODATA/PDG':<18} {'Ошибка %':<10}")
    print("-" * 70)
    groups = [
        ("[I: ЛЕПТОНЫ]", ["m_e","m_mu","m_tau"], ".6f"),
        ("[II: КВАРКИ]", ["m_u","m_d","m_s","m_c","m_b","m_t"], ".4f"),
        ("[III: БОЗОНЫ]", ["m_W","m_Z","m_H"], ".4f"),
        ("[IV: CKM]", ["sin_th12","sin_th23","sin_th13","delta_CP"], ".6f"),
        ("[V: КАЛИБРОВОЧНЫЕ]", ["alpha_inv","alpha_w","alpha_s"], ".6f"),
        ("[VI: PMNS]", ["sin2_th12_nu","sin2_th23_nu","sin2_th13_nu","delta_CP_nu"], ".6f"),
        ("[VII: ХИГГС]", ["mu_sq","lambda_H","theta_QCD"], ".6f"),
    ]
    for title, keys, fmt in groups:
        print(f"\n{title}")
        for key in keys:
            mod = const[key]; cod = CODATA[key]
            err = abs(mod-cod)/abs(cod)*100 if cod!=0 else 0
            print(f"{NAMES[key]:<18} {mod:<18{fmt}} {cod:<18{fmt}} {err:<10.4f}")
    print("=" * 80)

# =============================================================================
# 6. ИТОГОВАЯ СВОДКА
# =============================================================================

def print_final_summary(all_errors):
    """
    all_errors — dict: key -> list of errors по всем выводам
    """
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СВОДКА: СРЕДНЯЯ ОШИБКА ПО КАЖДОЙ КОНСТАНТЕ")
    print("=" * 80)
    print(f"{'Константа':<18} {'Средняя ошибка %':<18} {'Мин %':<12} {'Макс %':<12}")
    print("-" * 70)
    
    means = []
    for key in ALL_KEYS:
        errs = np.array(all_errors[key])
        m = np.mean(errs); mn = np.min(errs); mx = np.max(errs)
        means.append(m)
        print(f"{NAMES[key]:<18} {m:<18.4f} {mn:<12.4f} {mx:<12.4f}")
    
    print("-" * 70)
    print(f"{'ОБЩАЯ СРЕДНЯЯ:':<18} {np.mean(means):<18.4f}")
    print(f"{'МЕДИАНА:':<18} {np.median(means):<18.4f}")
    print("=" * 80)

# =============================================================================
# 7. ЗАПУСК
# =============================================================================

def run_and_report(n_steps=10000, log_every=1000):
    print("=" * 80)
    print("🌀 ETVP v14.2 KONSTANTS TRACKER + ИТОГ")
    print(f"   γ = 1/Φ¹² = {GAMMA:.6f}, η = 1/Φ¹⁰ = {ETA:.6f}")
    print(f"   k = 30 | E_vacuum = {E_VACUUM} МэВ")
    print(f"   Тактов: {n_steps:,}, вывод каждые {log_every:,}")
    print("=" * 80)

    model = ETVEComplexCoreV142(memory_depth=100)
    print(f"\n🔧 База (C = 1):")
    print(f"   1/α     = {model.alpha_base:.9f}")
    print(f"   m_p/m_e = {model.mass_base:.6f}")
    print(f"   G       = {model.G_base:.6e}\n")

    all_errors = {key: [] for key in ALL_KEYS}

    # Такт 0
    const = compute_26_constants(model.alpha_base, model.mass_base, model.C, model.S)
    for key in ALL_KEYS:
        cod = CODATA[key]
        err = abs(const[key]-cod)/abs(cod)*100 if cod!=0 else 0
        all_errors[key].append(err)
    print_registry(0, const, model.C, model.S)

    t0 = time.time()
    for i in range(n_steps):
        entropy_flux = 0.005*np.sin(i/7.0)+0.001*np.random.randn()
        result = model.evolve(entropy_flux, time_step=1.0)
        if (i+1) % log_every == 0:
            const = compute_26_constants(result["alpha_inv"], result["mass_ratio"], model.C, model.S)
            for key in ALL_KEYS:
                cod = CODATA[key]
                err = abs(const[key]-cod)/abs(cod)*100 if cod!=0 else 0
                all_errors[key].append(err)
            print_registry(i+1, const, model.C, model.S)
            elapsed = time.time()-t0
            print(f"  ⏱ {(i+1)/elapsed:.0f} такт/с | {elapsed:.1f} с")
            sys.stdout.flush()

    print_final_summary(all_errors)
    print("\n✅ ГОТОВО")

if __name__ == "__main__":
    run_and_report(n_steps=10000, log_every=1000)
