#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP v12.6 — ЧИСТЫЙ ВЫВОД ИЗ Φ, π, √3
100 000 тактов. C = 0.999. Шум = 0.001.
Никаких нормировок вручную — только спектр E8.

Константы выводятся из отношений собственных значений
матрицы Картана E8, взвешенной плотностью вакуума C.
"""

import numpy as np
import math
import random
import time
from collections import deque
import matplotlib.pyplot as plt
import sys

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС (ТОЛЬКО Φ, π, √3)
# =============================================================================

GLOBAL_PHI = (1.0 + np.sqrt(5.0)) / 2.0
GLOBAL_PI  = np.pi
GLOBAL_SQ3 = np.sqrt(3.0)

# Плотность вакуума (она же когерентность области)
C_FIELD = 0.999
NOISE_LEVEL = 0.001

# Для проверки постфактум
CODATA_ALPHA_INV  = 137.035999084
CODATA_MASS_RATIO = 1836.15267343
CODATA_G          = 6.67430e-11

# =============================================================================
# 1. ЯДРО
# =============================================================================

class ETVEPureCore:
    """
    Чистое ядро. Константы — из спектра E8.
    C — плотность вакуума (не подгоняется).
    """
    def __init__(self):
        self.Phi = GLOBAL_PHI
        self.pi  = GLOBAL_PI
        self.sq3 = GLOBAL_SQ3
        self.step_counter = 0

        # Матрица Картана E8 в базисе 11×11
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

        # Состояние
        self.C = C_FIELD
        self.S = 0.0

        # История (для 100k — можно всю)
        self.history = {
            "step": [], "C": [], "S": [],
            "alpha_inv": [], "mass_ratio": [], "G": [],
            "eig_ratio_0_10": [], "eig_ratio_0_9": [],
            "eig_product": []
        }

    def build_matrix(self):
        """Матрица 11×11 с плотностью вакуума C."""
        # E8, взвешенная C
        M = self.C_E8.copy() * self.C

        # Диагональное расширение до 11D
        for i in range(8, 11):
            M[i, i] = self.C

        # Небольшая асимметрия от Φ (фрактальность)
        for i in range(11):
            M[i, i] *= (1.0 + 0.01 * np.sin(self.Phi * i))

        # Мнимая часть — дыхание (π, √3)
        M_imag = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                M_imag[i, j] = M[i, j] * np.tan(self.pi / 4.0 + 0.1 * (i - j))
        M_imag = (M_imag + M_imag.T) / 2.0

        # Фазовый сдвиг от S и √3
        phase_shift = 0.05 * self.sq3 * np.sin(self.S * self.step_counter)
        M_imag = M_imag + M * phase_shift

        return M + 1j * M_imag

    def update_field(self):
        """Спектр → константы. Без ручных нормировок."""
        self.step_counter += 1
        M = self.build_matrix()

        eigenvalues = np.linalg.eigvals(M)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]

        # Сырые отношения
        eig0 = eigenvalues[0]
        eig9 = eigenvalues[9]
        eig10 = eigenvalues[10]

        ratio_0_10 = np.real(eig0 / eig10)
        ratio_0_9 = np.real(eig0 / eig9)
        product = np.real(eig10 * eig9)

        # Константы из геометрии (без ручных нормировок)
        # 1/α — из отношения eig0/eig10, нормированного на Φ²
        alpha_inv = ratio_0_10 / (self.Phi ** 2)

        # m_p/m_e — из отношения eig0/eig9, нормированного на Φ
        mass_ratio = ratio_0_9 * self.Phi

        # G — из произведения eig10·eig9, нормированного на Φ²⁰
        G = 1.0 / (product * (self.Phi ** 20)) if abs(product) > 1e-30 else 0.0

        return {
            "alpha_inv": alpha_inv,
            "mass_ratio": mass_ratio,
            "G": G,
            "ratio_0_10": ratio_0_10,
            "ratio_0_9": ratio_0_9,
            "product": product
        }

    def evolve(self, noise=0.0):
        """Марковский такт."""
        # C дышит от шума
        self.C = self.C * (1.0 - noise) + noise * (1.0 - 1.0 / (self.Phi ** 10))
        self.S = max(0.0, min(1.0, self.S + noise * 0.1))
        return self.update_field()


# =============================================================================
# 2. ЗАПУСК
# =============================================================================

def run_pure(n_steps=100_000, log_every=10_000):
    print("=" * 80)
    print("🌀 ETVP v12.6 — ЧИСТЫЙ ВЫВОД ИЗ Φ, π, √3")
    print(f"   Тактов: {n_steps:,}")
    print(f"   C (плотность вакуума) = {C_FIELD}")
    print(f"   Шум = {NOISE_LEVEL}")
    print("   Никаких ручных нормировок — только спектр E8.")
    print("=" * 80)
    print(f"\n🔧 Геометрия:")
    print(f"   Φ  = {GLOBAL_PHI:.10f}")
    print(f"   π  = {GLOBAL_PI:.10f}")
    print(f"   √3 = {GLOBAL_SQ3:.10f}")
    print()

    core = ETVEPureCore()
    t0 = time.time()

    for i in range(n_steps):
        result = core.evolve(noise=NOISE_LEVEL)

        if (i + 1) % log_every == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1:>7,}] C={core.C:.8f}  "
                  f"1/α={result['alpha_inv']:.4f}  "
                  f"mₚ/mₑ={result['mass_ratio']:.2f}  "
                  f"G={result['G']:.4e}  "
                  f"| {rate:.0f} такт/с")
            sys.stdout.flush()

        core.history["step"].append(i + 1)
        core.history["C"].append(core.C)
        core.history["S"].append(core.S)
        core.history["alpha_inv"].append(result["alpha_inv"])
        core.history["mass_ratio"].append(result["mass_ratio"])
        core.history["G"].append(result["G"])
        core.history["eig_ratio_0_10"].append(result["ratio_0_10"])
        core.history["eig_ratio_0_9"].append(result["ratio_0_9"])
        core.history["eig_product"].append(result["product"])

    elapsed = time.time() - t0
    print(f"\n✅ Прогон завершён за {elapsed:.1f} с")

    # Итог
    n_avg = max(1, len(core.history["alpha_inv"]) // 10)
    alpha_mean = np.mean(core.history["alpha_inv"][-n_avg:])
    mass_mean = np.mean(core.history["mass_ratio"][-n_avg:])
    G_mean = np.mean(core.history["G"][-n_avg:])

    print("\n" + "=" * 80)
    print("📊 РЕЗУЛЬТАТЫ (последние 10% тактов)")
    print("=" * 80)
    print(f"  1/α     = {alpha_mean:.6f}")
    print(f"  mₚ/mₑ   = {mass_mean:.4f}")
    print(f"  G       = {G_mean:.6e}")

    print("\n📊 СРАВНЕНИЕ С CODATA")
    print("-" * 80)
    print(f"  1/α     : CODATA={CODATA_ALPHA_INV:.6f}  |  модель={alpha_mean:.6f}  |  "
          f"отношение={alpha_mean/CODATA_ALPHA_INV:.4f}")
    print(f"  mₚ/mₑ   : CODATA={CODATA_MASS_RATIO:.4f}  |  модель={mass_mean:.4f}  |  "
          f"отношение={mass_mean/CODATA_MASS_RATIO:.4f}")
    print(f"  G       : CODATA={CODATA_G:.4e}  |  модель={G_mean:.4e}  |  "
          f"отношение={G_mean/CODATA_G:.4f}")

    # Графики
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    steps = core.history["step"]

    axes[0, 0].plot(steps, core.history["C"], color='purple', linewidth=0.5)
    axes[0, 0].set_title('C(t) — плотность вакуума')
    axes[0, 0].set_xlabel('Такт')
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(steps, core.history["alpha_inv"], color='blue', linewidth=0.5)
    axes[0, 1].axhline(CODATA_ALPHA_INV, color='red', linestyle='--', label='CODATA')
    axes[0, 1].set_title('1/α(t) — из спектра E8')
    axes[0, 1].set_xlabel('Такт')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(steps, core.history["mass_ratio"], color='green', linewidth=0.5)
    axes[0, 2].axhline(CODATA_MASS_RATIO, color='red', linestyle='--', label='CODATA')
    axes[0, 2].set_title('mₚ/mₑ(t) — из спектра E8')
    axes[0, 2].set_xlabel('Такт')
    axes[0, 2].legend()
    axes[0, 2].grid(alpha=0.3)

    axes[1, 0].plot(steps, core.history["G"], color='orange', linewidth=0.5)
    axes[1, 0].axhline(CODATA_G, color='red', linestyle='--', label='CODATA')
    axes[1, 0].set_title('G(t) — из спектра E8')
    axes[1, 0].set_xlabel('Такт')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(steps, core.history["eig_ratio_0_10"], color='cyan', linewidth=0.5)
    axes[1, 1].set_title('eig[0]/eig[10]')
    axes[1, 1].set_xlabel('Такт')
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(steps, core.history["eig_ratio_0_9"], color='magenta', linewidth=0.5)
    axes[1, 2].set_title('eig[0]/eig[9]')
    axes[1, 2].set_xlabel('Такт')
    axes[1, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('etvp_pure_100k.png', dpi=150)
    plt.show()

    print("\n✅ Симуляция завершена.")


if __name__ == "__main__":
    run_pure(n_steps=100_000, log_every=10_000)
