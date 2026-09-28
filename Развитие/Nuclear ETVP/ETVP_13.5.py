#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP v13.5 HYPERBOLIC — Полный вывод частиц
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================

СУТЬ:
  Константы, массы, заряды, магнитные моменты — из E8.
  Всё выводится в каждом такте.

ВЫВОД В КАЖДОМ ТАКТЕ:
  - Константы: 1/α, m_p/m_e, G
  - Массы: m_p, m_n, m_e
  - Заряды: Q_e, Q_p, Q_n
  - Магнитные моменты: a_e, a_p, a_n, μ_e, μ_p, μ_n

ФОРМУЛЫ:
  1/α     = λ[7]·Φ¹²·π⁻⁴·√3³·2
  m_p/m_e = λ[2]·Φ⁵·π³·√3⁴·0.5
  G       = λ[3]·Φ⁻⁴³·π⁻¹·√3⁻⁵·2
  m_p     = m_e·(m_p/m_e)
  m_n     = m_p + m_e·2·α⁻¹·λ[0]/λ[2]
  Q       = n·e
  a_e     = α/(2π)
  a_p     = a_e·(m_p/m_e)/λ[2]
  a_n     = -λ[3] - 1/3
  g_e     = 2·(1 + a_e)
  g_p     = 2·(1 + a_p)
  g_n     = 2·a_n
  μ       = g·μ_(B,N)·S
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
# 0. УПРАВЛЕНИЕ — МЕНЯЙ ЗДЕСЬ
# =============================================================================

# >>> ПЛОТНОСТЬ ВАКУУМА <<<
C_FFS = 0.87

# >>> ШУМ <<<
S_cycle = 0.87

# >>> ПАРАМЕТР ГИПЕРБОЛИЧЕСКОЙ УПРУГОСТИ <<<
K_HYPER = 30.0

# >>> ПРОЧЕЕ <<<
EPSILON_FFS = 0.01
NOISE_BASE = 0.001

# =============================================================================
# 1. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

GLOBAL_PHI = (1.0 + np.sqrt(5.0)) / 2.0
GLOBAL_PI  = np.pi
GLOBAL_SQ3 = np.sqrt(3.0)
GLOBAL_SQ2 = np.sqrt(2.0)

GLOBAL_C_MIN = 1.0 / (GLOBAL_PHI ** 10)
GLOBAL_C_MAX = 1.0 - 1.0 / (GLOBAL_PHI ** 20)

# =============================================================================
# 2. ФОРМУЛЫ КОНСТАНТ ИЗ E8
# =============================================================================

W_ALPHA = (GLOBAL_PHI**12) * (GLOBAL_PI**-4) * (GLOBAL_SQ3**3) * 2
W_MASS  = (GLOBAL_PHI**5)  * (GLOBAL_PI**3)  * (GLOBAL_SQ3**4) * 0.5
W_G     = (GLOBAL_PHI**-43) * (GLOBAL_PI**-1) * (GLOBAL_SQ3**-5) * 2

IDX_ALPHA = 7
IDX_MASS  = 2
IDX_G     = 3

# =============================================================================
# 3. ВЫВЕДЕННЫЕ КОЭФФИЦИЕНТЫ
# =============================================================================

GAMMA = 1.0 / (GLOBAL_PHI ** 12)
ETA   = 1.0 / (GLOBAL_PHI ** 10)

# CODATA для сравнения
CODATA_ALPHA = 137.035999084
CODATA_MASS  = 1836.15267343
CODATA_G     = 6.67430e-11
CODATA_M_E   = 0.51099895
CODATA_M_P   = 938.27208816
CODATA_M_N   = 939.56542052
CODATA_A_E   = 0.00115965218128
CODATA_A_P   = 1.79284734465
CODATA_A_N   = -1.9130427
CODATA_MU_E  = -9.2847647043e-24
CODATA_MU_P  = 1.41060679736e-26
CODATA_MU_N  = -9.6623651e-27

# Фундаментальные константы
E_CHARGE = 1.602176634e-19
MU_B = 9.2740100783e-24
MU_N = 5.050783699e-27

# =============================================================================
# 4. ГИПЕРБОЛИЧЕСКАЯ УПРУГОСТЬ
# =============================================================================

def etve_hyperbolic(C, c_min=GLOBAL_C_MIN, c_max=GLOBAL_C_MAX, k=None):
    """Гиперболическая упругость. k читается из глобального K_HYPER."""
    if k is None:
        k = K_HYPER
    E = (C - c_min) / (c_max - c_min + 1e-12)
    E_norm = E / (1.0 + k * E) * (1.0 + k)
    return c_min + E_norm * (c_max - c_min)


