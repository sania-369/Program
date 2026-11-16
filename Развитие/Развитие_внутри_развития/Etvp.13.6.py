#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP v13.6 — ВСЁ ИЗ ПЛОТНОСТИ, КОГЕРЕНТНОСТИ И ШУМА
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================
СУТЬ:
  rho_C = rho_full(C, S, K) — из C, S, K через гиперболу.
  m_e = rho_C * scale_factor — из плотности.
  m_p = m_e * mass_ratio — из E8.
  m_n = m_p + m_e * 2*alpha_inv * lambda_0/lambda_2 — из E8.
================================================================================
"""

import numpy as np
import math
import random
import time
from collections import deque
import matplotlib.pyplot as plt
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

# =============================================================================
# ГЛАВНЫЕ ПАРАМЕТРЫ
# =============================================================================
K_HYPER = 30.0
C_FFS = 1.0
S_cycle = 0.00000001
EPSILON_FFS = 0.01

# =============================================================================
# 1. ФОРМУЛЫ КОНСТАНТ ИЗ E8
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

CODATA_ALPHA = 137.035999084
CODATA_MASS  = 1836.15267343
CODATA_G     = 6.67430e-11
CODATA_NEUTRON = 939.56542052
CODATA_PROTON  = 938.27208816
CODATA_ELECTRON = 0.51099895

NOISE_BASE = 0.001

# =============================================================================
# 3. ГИПОТЕЗЫ ИЗ E8 ДЛЯ rho_C
# =============================================================================
RHO_0 = GLOBAL_PHI ** 20
RHO_MIN = RHO_0 * (GLOBAL_PHI ** -10)
RHO_MAX = RHO_0 * (1.0 - GLOBAL_PHI ** -20)
S_MAX = 30.0 * np.log(GLOBAL_PHI)
K_0 = 30.0
h = 30.0

# =============================================================================
# 4. ФУНКЦИЯ f: rho_C ИЗ C, S, K
# =============================================================================
def sigma_from_C(C, C_min=GLOBAL_C_MIN, C_max=GLOBAL_C_MAX, h=h):
    delta_C = C - C_min
    delta_C_max = C_max - C_min
    return delta_C / (delta_C_max * (1 + h) - h * delta_C)

def rho_from_C(C, rho_min=RHO_MIN, rho_max=RHO_MAX, C_min=GLOBAL_C_MIN, C_max=GLOBAL_C_MAX, h=h):
    sigma = sigma_from_C(C, C_min, C_max, h)
    return rho_min + (rho_max - rho_min) * sigma

def rho_full(C, S, K, rho_min=RHO_MIN, rho_max=RHO_MAX, C_min=GLOBAL_C_MIN, C_max=GLOBAL_C_MAX, h=h, S_max=S_MAX, K_0=K_0):
    rho_C = rho_from_C(C, rho_min, rho_max, C_min, C_max, h)
    return rho_C * (1.0 - S / S_max) * (K / K_0)

# =============================================================================
# 5. ГИПЕРБОЛИЧЕСКАЯ УПРУГОСТЬ (для C)
# =============================================================================
def etve_hyperbolic(C, c_min=GLOBAL_C_MIN, c_max=GLOBAL_C_MAX, k=K_HYPER):
    E = (C - c_min) / (c_max - c_min + 1e-12)
    E_norm = E / (1.0 + k * E) * (1.0 + k)
    return c_min + E_norm * (c_max - c_min)

# =============================================================================
# 6. КАЛИБРОВКА МАСШТАБА
# =============================================================================
# Калибровка при C = C_MAX, S = 0, K = 30
C_CAL = GLOBAL_C_MAX
S_CAL = 0.0
K_CAL = 30.0
RHO_CAL = rho_full(C_CAL, S_CAL, K_CAL)
SCALE_FACTOR = CODATA_ELECTRON / RHO_CAL

print("=" * 80)
print("КАЛИБРОВКА МАСШТАБА")
print("=" * 80)
print(f"C_CAL = {C_CAL:.15f}")
print(f"S_CAL = {S_CAL:.15f}")
print(f"K_CAL = {K_CAL:.1f}")
print(f"RHO_CAL = {RHO_CAL:.6f}")
print(f"SCALE_FACTOR = {SCALE_FACTOR:.6e}")
print("=" * 80)

# =============================================================================
# 7. ФИЗИЧЕСКОЕ ЯДРО
# =============================================================================
class ETVEComplexCoreV136:
    def __init__(self, memory_depth=100):
        self.Phi = GLOBAL_PHI
        self.pi = GLOBAL_PI
        self.Z_res = GLOBAL_SQ3

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

        self._derive_coeffs()

        self.euler_characteristic = 4.18
        self.coxeter_SU2 = 3
        self.coxeter_SU3 = 4

        self.C = GLOBAL_C_MAX
        self.S = 0.15
        self.step_counter = 0

        self.dt_real = 1.0
        self.dt_imag = 0.0
        self.phi = 0.0
        self.a = 1.0
        self.H = 0.0
        self.dark_energy = 0.0
        self.G = self.G_base

        # m_e, m_p, m_n — из rho_C
        self.m_e = 0.0
        self.m_p = 0.0
        self.m_n = 0.0
        self.E_binding = 0.0
        self.rho_C = 0.0

        self.real_particles = []
        self.virtual_particles = []
        self.memory = deque(maxlen=memory_depth)
        self.memory_matrices = deque(maxlen=memory_depth)

        self.history = {
            "C": [], "S": [], "dt_real": [], "dt_imag": [], "phi": [],
            "alpha": [], "mass_ratio": [], "G": [], "unification": [],
            "a": [], "H": [], "dark_energy": [], "m_n": [], "E_binding": [],
            "m_p": [], "m_e": [], "rho_C": []
        }

        self._build_memory_kernel()

    def _derive_coeffs(self):
        v7 = np.abs(self.E8_eigvecs[:, IDX_ALPHA])
        self.alpha_i_alpha = v7 / np.sum(v7)

        v2 = np.abs(self.E8_eigvecs[:, IDX_MASS])
        self.alpha_i_mass = v2 / np.sum(v2)

        v3 = np.abs(self.E8_eigvecs[:, IDX_G])
        self.alpha_i_G = v3 / np.sum(v3)

        sum_lambda = np.sum(self.E8_eigvals)
        self.beta_i_alpha = self.alpha_i_alpha * self.E8_eigvals[IDX_ALPHA] / sum_lambda
        self.beta_i_mass  = self.alpha_i_mass  * self.E8_eigvals[IDX_MASS]  / sum_lambda
        self.beta_i_G     = self.alpha_i_G     * self.E8_eigvals[IDX_G]     / sum_lambda

        self.k_alpha_C = np.sum(self.alpha_i_alpha) / (GLOBAL_PHI ** 12) * 10
        self.k_alpha_S = np.sum(self.beta_i_alpha) / (GLOBAL_PHI ** 10) * 10
        self.k_mass_C = np.sum(self.alpha_i_mass) / (GLOBAL_PHI ** 12) * 10
        self.k_mass_S = np.sum(self.beta_i_mass) / (GLOBAL_PHI ** 10) * 10
        self.k_G_C = np.sum(self.alpha_i_G) / (GLOBAL_PHI ** 12) * 10
        self.k_G_S = np.sum(self.beta_i_G) / (GLOBAL_PHI ** 10) * 10

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
        ffs_correction = 1.0 + EPSILON_FFS * (self.C - C_FFS)
        M = M * ffs_correction

        eigvals, eigenvectors = np.linalg.eigh(M[0:8, 0:8])
        mass_direction = eigenvectors[:, np.argmin(eigvals)]
        for i in range(8):
            projection = np.dot(eigenvectors[:, i], mass_direction)
            M[i, i] += abs(projection) * (GLOBAL_C_MAX - self.C) / (GLOBAL_C_MAX - GLOBAL_C_MIN)

        for i in range(4, 11):
            M[i, i] += self.C * 0.1

        particle_contribution = np.zeros(11)
        for p in self.real_particles:
            if p.get("alive", True):
                particle_contribution[0] += p.get("mass", 0.1) * 10
                particle_contribution[1] += p.get("charge", 0.1)
        M[0, :] += particle_contribution * 0.01

        M = self._apply_memory(M)

        self.phi = (self.pi / 2.0) * (1.0 - (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN))

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
            if random.random() < 0.01 and len(self.virtual_particles) < 10:
                self.virtual_particles.append({"energy": random.uniform(0.1, 1.0), "age": 0, "alive": True})
        for v in self.virtual_particles[:]:
            v["age"] += 1
            if v["age"] > 5 or random.random() < 0.02:
                self.virtual_particles.remove(v)

    def _compute_neutron(self, alpha_inv):
        lambda_0 = self.E8_eigvals[0]
        lambda_2 = self.E8_eigvals[2]
        E_binding = self.m_e * 2.0 * alpha_inv * lambda_0 / lambda_2
        m_n = self.m_p + E_binding
        self.E_binding = E_binding
        self.m_n = m_n
        return m_n, E_binding

    def update_field(self, dt):
        self.step_counter += 1

        M = self._build_complex_matrix()
        eigenvalues = np.linalg.eigvals(M)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]

        dC = self.C - C_FFS
        dS = self.S - S_cycle

        # Модуляция из E8
        mod_alpha = 1.0 + self.k_alpha_C * dC - self.k_alpha_S * dS
        mod_mass  = 1.0 + self.k_mass_C * dC - self.k_mass_S * dS
        mod_G     = 1.0 + self.k_G_C * dC - self.k_G_S * dS

        alpha_inv = self.alpha_base * mod_alpha
        mass_ratio = self.mass_base * mod_mass
        G = self.G_base * mod_G

        # --- ВЫЧИСЛЕНИЕ rho_C ИЗ C, S, K ---
        self.rho_C = rho_full(self.C, self.S, K_HYPER)

        # --- ВЫЧИСЛЕНИЕ m_e ИЗ rho_C ---
        self.m_e = self.rho_C * SCALE_FACTOR

        # --- ВЫЧИСЛЕНИЕ m_p ИЗ m_e И mass_ratio ---
        self.m_p = self.m_e * mass_ratio

        # --- ВЫЧИСЛЕНИЕ m_n ИЗ m_p И alpha_inv ---
        m_n, E_binding = self._compute_neutron(alpha_inv)

        dt_complex = eigenvalues[10] / eigenvalues[0]
        dt_real = np.real(dt_complex)
        dt_imag = np.imag(dt_complex)
        phi = np.arctan2(dt_imag, dt_real)

        a_new = np.real(eigenvalues[0] / (eigenvalues[1] + eigenvalues[2] + 1e-12))
        if self.a > 0:
            da = a_new - self.a
            H = da / (self.a * dt + 1e-12)
        else:
            H = 0.0
        self.a = a_new
        self.H = H
        rho = len(self.real_particles) + 0.1 * len(self.virtual_particles)
        dark_energy = max(0.0, H**2 - (8 * self.pi * G * rho) / 3.0)

        alpha_em = 1.0 / alpha_inv
        M_U1 = M[0:1, 0:1]
        M_SU2 = M[0:2, 0:2]
        M_SU3 = M[0:3, 0:3]

        def casimir(M_sub):
            trace = np.trace(M_sub)
            trace2 = np.trace(M_sub @ M_sub)
            if abs(trace) < 1e-12:
                return 1.0
            return trace2 / (trace**2 + 1e-12)

        C_U1 = casimir(M_U1)
        C_SU2 = casimir(M_SU2)
        C_SU3 = casimir(M_SU3)

        beta_em = (1.0 / (C_U1 + 0.5)) * self.euler_characteristic
        beta_s = (1.0 / (C_SU3 + 0.5)) * self.coxeter_SU3
        beta_w = (1.0 / (C_SU2 + 0.5)) * self.coxeter_SU2

        E = (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN)
        E = np.clip(E, 1e-6, 1.0)
        log_ratio = np.log(1.0 / E)

        alpha_s = alpha_em / (1.0 + beta_s * alpha_em * log_ratio)
        alpha_w = alpha_em / (1.0 + beta_w * alpha_em * log_ratio)

        couplings = np.array([alpha_em, alpha_s, alpha_w])
        couplings = couplings / (np.mean(couplings) + 1e-12)
        unification = 1.0 - np.std(couplings)

        self.dt_real = dt_real
        self.dt_imag = dt_imag
        self.G = G
        self.dark_energy = dark_energy
        self.alpha_inv = alpha_inv
        self.mass_ratio = mass_ratio
        self.unification_measure = unification
        self.Eigenvalues = eigenvalues

        self.memory_matrices.append((M, time.time()))

        return {
            "alpha_inv": alpha_inv,
            "mass_ratio": mass_ratio,
            "dt_real": dt_real,
            "dt_imag": dt_imag,
            "phi": phi,
            "G": G,
            "a": self.a,
            "H": H,
            "dark_energy": dark_energy,
            "alpha_em": alpha_em,
            "alpha_s": alpha_s,
            "alpha_w": alpha_w,
            "unification": unification,
            "m_n": m_n,
            "E_binding": E_binding,
            "m_p": self.m_p,
            "m_e": self.m_e,
            "rho_C": self.rho_C
        }

    def evolve(self, entropy_flux=0.0, time_step=1.0):
        noise = NOISE_BASE * np.random.randn()
        self.C = self.C * (1.0 - GAMMA) + GAMMA * C_FFS + noise * 0.1
        self.S = self.S * (1.0 - ETA) + ETA * S_cycle + noise * 0.01
        self.S = max(0.0, min(1.0, self.S))

        self.C = etve_hyperbolic(self.C, k=K_HYPER)

        self._update_particles()
        result = self.update_field(time_step)

        self.history["C"].append(self.C)
        self.history["S"].append(self.S)
        self.history["dt_real"].append(result["dt_real"])
        self.history["dt_imag"].append(result["dt_imag"])
        self.history["phi"].append(result["phi"])
        self.history["alpha"].append(result["alpha_inv"])
        self.history["mass_ratio"].append(result["mass_ratio"])
        self.history["G"].append(result["G"])
        self.history["a"].append(result["a"])
        self.history["H"].append(result["H"])
        self.history["dark_energy"].append(result["dark_energy"])
        self.history["unification"].append(result["unification"])
        self.history["m_n"].append(result["m_n"])
        self.history["E_binding"].append(result["E_binding"])
        self.history["m_p"].append(result["m_p"])
        self.history["m_e"].append(result["m_e"])
        self.history["rho_C"].append(result["rho_C"])

        return result

# =============================================================================
# 8. ЗАПУСК
# =============================================================================
def demo_ffs_calibration(n_steps=10_000, log_every=1_000):
    print("=" * 80)
    print("🌀 ETVP v13.6 — ВСЁ ИЗ ПЛОТНОСТИ, КОГЕРЕНТНОСТИ И ШУМА")
    print(f"   Тактов: {n_steps:,}")
    print(f"   K_HYPER = {K_HYPER}")
    print(f"   C_FFS = {C_FFS}, S_cycle = {S_cycle}")
    print(f"   RHO_0 = {RHO_0:.6f}, S_MAX = {S_MAX:.6f}")
    print(f"   SCALE_FACTOR = {SCALE_FACTOR:.6e}")
    print("=" * 80)

    model = ETVEComplexCoreV136(memory_depth=100)
    print(f"\n🔧 База (C = 1):")
    print(f"   1/α     = {model.alpha_base:.9f}")
    print(f"   m_p/m_e = {model.mass_base:.6f}")
    print(f"   G       = {model.G_base:.6e}")
    print(f"   RHO_0   = {RHO_0:.6f} (Phi^20)")
    print(f"   RHO_MIN = {RHO_MIN:.6f} (Phi^10)")
    print(f"   RHO_MAX = {RHO_MAX:.6f} (Phi^20 - 1)")
    print(f"   S_MAX   = {S_MAX:.6f} (h * ln(Phi))")

    t0 = time.time()
    for i in range(n_steps):
        entropy_flux = 0.005 * np.sin(i / 7.0) + 0.001 * np.random.randn()
        result = model.evolve(entropy_flux, time_step=1.0)
        if (i + 1) % log_every == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1:>7,}] C={model.C:.6f} S={model.S:.6f} "
                  f"alpha_inv={result['alpha_inv']:.6f} m_p/m_e={result['mass_ratio']:.4f} "
                  f"G={result['G']:.4e} rho_C={result['rho_C']:.6f} "
                  f"m_e={result['m_e']:.6f} m_p={result['m_p']:.6f} m_n={result['m_n']:.6f} "
                  f"| {rate:.0f} такт/с")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\n✅ Прогон завершён за {elapsed:.1f} с")

    n_avg = 1000
    print("\n--- РЕЗУЛЬТАТЫ (последние 1000 тактов) ---")
    print(f"1/α    = {np.mean(model.history['alpha'][-n_avg:]):.9f} ± {np.std(model.history['alpha'][-n_avg:]):.9f}")
    print(f"m_p/m_e  = {np.mean(model.history['mass_ratio'][-n_avg:]):.6f} ± {np.std(model.history['mass_ratio'][-n_avg:]):.6f}")
    print(f"G      = {np.mean(model.history['G'][-n_avg:]):.6e} ± {np.std(model.history['G'][-n_avg:]):.6e}")
    print(f"m_n    = {np.mean(model.history['m_n'][-n_avg:]):.6f} ± {np.std(model.history['m_n'][-n_avg:]):.6f}")
    print(f"m_p    = {np.mean(model.history['m_p'][-n_avg:]):.6f} ± {np.std(model.history['m_p'][-n_avg:]):.6f}")
    print(f"m_e    = {np.mean(model.history['m_e'][-n_avg:]):.6f} ± {np.std(model.history['m_e'][-n_avg:]):.6f}")
    print(f"rho_C  = {np.mean(model.history['rho_C'][-n_avg:]):.6f} ± {np.std(model.history['rho_C'][-n_avg:]):.6f}")

    print("\n--- ОШИБКИ ---")
    a_err = abs(np.mean(model.history['alpha'][-n_avg:]) - CODATA_ALPHA) / CODATA_ALPHA * 100
    m_err = abs(np.mean(model.history['mass_ratio'][-n_avg:]) - CODATA_MASS) / CODATA_MASS * 100
    G_err = abs(np.mean(model.history['G'][-n_avg:]) - CODATA_G) / CODATA_G * 100
    n_err = abs(np.mean(model.history['m_n'][-n_avg:]) - CODATA_NEUTRON) / CODATA_NEUTRON * 100
    p_err = abs(np.mean(model.history['m_p'][-n_avg:]) - CODATA_PROTON) / CODATA_PROTON * 100
    e_err = abs(np.mean(model.history['m_e'][-n_avg:]) - CODATA_ELECTRON) / CODATA_ELECTRON * 100
    print(f"   1/α     : {a_err:.6f}%")
    print(f"   m_p/m_e : {m_err:.6f}%")
    print(f"   G       : {G_err:.6f}%")
    print(f"   m_n     : {n_err:.6f}%")
    print(f"   m_p     : {p_err:.6f}% (из E8 через rho_C)")
    print(f"   m_e     : {e_err:.6f}% (из rho_C)")

    # Графики
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].plot(model.history["alpha"], color='blue', linewidth=0.5)
    axes[0, 0].axhline(CODATA_ALPHA, color='red', linestyle='--', label='CODATA')
    axes[0, 0].set_title('1/α(t)')
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(model.history["mass_ratio"], color='green', linewidth=0.5)
    axes[0, 1].axhline(CODATA_MASS, color='red', linestyle='--', label='CODATA')
    axes[0, 1].set_title('m_p/m_e(t)')
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(np.array(model.history["G"]) * 1e11, color='orange', linewidth=0.5)
    axes[0, 2].axhline(CODATA_G * 1e11, color='red', linestyle='--', label='CODATA')
    axes[0, 2].set_title('G(t) · 10¹¹')
    axes[0, 2].legend(fontsize=8)
    axes[0, 2].grid(alpha=0.3)

    axes[1, 0].plot(model.history["m_e"], color='purple', linewidth=0.5)
    axes[1, 0].axhline(CODATA_ELECTRON, color='red', linestyle='--', label='CODATA')
    axes[1, 0].set_title('m_e(t)')
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(model.history["m_p"], color='brown', linewidth=0.5)
    axes[1, 1].axhline(CODATA_PROTON, color='red', linestyle='--', label='CODATA')
    axes[1, 1].set_title('m_p(t)')
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(model.history["m_n"], color='cyan', linewidth=0.5)
    axes[1, 2].axhline(CODATA_NEUTRON, color='red', linestyle='--', label='CODATA')
    axes[1, 2].set_title('m_n(t)')
    axes[1, 2].legend(fontsize=8)
    axes[1, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('etvp_v136_from_rho.png', dpi=150)
    plt.show()

    print("\n✅ Калибровка завершена.")

if __name__ == "__main__":
    demo_ffs_calibration(n_steps=10_000, log_every=1_000)
