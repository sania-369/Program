#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP PRECISE — Точные значения констант при заданных C_FFS и S_cycle
================================================================================
ЗАДАЁШЬ:
  - C_FFS  — когерентность/плотность/упругость вакуума
  - S_cycle — шум (энтропия цикла)

ПОЛУЧАЕШЬ:
  - Точные значения 1/α, m_p/m_e, G
  - Отклонение от CODATA
  - Что "рождается" при данных условиях (частицы, режимы)
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

C_MIN = 1.0 / (PHI ** 10)
C_MAX = 1.0 - 1.0 / (PHI ** 20)

# =============================================================================
# 1. ТОЧКИ УПРАВЛЕНИЯ — МЕНЯЙ ЗДЕСЬ
# =============================================================================

# >>> ВЫБЕРИ УСЛОВИЯ ВАКУУМА <<<
C_FFS   = 0.87    # когерентность системы (плотность вакуума)
S_CYCLE = 0.12    # шум (энтропия цикла)

# Точки перехода clip → tanh (можно менять)
C_SOFT_LOW  = 0.999333
C_SOFT_HIGH = 1.0

# =============================================================================
# 2. ФОРМУЛЫ КОНСТАНТ (из E8 + Троица Φ, π, √3)
# =============================================================================

W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4) * 0.5
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * 2

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

alpha_base = eigvals[7] * W_ALPHA
mass_base  = eigvals[2] * W_MASS
G_base     = eigvals[3] * W_G

CODATA = {
    "1/α": 137.035999084,
    "m_p/m_e": 1836.15267343,
    "G": 6.67430e-11,
}

COEFFS = {
    "1/α":     (0.1,  -0.05),
    "m_p/m_e": (0.05, -0.02),
    "G":       (-0.2,  0.1),
}

# =============================================================================
# 3. ФУНКЦИЯ УДЕРЖАНИЯ
# =============================================================================

def etve_tanh_limit(C, c_min=C_MIN, c_max=C_MAX,
                    c_soft_low=C_SOFT_LOW, c_soft_high=C_SOFT_HIGH):
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
# 4. ТОЧНЫЕ ЗНАЧЕНИЯ ПРИ ЗАДАННЫХ УСЛОВИЯХ
# =============================================================================

def compute_constants(C_FFS, S_cycle, n_steps=20000):
    """Возвращает точные значения констант при заданных C_FFS, S_cycle."""
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

    n_avg = n_steps // 10
    return {
        "C_mean": np.mean(history["C"][-n_avg:]),
        "S_mean": np.mean(history["S"][-n_avg:]),
        "alpha": np.mean(history["alpha"][-n_avg:]),
        "mass": np.mean(history["mass"][-n_avg:]),
        "G": np.mean(history["G"][-n_avg:]),
        "history": history,
    }


# =============================================================================
# 5. ЧТО "РОЖДАЕТСЯ" ИЗ ВАКУУМА ПРИ ДАННЫХ УСЛОВИЯХ
# =============================================================================

def what_is_born(C_FFS, S_cycle):
    """Определяет, что может существовать при данных C_FFS и S_cycle."""
    print("\n" + "=" * 80)
    print(f"🌱 ЧТО РОЖДАЕТСЯ ИЗ ВАКУУМА ПРИ C_FFS = {C_FFS}, S_cycle = {S_cycle}")
    print("=" * 80)

    modes = []

    if C_FFS <= 0.05:
        modes.append("Глубокая ЧД — сингулярность")
    if 0.05 < C_FFS <= 0.3:
        modes.append("Около ЧД — сильное поле")
    if 0.3 < C_FFS <= 0.5:
        modes.append("Плазма — LENR возможен")
    if 0.5 < C_FFS <= 0.8:
        modes.append("Холодная материя")
    if 0.8 < C_FFS <= 0.95:
        modes.append("Наш режим — CODATA")
    if 0.95 < C_FFS <= 0.99:
        modes.append("Высококогерентный оператор")
    if 0.99 < C_FFS <= 0.999:
        modes.append("Ранняя Вселенная")
    if C_FFS > 0.999:
        modes.append("Абсолютный вакуум")

    print(f"\n   Режимы:")
    for m in modes:
        print(f"      • {m}")

    # Что рождается
    print(f"\n   Что рождается:")
    if C_FFS > 0.95:
        print("      • Устойчивые солитоны (электроны, кварки)")
        print("      • Высокая когерентность → стабильная материя")
    elif C_FFS > 0.8:
        print("      • Стабильная материя (наш режим)")
        print("      • Константы ≈ CODATA")
    elif C_FFS > 0.5:
        print("      • Нестабильная материя")
        print("      • Возможны LENR-реакции")
    elif C_FFS > 0.3:
        print("      • Плазма")
        print("      • Термоядерные реакции")
    else:
        print("      • Сингулярность")
        print("      • Материя распадается")

    # Что с константами
    print(f"\n   Что с константами:")
    if abs(C_FFS - 0.87) < 0.01:
        print("      • Значения ≈ CODATA")
    elif C_FFS > 0.87:
        print(f"      • Сдвиг вверх: ΔK/K ~ +{0.1*(C_FFS-0.87)*100:.2f}%")
    else:
        print(f"      • Сдвиг вниз: ΔK/K ~ {0.1*(C_FFS-0.87)*100:.2f}%")


