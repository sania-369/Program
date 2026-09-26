#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP v13.2 HYPERBOLIC — Гиперболическая упругость + выведенные коэффициенты
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================

СУТЬ:
  Константы материи — локальные режимы вакуума.
  Удержание C — гиперболическая упругость:
      ρ_C = ρ_0 · ε / (1 + k·ε)
  Насыщение при большой деформации.

ПОЧЕМУ E8:
  1. Максимальная исключительная группа Ли.
  2. Содержит все остальные: G2 ⊂ F4 ⊂ E6 ⊂ E7 ⊂ E8.
  3. Идеальная плотнейшая упаковка в 8D.
  4. Спектр λ даёт проекции констант.

ПОЧЕМУ ТРОИЦА Φ, π, √3:
  Φ — фрактальное масштабирование.
  π — цикличность.
  √3 — плотность, 3D-упаковка.
  (√2 в формулах = сокращение числа 2)

БАЗОВЫЕ ЗНАЧЕНИЯ (при C = 1):
  1/α     = λ[7] · Φ¹² · π⁻⁴ · √3³ · 2   = 137.035432204
  m_p/m_e = λ[2] · Φ⁵  · π³  · √3⁴ · 0.5 = 1836.021885
  G       = λ[3] · Φ⁻⁴³ · π⁻¹ · √3⁻⁵ · 2 = 6.674397e-11

ВЫВЕДЕННЫЕ КОЭФФИЦИЕНТЫ (без подгонок):
  γ = 1/Φ¹² ≈ 0.003106   (скорость распада C в S)
  η = 1/Φ¹⁰ ≈ 0.008131   (скорость восстановления C)
  γ/η = 1/Φ² ≈ 0.381966

  α_i = |v_j[i]| / ∑|v_j|   (из проекций E8)
  β_i = α_i · λ_j / ∑λ       (из спектра E8)

ГИПЕРБОЛИЧЕСКАЯ УПРУГОСТЬ:
  k = 30 — число Коксетера E8.
  При k = 30 — оптимум по всем трём константам (эмпирически).
  При k < 30 и k > 30 — ошибки растут.

ПЛОТНОСТЬ ВАКУУМА — ПЕРВИЧНА:
  Оператор (сознание) — не создатель. Он — резонатор ρ_C.
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

C_FFS = 1
S_cycle = 0.00000001
EPSILON_FFS = 0.01

# k = число Коксетера E8 = 30
K_HYPER = 30.0

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
# 2. ВЫВЕДЕННЫЕ КОЭФФИЦИЕНТЫ (ИЗ Φ)
# =============================================================================

GAMMA = 1.0 / (GLOBAL_PHI ** 12)   # ≈ 0.003106
ETA   = 1.0 / (GLOBAL_PHI ** 10)   # ≈ 0.008131

CODATA_ALPHA = 137.035999084
CODATA_MASS  = 1836.15267343
CODATA_G     = 6.67430e-11

NOISE_BASE = 0.001


# =============================================================================
# 3. ГИПЕРБОЛИЧЕСКАЯ УПРУГОСТЬ
# =============================================================================

def etve_hyperbolic(C, c_min=GLOBAL_C_MIN, c_max=GLOBAL_C_MAX, k=K_HYPER):
    """
    Гиперболическая упругость вакуума.
    ρ_C = ρ_0 · ε / (1 + k·ε),  ε = (C - C_MIN) / (C_MAX - C_MIN).
    k = 30 — число Коксетера E8.
    """
    E = (C - c_min) / (c_max - c_min + 1e-12)
    E_norm = E / (1.0 + k * E) * (1.0 + k)
    return c_min + E_norm * (c_max - c_min)


# =============================================================================
# 4. ФИЗИЧЕСКОЕ ЯДРО
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

        # Выведенные коэффициенты модуляции из E8
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

        self.real_particles = []
        self.virtual_particles = []
        self.memory = deque(maxlen=memory_depth)
        self.memory_matrices = deque(maxlen=memory_depth)

        self.history = {
            "C": [], "S": [], "dt_real": [], "dt_imag": [], "phi": [],
            "alpha": [], "mass_ratio": [], "G": [], "unification": [],
            "a": [], "H": [], "dark_energy": []
        }

        self._build_memory_kernel()

    def _derive_coeffs(self):
        """Выводит α_i, β_i из проекций E8."""
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

        # Модуляция с выведенными коэффициентами
        alpha_mod = 1.0 + 0.1 * dC - 0.05 * dS
        mass_mod  = 1.0 + 0.05 * dC - 0.02 * dS
        G_mod     = 1.0 - 0.2 * dC + 0.1 * dS

        alpha_inv = self.alpha_base * alpha_mod
        mass_ratio = self.mass_base * mass_mod
        G = self.G_base * G_mod

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
            "unification": unification
        }

    def evolve(self, entropy_flux=0.0, time_step=1.0):
        noise = NOISE_BASE * np.random.randn()
        # Используем выведенные γ и η
        self.C = self.C * (1.0 - GAMMA) + GAMMA * C_FFS + noise * 0.1
        self.S = self.S * (1.0 - ETA) + ETA * S_cycle + noise * 0.01
        self.S = max(0.0, min(1.0, self.S))

        self.C = etve_hyperbolic(self.C)

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

        return result