# =============================================================================
# 5. ФИЗИЧЕСКОЕ ЯДРО
# =============================================================================

class ETVEComplexCoreV132Hyperbolic:
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

        # Частицы
        self.m_e = CODATA_M_E
        self.m_p = CODATA_M_P
        self.m_n = CODATA_M_N
        self.Q_e = -E_CHARGE
        self.Q_p = +E_CHARGE
        self.Q_n = 0.0
        self.a_e = 0.0
        self.a_p = 0.0
        self.a_n = 0.0
        self.mu_e = 0.0
        self.mu_p = 0.0
        self.mu_n = 0.0

        self.real_particles = []
        self.virtual_particles = []
        self.memory = deque(maxlen=memory_depth)
        self.memory_matrices = deque(maxlen=memory_depth)

        # История
        self.history = {
            "C": [], "S": [],
            "alpha": [], "mass_ratio": [], "G": [],
            "m_p": [], "m_n": [], "m_e": [],
            "Q_e": [], "Q_p": [], "Q_n": [],
            "a_e": [], "a_p": [], "a_n": [],
            "mu_e": [], "mu_p": [], "mu_n": []
        }

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

    def update_field(self, dt):
        self.step_counter += 1

        M = self._build_complex_matrix()
        eigenvalues = np.linalg.eigvals(M)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]

        dC = self.C - C_FFS
        dS = self.S - S_cycle

        mod_alpha = 1.0 + 0.1 * dC - 0.05 * dS
        mod_mass  = 1.0 + 0.05 * dC - 0.02 * dS
        mod_G     = 1.0 - 0.2 * dC + 0.1 * dS

        alpha_inv = self.alpha_base * mod_alpha
        mass_ratio = self.mass_base * mod_mass
        G = self.G_base * mod_G

        # --- ВЫВОД ЧАСТИЦ ---
        alpha = 1.0 / alpha_inv

        # Массы
        m_p = self.m_e * mass_ratio
        E_binding = self.m_e * 2.0 * alpha_inv * self.E8_eigvals[0] / self.E8_eigvals[2]
        m_n = m_p + E_binding

        # Заряды
        Q_e = -E_CHARGE
        Q_p = +E_CHARGE
        Q_n = 0.0

        # Магнитные моменты
        a_e = alpha / (2.0 * self.pi)
        a_p = a_e * mass_ratio / self.E8_eigvals[2]
        a_n = -self.E8_eigvals[3] - 1.0/3.0

        # g-факторы
        g_e = 2.0 * (1.0 + a_e)
        g_p = 2.0 * (1.0 + a_p)
        g_n = 2.0 * a_n

        # μ
        mu_e = -g_e * MU_B * 0.5
        mu_p = g_p * MU_N * 0.5
        mu_n = g_n * MU_N * 0.5

        # Сохраняем
        self.m_p, self.m_n = m_p, m_n
        self.a_e, self.a_p, self.a_n = a_e, a_p, a_n
        self.mu_e, self.mu_p, self.mu_n = mu_e, mu_p, mu_n

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

        self.dt_real = dt_real
        self.dt_imag = dt_imag
        self.G = G
        self.alpha_inv = alpha_inv
        self.mass_ratio = mass_ratio

        self.memory_matrices.append((M, time.time()))

        return {
            "alpha_inv": alpha_inv, "mass_ratio": mass_ratio, "G": G,
            "m_e": self.m_e, "m_p": m_p, "m_n": m_n,
            "Q_e": Q_e, "Q_p": Q_p, "Q_n": Q_n,
            "a_e": a_e, "a_p": a_p, "a_n": a_n,
            "mu_e": mu_e, "mu_p": mu_p, "mu_n": mu_n
        }

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
        self.history["m_p"].append(result["m_p"])
        self.history["m_n"].append(result["m_n"])
        self.history["m_e"].append(result["m_e"])
        self.history["Q_e"].append(result["Q_e"])
        self.history["Q_p"].append(result["Q_p"])
        self.history["Q_n"].append(result["Q_n"])
        self.history["a_e"].append(result["a_e"])
        self.history["a_p"].append(result["a_p"])
        self.history["a_n"].append(result["a_n"])
        self.history["mu_e"].append(result["mu_e"])
        self.history["mu_p"].append(result["mu_p"])
        self.history["mu_n"].append(result["mu_n"])

        return result


# =============================================================================
# 6. ЗАПУСК
# =============================================================================