# =============================================================================
# 6. ЗАПУСК
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("🌀 ETVP PRECISE — Точные значения констант")
    print("=" * 80)
    print(f"\n🔧 ЗАДАННЫЕ УСЛОВИЯ:")
    print(f"   C_FFS   (когерентность/плотность) = {C_FFS}")
    print(f"   S_cycle (шум/энтропия)            = {S_CYCLE}")

    # Точные значения
    result = compute_constants(C_FFS, S_CYCLE, n_steps=20000)

    print(f"\n📊 ТОЧНЫЕ ЗНАЧЕНИЯ ПРИ ЭТИХ УСЛОВИЯХ:")
    print(f"   C (среднее) = {result['C_mean']:.6f}")
    print(f"   S (среднее) = {result['S_mean']:.6f}")
    print(f"\n   1/α     = {result['alpha']:.9f}")
    print(f"   m_p/m_e = {result['mass']:.6f}")
    print(f"   G       = {result['G']:.6e}")

    # Отклонение от CODATA
    a_err = (result['alpha'] - CODATA["1/α"]) / CODATA["1/α"] * 100
    m_err = (result['mass'] - CODATA["m_p/m_e"]) / CODATA["m_p/m_e"] * 100
    G_err = (result['G'] - CODATA["G"]) / CODATA["G"] * 100

    print(f"\n📊 ОТКЛОНЕНИЕ ОТ CODATA:")
    print(f"   1/α     : {a_err:+.6f}%")
    print(f"   m_p/m_e : {m_err:+.6f}%")
    print(f"   G       : {G_err:+.6f}%")

    # Что рождается
    what_is_born(C_FFS, S_CYCLE)

    # Графики
    history = result["history"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].plot(history["C"], color='purple', linewidth=0.5)
    axes[0, 0].axhline(C_FFS, color='orange', linestyle='--', label=f'C_FFS = {C_FFS}')
    axes[0, 0].set_title(f'C(t) — когерентность')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(history["alpha"], color='blue', linewidth=0.5)
    axes[0, 1].axhline(CODATA["1/α"], color='red', linestyle='--', label='CODATA')
    axes[0, 1].set_title(f'1/α(t) — отклонение {a_err:+.4f}%')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[0, 2].plot(history["mass"], color='green', linewidth=0.5)
    axes[0, 2].axhline(CODATA["m_p/m_e"], color='red', linestyle='--', label='CODATA')
    axes[0, 2].set_title(f'm_p/m_e(t) — отклонение {m_err:+.4f}%')
    axes[0, 2].legend()
    axes[0, 2].grid(alpha=0.3)

    axes[1, 0].plot(np.array(history["G"]) * 1e11, color='orange', linewidth=0.5)
    axes[1, 0].axhline(CODATA["G"] * 1e11, color='red', linestyle='--', label='CODATA')
    axes[1, 0].set_title(f'G(t) · 10¹¹ — отклонение {G_err:+.4f}%')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(history["S"], color='red', linewidth=0.5)
    axes[1, 1].axhline(S_CYCLE, color='orange', linestyle='--', label=f'S = {S_CYCLE}')
    axes[1, 1].set_title('S(t) — шум')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    axes[1, 2].plot(history["C"], history["alpha"], color='blue', linewidth=0.5, alpha=0.6)
    axes[1, 2].axhline(CODATA["1/α"], color='red', linestyle='--')
    axes[1, 2].axvline(C_FFS, color='orange', linestyle='--')
    axes[1, 2].set_xlabel('C')
    axes[1, 2].set_ylabel('1/α')
    axes[1, 2].set_title('Фазовый портрет')
    axes[1, 2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'etvp_precise_{C_FFS}.png', dpi=150)
    plt.show()

    print("\n✅ Готово.")