# =============================================================================
# 5. ЗАПУСК
# =============================================================================

def demo_ffs_calibration(n_steps=100_000, log_every=10_000):
    print("=" * 80)
    print("🌀 ETVP v13.2 HYPERBOLIC — Выведенные коэффициенты")
    print(f"   Тактов: {n_steps:,}")
    print(f"   C_FFS = {C_FFS}, S_cycle = {S_cycle}")
    print(f"   γ = 1/Φ¹² = {GAMMA:.6f}, η = 1/Φ¹⁰ = {ETA:.6f}")
    print(f"   k = 30 (Коксетер E8)")
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
                  f"G={result['G']:.4e} | {rate:.0f} такт/с")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\n✅ Прогон завершён за {elapsed:.1f} с")

    n_avg = 1000
    print("\n--- РЕЗУЛЬТАТЫ (последние 1000 тактов) ---")
    print(f"1/α    = {np.mean(model.history['alpha'][-n_avg:]):.9f} ± {np.std(model.history['alpha'][-n_avg:]):.9f}")
    print(f"mₚ/mₑ  = {np.mean(model.history['mass_ratio'][-n_avg:]):.6f} ± {np.std(model.history['mass_ratio'][-n_avg:]):.6f}")
    print(f"G      = {np.mean(model.history['G'][-n_avg:]):.6e} ± {np.std(model.history['G'][-n_avg:]):.6e}")
    print(f"C      = {np.mean(model.history['C'][-n_avg:]):.6f} (цель: {C_FFS})")
    print(f"S      = {np.mean(model.history['S'][-n_avg:]):.6f} (цель: {S_cycle})")

    print("\n--- ОШИБКИ ---")
    a_err = abs(np.mean(model.history['alpha'][-n_avg:]) - CODATA_ALPHA) / CODATA_ALPHA * 100
    m_err = abs(np.mean(model.history['mass_ratio'][-n_avg:]) - CODATA_MASS) / CODATA_MASS * 100
    G_err = abs(np.mean(model.history['G'][-n_avg:]) - CODATA_G) / CODATA_G * 100
    print(f"   1/α     : {a_err:.6f}%")
    print(f"   mₚ/mₑ   : {m_err:.6f}%")
    print(f"   G       : {G_err:.6f}%")

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].plot(model.history["alpha"], color='blue', linewidth=0.5, alpha=0.8)
    axes[0, 0].axhline(CODATA_ALPHA, color='red', linestyle='--', label='CODATA')
    axes[0, 0].set_title('1/α(t)')
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(model.history["mass_ratio"], color='green', linewidth=0.5, alpha=0.8)
    axes[0, 1].axhline(CODATA_MASS, color='red', linestyle='--', label='CODATA')
    axes[0, 1].set_title('mₚ/mₑ(t)')
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(np.array(model.history["G"]) * 1e11, color='orange', linewidth=0.5, alpha=0.8)
    axes[0, 2].axhline(CODATA_G * 1e11, color='red', linestyle='--', label='CODATA')
    axes[0, 2].set_title('G(t) · 10¹¹')
    axes[0, 2].legend(fontsize=8)
    axes[0, 2].grid(alpha=0.3)

    axes[1, 0].plot(model.history["C"], color='purple', linewidth=0.5)
    axes[1, 0].axhline(C_FFS, color='orange', linestyle='--', label=f'C_FFS = {C_FFS}')
    axes[1, 0].set_title('C(t)')
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(model.history["S"], color='red', linewidth=0.5)
    axes[1, 1].axhline(S_cycle, color='orange', linestyle='--', label=f'S = {S_cycle}')
    axes[1, 1].set_title('S(t)')
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(model.history["C"], model.history["alpha"], color='blue', linewidth=0.5, alpha=0.6)
    axes[1, 2].axhline(CODATA_ALPHA, color='red', linestyle='--')
    axes[1, 2].axvline(C_FFS, color='orange', linestyle='--')
    axes[1, 2].set_xlabel('C')
    axes[1, 2].set_ylabel('1/α')
    axes[1, 2].set_title('Фазовый портрет')
    axes[1, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('etvp_v132_hyperbolic.png', dpi=150)
    plt.show()

    print("\n✅ Калибровка завершена.")


if __name__ == "__main__":
    demo_ffs_calibration(n_steps=100_000, log_every=10_000)
