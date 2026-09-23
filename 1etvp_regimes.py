#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP REGIMES — Перебор режимов вакуума
================================================================================
Одна точка управления: C_FFS (плотность/упругость/когерентность вакуума).

Меняй C_FFS — смотри, как меняются константы и графики.
================================================================================

ПРИМЕРЫ РЕЖИМОВ:
  • 0.013 — около ЧД (C_MIN)
  • 0.30  — сильное поле
  • 0.50  — плазма
  • 0.87  — наш режим (CODATA)
  • 0.95  — высококогерентный оператор
  • 0.99  — ранняя Вселенная
  • 0.999 — почти абсолютный вакуум
================================================================================
"""

import numpy as np
import math
import matplotlib.pyplot as plt

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

C_MIN = 1.0 / (PHI ** 10)        # ≈ 0.0132
C_MAX = 1.0 - 1.0 / (PHI ** 20)  # ≈ 0.99993

# =============================================================================
# 1. ТОЧКА УПРАВЛЕНИЯ — МЕНЯЙ ЗДЕСЬ
# =============================================================================

# >>> ВЫБЕРИ РЕЖИМ <<<
C_FFS = 0.87      # плотность/упругость/когерентность вакуума
S_CYCLE = 0.12    # энтропия цикла

# Точки перехода clip → tanh
C_SOFT_LOW  = 0.999333
C_SOFT_HIGH = 1.0

# =============================================================================
# 2. ФОРМУЛЫ КОНСТАНТ (из E8 + Троица Φ, π, √3)
# =============================================================================

# Множители (без √2: √2² = 2, √2⁻² = 1/2)
W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4) * 0.5
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * 2

# Матрица Картана E8
E8 = np.array([
    [ 2, -1,  0,  0,  0,  0,  0,  0],
    [-1,  2, -1,  0,  0,  0,  0,  0],
    [ 0, -1,  2, -1,  0,  0,  0,  0],
    [ 0,  0, -1,  2, -1,  0,  0,  0],
    [ 0,  0,  0, -1,  2, -1,  0, -1],
    [ 0,  0,  0,  0, -1,  2, -1,  0],
    [ 0,  0,  0,  0,  0, -1,  2,  0],
    [ 0,  0,  0,  0, -1,  0,  0,  2]
], dtype=float)

eigvals = np.sort(np.linalg.eigvalsh(E8))

# Базовые значения (при C = 1)
alpha_base = eigvals[7] * W_ALPHA
mass_base  = eigvals[2] * W_MASS
G_base     = eigvals[3] * W_G

# CODATA (только для сравнения)
CODATA = {
    "1/α": 137.035999084,
    "m_p/m_e": 1836.15267343,
    "G": 6.67430e-11,
}

# Коэффициенты модуляции
COEFFS = {
    "1/α":     (0.1,  -0.05),
    "m_p/m_e": (0.05, -0.02),
    "G":       (-0.2,  0.1),
}

# =============================================================================
# 3. ФУНКЦИЯ УДЕРЖАНИЯ (clip → tanh)
# =============================================================================

def etve_tanh_limit(C, c_min=C_MIN, c_max=C_MAX,
                    c_soft_low=C_SOFT_LOW, c_soft_high=C_SOFT_HIGH):
    """Гибрид: clip внизу, tanh наверху, smoothstep между."""
    c_clip = np.clip(C, c_min, c_max)

    E = (C - c_min) / (c_max - c_min + 1e-12)
    c_tanh = c_min + (np.tanh(E * 2.0) * 0.5 + 0.5) * (c_max - c_min)

    if C <= c_soft_low:
        w = 0.0
    elif C >= c_soft_high:
        w = 1.0
    else:
        t = (C - c_soft_low) / (c_soft_high - c_soft_low)
        w = t * t * (3.0 - 2.0 * t)

    return (1.0 - w) * c_clip + w * c_tanh


# =============================================================================
# 4. ЗАПУСК ДЛЯ ОДНОГО РЕЖИМА
# =============================================================================

def run_regime(C_FFS, S_cycle, n_steps=10000, label=""):
    print("=" * 80)
    print(f"🌀 РЕЖИМ: C_FFS = {C_FFS}, S_cycle = {S_cycle} {label}")
    print("=" * 80)

    C = C_MAX
    S = S_cycle
    history = {"C": [], "S": [], "alpha": [], "mass": [], "G": []}

    for i in range(n_steps):
        noise = 0.001 * np.random.randn()
        C = C * (1.0 - 0.001) + 0.001 * C_FFS + noise * 0.1
        S = S * (1.0 - 0.001) + 0.001 * S_cycle + noise * 0.01
        S = max(0.0, min(1.0, S))
        C = etve_tanh_limit(C)

        dC = C - C_FFS
        dS = S - S_cycle

        alpha = alpha_base * (1 + COEFFS["1/α"][0]*dC + COEFFS["1/α"][1]*dS)
        mass  = mass_base  * (1 + COEFFS["m_p/m_e"][0]*dC + COEFFS["m_p/m_e"][1]*dS)
        G     = G_base     * (1 + COEFFS["G"][0]*dC + COEFFS["G"][1]*dS)

        history["C"].append(C)
        history["S"].append(S)
        history["alpha"].append(alpha)
        history["mass"].append(mass)
        history["G"].append(G)

    n_avg = max(1, n_steps // 10)
    alpha_mean = np.mean(history["alpha"][-n_avg:])
    mass_mean  = np.mean(history["mass"][-n_avg:])
    G_mean     = np.mean(history["G"][-n_avg:])

    a_err = abs(alpha_mean - CODATA["1/α"]) / CODATA["1/α"] * 100
    m_err = abs(mass_mean - CODATA["m_p/m_e"]) / CODATA["m_p/m_e"] * 100
    G_err = abs(G_mean - CODATA["G"]) / CODATA["G"] * 100

    print(f"\n   C (среднее) = {np.mean(history['C'][-n_avg:]):.6f}")
    print(f"   S (среднее) = {np.mean(history['S'][-n_avg:]):.6f}")
    print(f"\n   1/α     = {alpha_mean:.6f}  (CODATA: {CODATA['1/α']:.6f})  ошибка: {a_err:.4f}%")
    print(f"   m_p/m_e = {mass_mean:.4f}  (CODATA: {CODATA['m_p/m_e']:.4f})  ошибка: {m_err:.4f}%")
    print(f"   G       = {G_mean:.6e}  (CODATA: {CODATA['G']:.6e})  ошибка: {G_err:.4f}%")

    return history, alpha_mean, mass_mean, G_mean


# =============================================================================
# 5. ПЕРЕБОР РЕЖИМОВ
# =============================================================================

if __name__ == "__main__":

    # Список режимов для перебора
    regimes = [
        (0.013, "около ЧД"),
        (0.30,  "сильное поле"),
        (0.50,  "плазма"),
        (0.87,  "наш режим (CODATA)"),
        (0.95,  "высококогерентный оператор"),
        (0.99,  "ранняя Вселенная"),
    ]

    # Единый прогон для выбранного C_FFS
    print("\n" + "=" * 80)
    print("📊 ЕДИНЫЙ ПРОГОН")
    print("=" * 80)
    history, a, m, g = run_regime(C_FFS, S_CYCLE, n_steps=10000)

    # Графики для единого прогона
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].plot(history["C"], color='purple', linewidth=0.5)
    axes[0, 0].axhline(C_FFS, color='orange', linestyle='--', label=f'C_FFS = {C_FFS}')
    axes[0, 0].set_title(f'C(t) — C_FFS = {C_FFS}')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(history["alpha"], color='blue', linewidth=0.5)
    axes[0, 1].axhline(CODATA["1/α"], color='red', linestyle='--', label='CODATA')
    axes[0, 1].set_title('1/α(t)')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(history["mass"], color='green', linewidth=0.5)
    axes[0, 2].axhline(CODATA["m_p/m_e"], color='red', linestyle='--', label='CODATA')
    axes[0, 2].set_title('m_p/m_e(t)')
    axes[0, 2].legend()
    axes[0, 2].grid(alpha=0.3)

    axes[1, 0].plot(np.array(history["G"]) * 1e11, color='orange', linewidth=0.5)
    axes[1, 0].axhline(CODATA["G"] * 1e11, color='red', linestyle='--', label='CODATA')
    axes[1, 0].set_title('G(t) · 10¹¹')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(history["S"], color='red', linewidth=0.5)
    axes[1, 1].axhline(S_CYCLE, color='orange', linestyle='--', label=f'S = {S_CYCLE}')
    axes[1, 1].set_title('S(t)')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(history["C"], history["alpha"], color='blue', linewidth=0.5, alpha=0.6)
    axes[1, 2].axhline(CODATA["1/α"], color='red', linestyle='--')
    axes[1, 2].axvline(C_FFS, color='orange', linestyle='--')
    axes[1, 2].set_xlabel('C')
    axes[1, 2].set_ylabel('1/α')
    axes[1, 2].set_title('Фазовый портрет: C vs 1/α')
    axes[1, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('etvp_regimes_single.png', dpi=150)
    plt.show()

    # Перебор режимов
    print("\n" + "=" * 80)
    print("📊 ПЕРЕБОР РЕЖИМОВ")
    print("=" * 80)

    print(f"\n{'C_FFS':>10} | {'Название':<30} | {'1/α':>12} | {'m_p/m_e':>12} | {'G·10¹¹':>12}")
    print("-" * 100)

    for c_val, name in regimes:
        _, a, m, g = run_regime(c_val, S_CYCLE, n_steps=5000, label=f"({name})")
        print(f"{c_val:>10.4f} | {name:<30} | {a:>12.4f} | {m:>12.4f} | {g*1e11:>12.4f}")

    print("\n✅ Перебор завершён.")