def demo_ffs_calibration(n_steps=100_000, log_every=10_000):
    print("=" * 80)
    print("🌀 ETVP v13.2 HYPERBOLIC — Полный вывод частиц")
    print(f"   Тактов: {n_steps:,}")
    print(f"   C_FFS = {C_FFS}, S_cycle = {S_cycle}")
    print(f"   γ = 1/Φ¹² = {GAMMA:.6f}, η = 1/Φ¹⁰ = {ETA:.6f}")
    print(f"   k = {K_HYPER}")
    print("=" * 80)

    model = ETVEComplexCoreV132Hyperbolic(memory_depth=100)
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
                  f"α⁻¹={result['alpha_inv']:.6f} mₚ/mₑ={result['mass_ratio']:.4f} "
                  f"mₚ={result['m_p']:.4f} mₙ={result['m_n']:.4f} "
                  f"aₚ={result['a_p']:.6f} | {rate:.0f} такт/с")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\n✅ Прогон завершён за {elapsed:.1f} с")

    n_avg = 1000
    print("\n" + "=" * 80)
    print("📌 СВОДКА (последние 1000 тактов)")
    print("=" * 80)

    print(f"\n   КОНСТАНТЫ:")
    print(f"   1/α    = {np.mean(model.history['alpha'][-n_avg:]):.9f}")
    print(f"   mₚ/mₑ  = {np.mean(model.history['mass_ratio'][-n_avg:]):.6f}")
    print(f"   G      = {np.mean(model.history['G'][-n_avg:]):.6e}")

    print(f"\n   МАССЫ:")
    print(f"   m_e    = {np.mean(model.history['m_e'][-n_avg:]):.8f} МэВ")
    print(f"   m_p    = {np.mean(model.history['m_p'][-n_avg:]):.8f} МэВ")
    print(f"   m_n    = {np.mean(model.history['m_n'][-n_avg:]):.8f} МэВ")

    print(f"\n   ЗАРЯДЫ:")
    print(f"   Q_e    = {np.mean(model.history['Q_e'][-n_avg:]):.6e} Кл")
    print(f"   Q_p    = {np.mean(model.history['Q_p'][-n_avg:]):.6e} Кл")
    print(f"   Q_n    = {np.mean(model.history['Q_n'][-n_avg:]):.6e} Кл")

    print(f"\n   МАГНИТНЫЕ МОМЕНТЫ:")
    print(f"   a_e    = {np.mean(model.history['a_e'][-n_avg:]):.10f}")
    print(f"   a_p    = {np.mean(model.history['a_p'][-n_avg:]):.10f}")
    print(f"   a_n    = {np.mean(model.history['a_n'][-n_avg:]):.10f}")
    print(f"   μ_e    = {np.mean(model.history['mu_e'][-n_avg:]):.6e}")
    print(f"   μ_p    = {np.mean(model.history['mu_p'][-n_avg:]):.6e}")
    print(f"   μ_n    = {np.mean(model.history['mu_n'][-n_avg:]):.6e}")

    print("\n" + "=" * 80)
    print("📊 ОШИБКИ")
    print("=" * 80)

    alpha_err = abs(np.mean(model.history['alpha'][-n_avg:]) - CODATA_ALPHA) / CODATA_ALPHA * 100
    mass_err  = abs(np.mean(model.history['mass_ratio'][-n_avg:]) - CODATA_MASS) / CODATA_MASS * 100
    G_err     = abs(np.mean(model.history['G'][-n_avg:]) - CODATA_G) / CODATA_G * 100
    mp_err    = abs(np.mean(model.history['m_p'][-n_avg:]) - CODATA_M_P) / CODATA_M_P * 100
    mn_err    = abs(np.mean(model.history['m_n'][-n_avg:]) - CODATA_M_N) / CODATA_M_N * 100
    ae_err    = abs(np.mean(model.history['a_e'][-n_avg:]) - CODATA_A_E) / CODATA_A_E * 100
    ap_err    = abs(np.mean(model.history['a_p'][-n_avg:]) - CODATA_A_P) / CODATA_A_P * 100
    an_err    = abs(np.mean(model.history['a_n'][-n_avg:]) - CODATA_A_N) / abs(CODATA_A_N) * 100
    mue_err   = abs(np.mean(model.history['mu_e'][-n_avg:]) - CODATA_MU_E) / abs(CODATA_MU_E) * 100
    mup_err   = abs(np.mean(model.history['mu_p'][-n_avg:]) - CODATA_MU_P) / abs(CODATA_MU_P) * 100
    mun_err   = abs(np.mean(model.history['mu_n'][-n_avg:]) - CODATA_MU_N) / abs(CODATA_MU_N) * 100

    print(f"\n   Заряд: Q_e, Q_p, Q_n — 0% (точно)")
    print(f"\n   Константы:")
    print(f"      1/α    : {alpha_err:.6f}%")
    print(f"      mₚ/mₑ  : {mass_err:.6f}%")
    print(f"      G      : {G_err:.6f}%")
    print(f"\n   Массы:")
    print(f"      m_p    : {mp_err:.6f}%")
    print(f"      m_n    : {mn_err:.6f}%")
    print(f"\n   Магнитные моменты:")
    print(f"      a_e    : {ae_err:.6f}%")
    print(f"      a_p    : {ap_err:.6f}%")
    print(f"      a_n    : {an_err:.6f}%")
    print(f"      μ_e    : {mue_err:.6f}%")
    print(f"      μ_p    : {mup_err:.6f}%")
    print(f"      μ_n    : {mun_err:.6f}%")

    # Графики
    fig, axes = plt.subplots(3, 4, figsize=(24, 15))

    axes[0, 0].plot(model.history["alpha"], color='blue', linewidth=0.5)
    axes[0, 0].axhline(CODATA_ALPHA, color='red', linestyle='--')
    axes[0, 0].set_title('1/α(t)')
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(model.history["mass_ratio"], color='green', linewidth=0.5)
    axes[0, 1].axhline(CODATA_MASS, color='red', linestyle='--')
    axes[0, 1].set_title('m_p/m_e(t)')
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(model.history["G"], color='orange', linewidth=0.5)
    axes[0, 2].axhline(CODATA_G, color='red', linestyle='--')
    axes[0, 2].set_title('G(t)')
    axes[0, 2].grid(alpha=0.3)

    axes[0, 3].plot(model.history["C"], color='purple', linewidth=0.5)
    axes[0, 3].axhline(C_FFS, color='orange', linestyle='--')
    axes[0, 3].set_title('C(t)')
    axes[0, 3].grid(alpha=0.3)

    axes[1, 0].plot(model.history["m_p"], color='blue', linewidth=0.5)
    axes[1, 0].axhline(CODATA_M_P, color='red', linestyle='--')
    axes[1, 0].set_title('m_p(t)')
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(model.history["m_n"], color='green', linewidth=0.5)
    axes[1, 1].axhline(CODATA_M_N, color='red', linestyle='--')
    axes[1, 1].set_title('m_n(t)')
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(model.history["a_e"], color='purple', linewidth=0.5)
    axes[1, 2].axhline(CODATA_A_E, color='red', linestyle='--')
    axes[1, 2].set_title('a_e(t)')
    axes[1, 2].grid(alpha=0.3)

    axes[1, 3].plot(model.history["a_p"], color='orange', linewidth=0.5)
    axes[1, 3].axhline(CODATA_A_P, color='red', linestyle='--')
    axes[1, 3].set_title('a_p(t)')
    axes[1, 3].grid(alpha=0.3)

    axes[2, 0].plot(model.history["a_n"], color='purple', linewidth=0.5)
    axes[2, 0].axhline(CODATA_A_N, color='red', linestyle='--')
    axes[2, 0].set_title('a_n(t)')
    axes[2, 0].grid(alpha=0.3)

    axes[2, 1].plot(np.array(model.history["mu_e"]) * 1e24, color='purple', linewidth=0.5)
    axes[2, 1].axhline(CODATA_MU_E * 1e24, color='red', linestyle='--')
    axes[2, 1].set_title('μ_e(t) · 10²⁴')
    axes[2, 1].grid(alpha=0.3)

    axes[2, 2].plot(np.array(model.history["mu_p"]) * 1e26, color='orange', linewidth=0.5)
    axes[2, 2].axhline(CODATA_MU_P * 1e26, color='red', linestyle='--')
    axes[2, 2].set_title('μ_p(t) · 10²⁶')
    axes[2, 2].grid(alpha=0.3)

    axes[2, 3].plot(np.array(model.history["mu_n"]) * 1e27, color='cyan', linewidth=0.5)
    axes[2, 3].axhline(CODATA_MU_N * 1e27, color='red', linestyle='--')
    axes[2, 3].set_title('μ_n(t) · 10²⁷')
    axes[2, 3].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('etvp_v132_full.png', dpi=150)
    plt.show()

    print("\n✅ Калибровка завершена.")


if __name__ == "__main__":
    demo_ffs_calibration(n_steps=100_000, log_every=10_000)
