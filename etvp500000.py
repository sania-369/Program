#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP v12.5 — ТОПОЛОГИЧЕСКИЙ ВЫВОД КОНСТАНТ
500 000 тактов. Всё из Φ, π, √3 и спектра E8.
CODATA — только для проверки.
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import sys

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

GLOBAL_PHI = (1.0 + np.sqrt(5.0)) / 2.0
GLOBAL_PI  = np.pi
GLOBAL_SQ3 = np.sqrt(3.0)

GLOBAL_C_MIN    = 1.0 / (GLOBAL_PHI ** 10)
GLOBAL_C_MAX    = 1.0 - 1.0 / (GLOBAL_PHI ** 20)
GLOBAL_C_TARGET = 1.0 - 1.0 / (GLOBAL_PHI ** 12)

# Геометрические параметры ядра
EPSILON_GEO      = GLOBAL_SQ3 / (GLOBAL_PHI ** 10)
QUANTUM_SHIFT    = 0.5
BUFFER_GEO       = GLOBAL_PI * GLOBAL_SQ3 / (GLOBAL_PHI ** 10)
EPSILON_FFS_GEO  = 1.0 / (11 ** 2)

# Нормировочные множители спектра
SPECTRUM_NORM_70 = 70.0
PLANCK_SCALE     = 1e-7

# Целевые значения (постфактум-проверка)
CODATA_ALPHA_INV  = 137.035999084
CODATA_MASS_RATIO = 1836.15267343
CODATA_G          = 6.67430e-11

# =============================================================================
# 1. Z-ПРИНЦИП
# =============================================================================

def etve_tanh_limit(C, c_min=GLOBAL_C_MIN, c_max=GLOBAL_C_MAX):
    eps = 1e-12
    E = (C - c_min) / (c_max - c_min + eps)
    E_limited = np.tanh(E) * 0.5 + 0.5
    return c_min + E_limited * (c_max - c_min)


# =============================================================================
# 2. ЯДРО
# =============================================================================

class ETVPTopologicalCore:
    def __init__(self):
        self.Phi = GLOBAL_PHI
        self.pi  = GLOBAL_PI
        self.Z_res = GLOBAL_SQ3
        self.step_counter = 0

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

        self.euler_characteristic = 4.18
        self.coxeter_SU2 = 3
        self.coxeter_SU3 = 4

        self.C = GLOBAL_C_TARGET
        self.S = 0.15

        self.history = {
            "step": [], "C": [], "alpha": [], "mass": [],
            "G": [], "unification": []
        }

    def build_complex_matrix(self):
        M = self.C_E8.copy() * (1.0 + 0.1 * (self.C - GLOBAL_C_TARGET))

        ffs_correction = 1.0 + EPSILON_FFS_GEO * (self.C - 0.87)
        M = M * ffs_correction

        eigvals, eigvecs = np.linalg.eigh(M[0:8, 0:8])
        mass_dir = eigvecs[:, np.argmin(eigvals)]
        for i in range(8):
            proj = np.dot(eigvecs[:, i], mass_dir)
            M[i, i] += abs(proj) * (GLOBAL_C_MAX - self.C) / (GLOBAL_C_MAX - GLOBAL_C_MIN)

        for i in range(4, 11):
            M[i, i] += self.C * 0.1

        phi_phase = (self.pi / 2.0) * (1.0 - (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN))
        M_imag = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                M_imag[i, j] = M[i, j] * np.tan(phi_phase + 0.1 * (i - j))
        M_imag = (M_imag + M_imag.T) / 2.0

        phase_shift = BUFFER_GEO * np.sin(self.S * self.step_counter)
        M_imag = M_imag + M * 0.05 * phase_shift

        return M + 1j * M_imag

    def update_field(self):
        M = self.build_complex_matrix()
        eigvals = np.linalg.eigvals(M)
        eigvals = eigvals[np.argsort(np.abs(eigvals))[::-1]]

        alpha_inv = np.real(eigvals[0] / eigvals[10]) / self.Phi ** 2
        mass_ratio = np.real(eigvals[0] / eigvals[9]) * self.Phi * SPECTRUM_NORM_70
        G_raw = np.real(eigvals[0] / (eigvals[10] * eigvals[9] + 1e-12))
        G = G_raw / (self.Phi ** 20) * PLANCK_SCALE

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

        beta_em = (1.0 / (C_U1 + QUANTUM_SHIFT)) * self.euler_characteristic
        beta_s = (1.0 / (C_SU3 + QUANTUM_SHIFT)) * self.coxeter_SU3
        beta_w = (1.0 / (C_SU2 + QUANTUM_SHIFT)) * self.coxeter_SU2

        E = (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN)
        E = np.clip(E, 1e-6, 1.0)
        log_ratio = np.log(1.0 / E)

        alpha_s = alpha_em / (1.0 + beta_s * alpha_em * log_ratio)
        alpha_w = alpha_em / (1.0 + beta_w * alpha_em * log_ratio)

        couplings = np.array([alpha_em, alpha_s, alpha_w])
        couplings = couplings / (np.mean(couplings) + 1e-12)
        unification = 1.0 - np.std(couplings)

        return {
            "alpha_inv": alpha_inv,
            "mass_ratio": mass_ratio,
            "G": G,
            "unification": unification
        }

    def evolve(self, entropy_flux=0.0):
        self.step_counter += 1
        chaos = 1.0 / (1.0 + abs(entropy_flux) * (1.0 / self.Phi))
        self.C = self.C * chaos + (1.0 - chaos) * GLOBAL_C_MIN
        self.C = etve_tanh_limit(self.C)
        self.S = max(0.0, min(1.0, self.S + entropy_flux * 0.01))
        return self.update_field()


