#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP v12.7 — ОПЕРАТОР U^E8 С НАПРАВЛЕНИЕМ ВРАЩЕНИЯ
100 000 тактов. C = 0.999. Шум = 0.001.

Ключевое:
- Работаем с оператором U^E8 = exp(i·φ·E8), а не с E8 напрямую.
- φ = (π/2)·(1 - C) — фаза вращения, зависит от C.
- При C = 1: φ = 0, U = I (тождество).
- При C < 1: φ > 0, U поворачивает состояние.
- Направление вращения (знак φ) определяет хиральность.
- Спектр U комплексный — константы из отношений модулей.
"""

import numpy as np
import time
import sys
from scipy.linalg import expm
import matplotlib.pyplot as plt

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

GLOBAL_PHI = (1.0 + np.sqrt(5.0)) / 2.0
GLOBAL_PI  = np.pi
GLOBAL_SQ3 = np.sqrt(3.0)

C_FIELD = 0.999
NOISE_LEVEL = 0.001

CODATA_ALPHA_INV  = 137.035999084
CODATA_MASS_RATIO = 1836.15267343
CODATA_G          = 6.67430e-11

# =============================================================================
# 1. ЯДРО С ОПЕРАТОРОМ U^E8
# =============================================================================

class ETVEOperatorCore:
    """
    Ядро с оператором U^E8 = exp(i·φ·E8).
    φ зависит от C — направление вращения.
    """
    def __init__(self):
        self.Phi = GLOBAL_PHI
        self.pi  = GLOBAL_PI
        self.sq3 = GLOBAL_SQ3
        self.step_counter = 0

        # Матрица Картана E8 в базисе 11×11
        self.E8 = np.zeros((11, 11), dtype=float)
        self.E8[0:8, 0:8] = np.array([
            [ 2, -1,  0,  0,  0,  0,  0,  0],
            [-1,  2, -1,  0,  0,  0,  0,  0],
            [ 0, -1,  2, -1,  0,  0,  0,  0],
            [ 0,  0, -1,  2, -1,  0,  0,  0],
            [ 0,  0,  0, -1,  2, -1,  0, -1],
            [ 0,  0,  0,  0, -1,  2, -1,  0],
            [ 0,  0,  0,  0,  0, -1,  2,  0],
            [ 0,  0,  0,  0, -1,  0,  0,  2]
        ], dtype=float)

        # Расширение до 11×11: три дополнительных измерения
        for i in range(8, 11):
            self.E8[i, i] = self.sq3  # √3 как «вес» дополнительных измерений

        # Состояние
        self.C = C_FIELD
        self.S = 0.0
        self.phi = 0.0

        # История
        self.history = {
            "step": [], "C": [], "phi": [],
            "alpha_inv": [], "mass_ratio": [], "G": [],
            "eig_mod_0": [], "eig_mod_1": [], "eig_mod_2": []
        }

    def build_operator(self):
        """
        Оператор U^E8 = exp(i·φ·E8).
        φ = (π/2)·(1 - C) — фаза вращения.
        """
        # Фаза вращения — зависит от C
        self.phi = (self.pi / 2.0) * (1.0 - self.C)

        # Мнимая часть от S
        phi_imag = self.phi + 0.1 * self.S * self.sq3

        # Оператор
        U = expm(1j * phi_imag * self.E8)
        return U

    def update_field(self):
        """Спектр U → константы."""
        self.step_counter += 1
        U = self.build_operator()

        eigenvalues = np.linalg.eigvals(U)
        # Сортируем по модулю (убывание)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]

        # Модули
        mods = np.abs(eigenvalues)
        # Фазы
        phases = np.angle(eigenvalues)

        # Сырые отношения
        mod_0 = mods[0] if mods[0] > 1e-30 else 1e-30
        mod_9 = mods[9] if mods[9] > 1e-30 else 1e-30
        mod_10 = mods[10] if mods[10] > 1e-30 else 1e-30

        ratio_0_10 = mod_0 / mod_10
        ratio_0_9 = mod_0 / mod_9
        product = mod_10 * mod_9

        # Константы из отношений (без ручных нормировок)
        # 1/α = (модуль eig[0]/eig[10]) / Φ² · (π/√3)
        alpha_inv = ratio_0_10 / (self.Phi ** 2) * (self.pi / self.sq3)

        # m_p/m_e = (модуль eig[0]/eig[9]) · Φ · √3
        mass_ratio = ratio_0_9 * self.Phi * self.sq3

        # G = 1 / (mod_10 · mod_9 · Φ²⁰)
        G = 1.0 / (product * (self.Phi ** 20)) if abs(product) > 1e-30 else 0.0

        # Учет направления вращения (знак φ)
        if self.phi < 0:
            alpha_inv = -alpha_inv

        return {
            "alpha_inv": alpha_inv,
            "mass_ratio": mass_ratio,
            "G": G,
            "ratio_0_10": ratio_0_10,
            "ratio_0_9": ratio_0_9,
            "product": product,
            "mod_0": mod_0,
            "mod_9": mod_9,
            "mod_10": mod_10,
            "phase_0": phases[0] if len(phases) > 0 else 0
        }

    def evolve(self, noise=0.0):
        """Марковский такт."""
        self.C = self.C * (1.0 - noise) + noise * (1.0 - 1.0 / (self.Phi ** 10))
        self.S = max(0.0, min(1.0, self.S + noise * 0.1))
        return self.update_field()


# =============================================================================
# 2. ЗАПУСК
# =============================================================================

def run_operator(n_steps=100_000, log_every=10_000):
    print("=" * 80)
    print("🌀 ETVP v12.7 — ОПЕРАТОР U^E8 С НАПРАВЛЕНИЕМ ВРАЩЕНИЯ")
    print(f"   Тактов: {n_steps:,}")
    print(f"   C = {C_FIELD}, шум = {NOISE_LEVEL}")
    print("   U = exp(i·φ·E8), φ = (π/2)·(1-C)")
    print("   Направление вращения (знак φ) определяет хиральность.")
    print("=" * 80)
    print()

    core = ETVEOperatorCore()
    t0 = time.time()

    for i in range(n_steps):
        result = core.evolve(noise=NOISE_LEVEL)

        if (i + 1) % log_every == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1:>7,}] C={core.C:.8f}  φ={core.phi:.6f}  "
                  f"1/α={result['alpha_inv']:.4f}  "
                  f"mₚ/mₑ={result['mass_ratio']:.2f}  "
                  f"G={result['G']:.4e}  "
                  f"| {rate:.0f} такт/с")
            sys.stdout.flush()

        core.history["step"].append(i + 1)
        core.history["C"].append(core.C)
        core.history["phi"].append(core.phi)
        core.history["alpha_inv"].append(result["alpha_inv"])
        core.history["mass_ratio"].append(result["mass_ratio"])
        core.history["G"].append(result["G"])
        core.history["eig_mod_0"].append(result["mod_0"])
        core.history["eig_mod_1"].append(result["mod_9"])
        core.history["eig_mod_2"].append(result["mod_10"])

    elapsed = time.time() - t0
    print(f"\n✅ Прогон завершён за {elapsed:.1f} с")

    n_avg = max(1, len(core.history["alpha_inv"]) // 10)
    alpha_mean = np.mean(core.history["alpha_inv"][-n_avg:])
    mass_mean = np.mean(core.history["mass_ratio"][-n_avg:])
    G_mean = np.mean(core.history["G"][-n_avg:])
    phi_mean = np.mean(core.history["phi"][-n_avg:])

    print("\n" + "=" * 80)
    print("📊 РЕЗУЛЬТАТЫ (последние 10% тактов)")
    print("=" * 80)
    print(f"  φ (фаза вращения) = {phi_mean:.6f}")
    print(f"  1/α     = {alpha_mean:.6f}")
    print(f"  mₚ/mₑ   = {mass_mean:.4f}")
    print(f"  G       = {G_mean:.6e}")

    print("\n📊 СРАВНЕНИЕ С CODATA")
    print("-" * 80)
    print(f"  1/α     : CODATA={CODATA_ALPHA_INV:.6f}  |  модель={alpha_mean:.6f}  |  "
          f"отношение={alpha_mean/CODATA_ALPHA_INV:.6f}")
    print(f"  mₚ/mₑ   : CODATA={CODATA_MASS_RATIO:.4f}  |  модель={mass_mean:.4f}  |  "
          f"отношение={mass_mean/CODATA_MASS_RATIO:.6f}")
    print(f"  G       : CODATA={CODATA_G:.4e}  |  модель={G_mean:.4e}  |  "
          f"отношение={G_mean/CODATA_G:.4e}")

    # Графики
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    steps = core.history["step"]

    axes[0, 0].plot(steps, core.history["C"], color='purple', linewidth=0.5)
    axes[0, 0].set_title('C(t) — плотность вакуума')
    axes[0, 0].set_xlabel('Такт')
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(steps, core.history["phi"], color='red', linewidth=0.5)
    axes[0, 1].set_title('φ(t) — фаза вращения')
    axes[0, 1].set_xlabel('Такт')
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(steps, core.history["alpha_inv"], color='blue', linewidth=0.5)
    axes[0, 2].axhline(CODATA_ALPHA_INV, color='red', linestyle='--', label='CODATA')
    axes[0, 2].set_title('1/α(t) — из оператора U^E8')
    axes[0, 2].set_xlabel('Такт')
    axes[0, 2].legend()
    axes[0, 2].grid(alpha=0.3)

    axes[1, 0].plot(steps, core.history["mass_ratio"], color='green', linewidth=0.5)
    axes[1, 0].axhline(CODATA_MASS_RATIO, color='red', linestyle='--', label='CODATA')
    axes[1, 0].set_title('mₚ/mₑ(t) — из оператора U^E8')
    axes[1, 0].set_xlabel('Такт')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(steps, core.history["G"], color='orange', linewidth=0.5)
    axes[1, 1].axhline(CODATA_G, color='red', linestyle='--', label='CODATA')
    axes[1, 1].set_title('G(t) — из оператора U^E8')
    axes[1, 1].set_xlabel('Такт')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(steps, core.history["eig_mod_0"], color='cyan', linewidth=0.5, label='mod[0]')
    axes[1, 2].plot(steps, core.history["eig_mod_1"], color='magenta', linewidth=0.5, label='mod[9]')
    axes[1, 2].plot(steps, core.history["eig_mod_2"], color='yellow', linewidth=0.5, label='mod[10]')
    axes[1, 2].set_title('Модули собственных значений')
    axes[1, 2].set_xlabel('Такт')
    axes[1, 2].legend()
    axes[1, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('etvp_operator_100k.png', dpi=150)
    plt.show()

    print("\n✅ Симуляция завершена.")


if __name__ == "__main__":
    run_operator(n_steps=100_000, log_every=10_000)
