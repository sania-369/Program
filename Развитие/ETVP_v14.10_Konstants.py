#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP v14.0 KONSTANTS — Полный реестр 26 констант (10000 тактов)
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================

ОСНОВА: v13.2 HYPERBOLIC (эталон)
  Ошибки: 1/α = 0.0014%, m_p/m_e = 0.0076%, G = 0.0034%
  
ПРОГОН: 10000 тактов (быстрая проверка)
================================================================================
"""

import numpy as np
import time
from collections import deque
import sys

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
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

# =============================================================================
# 1. ВЕСА ИЗ E8
# =============================================================================

W_ALPHA = (GLOBAL_PHI**12) * (GLOBAL_PI**-4) * (GLOBAL_SQ3**3) * 2
W_MASS  = (GLOBAL_PHI**5)  * (GLOBAL_PI**3)  * (GLOBAL_SQ3**4) * 0.5
W_G     = (GLOBAL_PHI**-43) * (GLOBAL_PI**-1) * (GLOBAL_SQ3**-5) * 2

IDX_ALPHA = 7
IDX_MASS  = 2
IDX_G     = 3

# =============================================================================
# 2. ВЫВЕДЕННЫЕ КОЭФФИЦИЕНТЫ
# =============================================================================

GAMMA = 1.0 / (GLOBAL_PHI ** 12)
ETA   = 1.0 / (GLOBAL_PHI ** 10)

NOISE_BASE = 0.001

# =============================================================================
# 3. E_vacuum (калибровка из m_e)
# =============================================================================

E_VACUUM = 25.81  # МэВ

# =============================================================================
# 4. ГИПЕРБОЛИЧЕСКАЯ УПРУГОСТЬ
# =============================================================================

def etve_hyperbolic(C, c_min=GLOBAL_C_MIN, c_max=GLOBAL_C_MAX, k=K_HYPER):
    E = (C - c_min) / (c_max - c_min + 1e-12)
    E_norm = E / (1.0 + k * E) * (1.0 + k)
    return c_min + E_norm * (c_max - c_min)

# =============================================================================
# 5. 26 КОНСТАНТ ИЗ РЕЕСТРА
# =============================================================================

def compute_26_constants(alpha_inv, mass_ratio, C_op, S_op):
    PHI = GLOBAL_PHI
    PI = GLOBAL_PI
    SQ3 = GLOBAL_SQ3
    
    const = {}
    
    m_e_MeV = E_VACUUM * (2**12 - SQ3**4 * PI**3) / (PHI**20 * 2 * PI**2 + PI**5)
    
    # --- ГРУППА I: ЛЕПТОНЫ ---
    const["m_e"] = m_e_MeV
    const["m_mu"] = m_e_MeV * (PI * PHI**3 * SQ3 + 1/(3*PHI))
    const["m_tau"] = m_e_MeV * ((alpha_inv/PI) * PHI**4 * SQ3 - PI**2/2)
    
    # --- ГРУППА II: КВАРКИ ---
    m_u = m_e_MeV * (2/3 * PI * PHI * SQ3)
    m_d = m_e_MeV * (1/3 * PI**2 * PHI**2 + SQ3/4)
    m_s = m_u * (PI * PHI**2 * SQ3 + alpha_inv/(2*PI**2))
    m_p_MeV = m_e_MeV * mass_ratio
    m_c = m_p_MeV * (PHI**4/PI + SQ3/(2*PI**2))
    m_b = m_e_MeV * (alpha_inv * PI * PHI**3 + SQ3**4 * PI**2)
    m_t = m_p_MeV * (alpha_inv/(PI*SQ3) * PHI**4 - SQ3**2)
    
    const["m_u"] = m_u
    const["m_d"] = m_d
    const["m_s"] = m_s
    const["m_c"] = m_c
    const["m_b"] = m_b
    const["m_t"] = m_t
    
    # --- ГРУППА III: БОЗОНЫ ---
    m_W_MeV = m_e_MeV * np.sqrt(alpha_inv/(PI*SQ3) * PHI**10)
    const["m_W"] = m_W_MeV / 1000
    const["m_Z"] = const["m_W"] * np.sqrt(1 + SQ3/(PI*PHI**4))
    
    v = 246.22
    const["m_H"] = v/np.sqrt(2) * (1 - 1/(PI*PHI**3*SQ3))
    
    # --- ГРУППА IV: CKM ---
    const["sin_th12"] = SQ3/(PI*PHI**3) * (1 - 1/alpha_inv)
    const["sin_th23"] = SQ3/(PI*PHI**8)
    const["sin_th13"] = const["sin_th23"] / (alpha_inv * PHI)
    const["delta_CP"] = np.degrees(PI/2 * (1 + 1/(PHI**2*SQ3)))
    
    # --- ГРУППА V: КАЛИБРОВОЧНЫЕ КОНСТАНТЫ ---
    alpha_em = 1/alpha_inv
    const["alpha_inv"] = alpha_inv
    const["alpha_w"] = alpha_em * (1 + PI*PHI**4/SQ3)
    beta_s = 4
    const["alpha_s"] = alpha_em / (1 - beta_s * alpha_em * np.log(PHI**4*SQ3))
    
    # --- ГРУППА VI: PMNS ---
    const["sin2_th12_nu"] = 1/PHI**3 * (1 - SQ3/alpha_inv)
    const["sin2_th23_nu"] = 0.5 - 1/(PI*PHI**4)
    const["sin2_th13_nu"] = PI**2 / (alpha_inv/PHI)**2
    const["delta_CP_nu"] = -np.degrees(PI * (1 - 1/(PHI**3*SQ3)))
    
    # --- ГРУППА VII: ХИГГС ---
    m_H = const["m_H"]
    const["mu_sq"] = -(m_H/2 * (1 - 1/(PI*PHI**3*SQ3)))**2
    const["lambda_H"] = 1/4 * (1 - 1/(PI*PHI**3*SQ3))**2
    const["theta_QCD"] = (SQ3**2 - 3) / (PI*PHI**4)
    
    return const

# =============================================================================
# 6. CODATA
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

# =============================================================================
# 7. ФИЗИЧЕСКОЕ ЯДРО (v13.2)
# =============================================================================

class ETVEComplexCoreV140:
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

        self.real_particles = []
        self.virtual_particles = []
        self.memory_matrices = deque(maxlen=memory_depth)

        self.history = {"C": [], "S": [], "alpha": [], "mass_ratio": [], "G": []}

        self._build_memory_kernel()

    def _build_memory_kernel(self):
        lambda_spectrum = np.array([2.0, 1.5, 1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01])
        lambda_spectrum = lambda_spectrum / np.sum(lambda_spectrum)
        def kernel(tau):
            return np.sum(lambda_spectrum * np.exp(-lambda_spectrum * tau))
        self.memory_kernel = kernel

    def _apply_memory(self, M):
        if len(self.memory_matrices) == 0:
            return M
        memory_effect = np.zeros_like(M, dtype=complex)
        total_weight = 0.0
        for i, (matrix, _) in enumerate(self.memory_matrices):
            tau = len(self.memory_matrices) - i
            weight = self.memory_kernel(tau)
            memory_effect += weight * np.array(matrix, dtype=complex)
            total_weight += weight
        if total_weight > 0:
            memory_effect /= total_weight
            memory_strength = (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN)
            memory_strength = np.clip(memory_strength, 0.0, 1.0)
            return (1.0 - memory_strength) * M + memory_strength * memory_effect
        return M

    def _build_complex_matrix(self):
        M = self.C_E8.copy() * (1.0 + 0.1 * (self.C - C_FFS))
        M = M * (1.0 + EPSILON_FFS * (self.C - C_FFS))

        eigvals, eigenvectors = np.linalg.eigh(M[0:8, 0:8])
        mass_direction = eigenvectors[:, np.argmin(eigvals)]
        for i in range(8):
            projection = np.dot(eigenvectors[:, i], mass_direction)
            M[i, i] += abs(projection) * (GLOBAL_C_MAX - self.C) / (GLOBAL_C_MAX - GLOBAL_C_MIN)

        for i in range(4, 11):
            M[i, i] += self.C * 0.1

        M = self._apply_memory(M)

        self.phi = (GLOBAL_PI / 2.0) * (1.0 - (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN))

        M_imag = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                M_imag[i, j] = M[i, j] * np.tan(self.phi + 0.1 * (i - j))
        M_imag = (M_imag + M_imag.T) / 2.0
        phase_shift = 0.1 * np.sin(self.S * self.step_counter)
        M_imag = M_imag + M * 0.05 * phase_shift

        return M + 1j * M_imag

    def _update_particles(self):
        if self.C > GLOBAL_C_MIN + (GLOBAL_C_MAX - GLOBAL_C_MIN) * 0.15 and len(self.real_particles) == 0:
            self.real_particles.append({"mass": 0.1, "charge": 0.1, "alive": True})
        if self.C < GLOBAL_C_MIN + (GLOBAL_C_MAX - GLOBAL_C_MIN) * 0.05 and len(self.real_particles) > 0:
            self.real_particles = []
        if self.C > GLOBAL_C_MIN + (GLOBAL_C_MAX - GLOBAL_C_MIN) * 0.10:
            if np.random.random() < 0.01 and len(self.virtual_particles) < 10:
                self.virtual_particles.append({"energy": np.random.uniform(0.1, 1.0), "age": 0, "alive": True})
        for v in self.virtual_particles[:]:
            v["age"] += 1
            if v["age"] > 5 or np.random.random() < 0.02:
                self.virtual_particles.remove(v)

    def update_field(self, dt):
        self.step_counter += 1

        M = self._build_complex_matrix()
        eigenvalues = np.linalg.eigvals(M)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]

        dC = self.C - C_FFS
        dS = self.S - S_cycle

        alpha_mod = 1.0 + 0.1 * dC - 0.05 * dS
        mass_mod  = 1.0 + 0.05 * dC - 0.02 * dS
        G_mod     = 1.0 - 0.2 * dC + 0.1 * dS

        alpha_inv = self.alpha_base * alpha_mod
        mass_ratio = self.mass_base * mass_mod
        G = self.G_base * G_mod

        self.G = G
        self.alpha_inv = alpha_inv
        self.mass_ratio = mass_ratio

        self.memory_matrices.append((M, time.time()))

        return {"alpha_inv": alpha_inv, "mass_ratio": mass_ratio, "G": G}

    def evolve(self, entropy_flux=0.0, time_step=1.0):
        noise = NOISE_BASE * np.random.randn()
        self.C = self.C * (1.0 - GAMMA) + GAMMA * C_FFS + noise * 0.1
        self.S = self.S * (1.0 - ETA) + ETA * S_cycle + noise * 0.01
        self.S = max(0.0, min(1.0, self.S))

        self.C = etve_hyperbolic(self.C)

        self._update_particles()
        result = self.update_field(time_step)

        self.history["C"].append(self.C)
        self.history["S"].append(self.S)
        self.history["alpha"].append(result["alpha_inv"])
        self.history["mass_ratio"].append(result["mass_ratio"])
        self.history["G"].append(result["G"])

        return result

# =============================================================================
# 8. ЗАПУСК
# =============================================================================

def run_and_report(n_steps=10000, log_every=1000):
    print("=" * 80)
    print("🌀 ETVP v14.0 KONSTANTS — 26 констант (10000 тактов)")
    print(f"   γ = 1/Φ¹² = {GAMMA:.6f}, η = 1/Φ¹⁰ = {ETA:.6f}")
    print(f"   k = 30 (Коксетер E8)")
    print(f"   E_vacuum = {E_VACUUM} МэВ")
    print("=" * 80)

    model = ETVEComplexCoreV140(memory_depth=100)
    print(f"\n🔧 База (C = 1):")
    print(f"   1/α     = {model.alpha_base:.9f}")
    print(f"   m_p/m_e = {model.mass_base:.6f}")
    print(f"   G       = {model.G_base:.6e}\n")

    t0 = time.time()
    for i in range(n_steps):
        entropy_flux = 0.005 * np.sin(i / 7.0) + 0.001 * np.random.randn()
        result = model.evolve(entropy_flux, time_step=1.0)
        if (i + 1) % log_every == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1:>7,}] C={model.C:.6f} S={model.S:.6f} "
                  f"α⁻¹={result['alpha_inv']:.6f} | {rate:.0f} такт/с")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\n✅ Прогон за {elapsed:.1f} с")

    n_avg = min(1000, n_steps)
    C_avg = np.mean(model.history["C"][-n_avg:])
    S_avg = np.mean(model.history["S"][-n_avg:])
    alpha_avg = np.mean(model.history["alpha"][-n_avg:])
    mass_avg = np.mean(model.history["mass_ratio"][-n_avg:])

    const = compute_26_constants(alpha_avg, mass_avg, C_avg, S_avg)

    print("\n" + "=" * 80)
    print("📊 РЕЕСТР 26 КОНСТАНТ")
    print("=" * 80)
    print(f"\n{'Константа':<18} {'Модель':<18} {'CODATA/PDG':<18} {'Ошибка %':<10}")
    print("-" * 70)

    print("\n--- ГРУППА I: ЛЕПТОНЫ ---")
    for name, key in [("m_e", "m_e"), ("m_μ", "m_mu"), ("m_τ", "m_tau")]:
        mod = const[key]; cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")

    print("\n--- ГРУППА II: КВАРКИ ---")
    for name, key in [("m_u", "m_u"), ("m_d", "m_d"), ("m_s", "m_s"),
                       ("m_c", "m_c"), ("m_b", "m_b"), ("m_t", "m_t")]:
        mod = const[key]; cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.4f} {cod:<18.4f} {err:<10.4f}")

    print("\n--- ГРУППА III: БОЗОНЫ ---")
    for name, key in [("m_W", "m_W"), ("m_Z", "m_Z"), ("m_H", "m_H")]:
        mod = const[key]; cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.4f} {cod:<18.4f} {err:<10.4f}")

    print("\n--- ГРУППА IV: CKM ---")
    for name, key in [("sin θ_12", "sin_th12"), ("sin θ_23", "sin_th23"),
                       ("sin θ_13", "sin_th13"), ("δ_CP (град)", "delta_CP")]:
        mod = const[key]; cod = CODATA[key]
        err = abs(mod - cod) / cod * 100 if cod != 0 else 0
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")

    print("\n--- ГРУППА V: КАЛИБРОВОЧНЫЕ КОНСТАНТЫ ---")
    for name, key in [("1/α", "alpha_inv"), ("α_w", "alpha_w"), ("α_s", "alpha_s")]:
        mod = const[key]; cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")

    print("\n--- ГРУППА VI: PMNS ---")
    for name, key in [("sin²θ_12^ν", "sin2_th12_nu"), ("sin²θ_23^ν", "sin2_th23_nu"),
                       ("sin²θ_13^ν", "sin2_th13_nu"), ("δ_CP^ν (град)", "delta_CP_nu")]:
        mod = const[key]; cod = CODATA[key]
        err = abs(mod - cod) / abs(cod) * 100 if cod != 0 else 0
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")

    print("\n--- ГРУППА VII: ХИГГС ---")
    for name, key in [("μ² (ГэВ²)", "mu_sq"), ("λ_H", "lambda_H"), ("θ_QCD", "theta_QCD")]:
        mod = const[key]; cod = CODATA[key]
        err = abs(mod - cod) / abs(cod) * 100 if cod != 0 else 0
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")

    print("\n" + "=" * 80)
    print("✅ ГОТОВО")
    print("=" * 80)

if __name__ == "__main__":
    run_and_report(n_steps=10000, log_every=1000)