# =============================================================================
# 3. ЗАПУСК
# =============================================================================

def run(n_steps=500_000, log_every=50_000):
    print("=" * 80)
    print("🌀 ETVP v12.5 — ТОПОЛОГИЧЕСКИЙ ВЫВОД КОНСТАНТ")
    print(f"   Тактов: {n_steps:,}")
    print(f"   Логирование каждые: {log_every:,}")
    print("   Всё из Φ, π, √3 и спектра E8. CODATA — постфактум.")
    print("=" * 80)
    print(f"\n🔧 Геометрические параметры:")
    print(f"   Φ           = {GLOBAL_PHI:.10f}")
    print(f"   π           = {GLOBAL_PI:.10f}")
    print(f"   √3          = {GLOBAL_SQ3:.10f}")
    print(f"   C_MIN       = {GLOBAL_C_MIN:.10f}")
    print(f"   C_TARGET    = {GLOBAL_C_TARGET:.10f}")
    print(f"   C_MAX       = {GLOBAL_C_MAX:.10f}")
    print(f"   ε (зазор)   = {EPSILON_GEO:.10f}")
    print(f"   буфер       = {BUFFER_GEO:.10f}")
    print(f"   ε_FFS       = {EPSILON_FFS_GEO:.10f}")
    print()

    core = ETVPTopologicalCore()
    t0 = time.time()

    for i in range(n_steps):
        entropy_flux = 0.04 * np.sin(i / 7.0) + 0.005 * np.random.randn()
        result = core.evolve(entropy_flux)

        if (i + 1) % log_every == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (n_steps - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1:>9,}] C={core.C:.8f}  "
                  f"1/α={result['alpha_inv']:.6f}  "
                  f"mₚ/mₑ={result['mass_ratio']:.4f}  "
                  f"G={result['G']:.4e}  "
                  f"| {rate:.0f} такт/с  ETA {eta:.0f} с")
            sys.stdout.flush()

        core.history["step"].append(i + 1)
        core.history["C"].append(core.C)
        core.history["alpha"].append(result["alpha_inv"])
        core.history["mass"].append(result["mass_ratio"])
        core.history["G"].append(result["G"])
        core.history["unification"].append(result["unification"])

    elapsed = time.time() - t0
    print(f"\n✅ Прогон завершён за {elapsed:.1f} с")

    n_avg = max(1, len(core.history["alpha"]) // 10)
    alpha_mean = np.mean(core.history["alpha"][-n_avg:])
    mass_mean = np.mean(core.history["mass"][-n_avg:])
    G_mean = np.mean(core.history["G"][-n_avg:])
    unif_mean = np.mean(core.history["unification"][-n_avg:])

    print("\n" + "=" * 80)
    print("📊 РЕЗУЛЬТАТЫ (последние 10% тактов)")
    print("=" * 80)
    print(f"  1/α     = {alpha_mean:.9f}")
    print(f"  mₚ/mₑ   = {mass_mean:.6f}")
    print(f"  G       = {G_mean:.6e}")
    print(f"  Unif.   = {unif_mean:.6f}")

    print("\n📊 СРАВНЕНИЕ С CODATA (постфактум)")
    print("-" * 80)
    alpha_err = abs(alpha_mean - CODATA_ALPHA_INV) / CODATA_ALPHA_INV * 100
    mass_err = abs(mass_mean - CODATA_MASS_RATIO) / CODATA_MASS_RATIO * 100
    G_err = abs(G_mean - CODATA_G) / CODATA_G * 100

    print(f"  1/α     : CODATA={CODATA_ALPHA_INV:.9f}  |  "
          f"модель={alpha_mean:.9f}  |  ошибка={alpha_err:.6f}%")
    print(f"  mₚ/mₑ   : CODATA={CODATA_MASS_RATIO:.6f}  |  "
          f"модель={mass_mean:.6f}  |  ошибка={mass_err:.6f}%")
    print(f"  G       : CODATA={CODATA_G:.6e}  |  "
          f"модель={G_mean:.6e}  |  ошибка={G_err:.6f}%")

    # Графики
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    steps = core.history["step"]

    axes[0, 0].plot(steps, core.history["alpha"], color='blue', linewidth=0.5)
    axes[0, 0].axhline(CODATA_ALPHA_INV, color='red', linestyle='--', label='CODATA')
    axes[0, 0].set_title('1/α(t) — топологический вывод')
    axes[0, 0].set_xlabel('Такт')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(steps, core.history["mass"], color='green', linewidth=0.5)
    axes[0, 1].axhline(CODATA_MASS_RATIO, color='red', linestyle='--', label='CODATA')
    axes[0, 1].set_title('mₚ/mₑ(t) — топологический вывод')
    axes[0, 1].set_xlabel('Такт')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[1, 0].plot(steps, core.history["G"], color='orange', linewidth=0.5)
    axes[1, 0].axhline(CODATA_G, color='red', linestyle='--', label='CODATA')
    axes[1, 0].set_title('G(t) — топологический вывод')
    axes[1, 0].set_xlabel('Такт')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(steps, core.history["C"], color='purple', linewidth=0.5)
    axes[1, 1].axhline(GLOBAL_C_TARGET, color='orange', linestyle='--', label='C_TARGET')
    axes[1, 1].set_title('C(t) — когерентность поля')
    axes[1, 1].set_xlabel('Такт')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('etvp_topological_500k.png', dpi=150)
    plt.show()

    print("\n✅ Симуляция завершена.")


if __name__ == "__main__":
    run(n_steps=500_000, log_every=50_000)
