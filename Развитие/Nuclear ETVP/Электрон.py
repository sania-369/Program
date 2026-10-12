#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP Simple: ЭЛЕКТРОН
Вывод массы, заряда, магнитного момента (аномальный).
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

# =============================================================================
# 1. ФОРМУЛЫ ЭЛЕКТРОНА
# =============================================================================

# Масса: базовая единица
M_E = 0.51099895  # МэВ (CODATA)

# Заряд: -1
Q_E = -1.0

# Магнитный момент: μ_e = -1.00115965218128 μ_B (аномалия!)
# μ_B — магнетон Бора
# μ_e = g_e/2 · μ_B, где g_e = 2·(1 + a_e), a_e — аномалия
ALPHA = 1.0 / 137.035999084
A_E = ALPHA / (2 * PI)  # аномалия Швингера (первый порядок)
G_E = 2.0 * (1.0 + A_E)

MU_B = 9.2740100783e-24  # магнетон Бора, Дж/Тл
MU_E = -(G_E / 2) * MU_B  # отрицательный

CODATA_MU_E = -1.00115965218128

# =============================================================================
# 2. ПРОЦЕСС
# =============================================================================

N_STEPS = 100
history = {
    "step": [], "C": [], "mass": [], "charge": [],
    "a_e": [], "g_e": [], "mu_e": []
}

C = 0.0
for step in range(N_STEPS):
    # Когерентность растёт к 1
    C = 1.0 - 1.0 / (1.0 + step * 0.1)

    # Масса — базовая, стабильна
    mass = M_E * (1.0 + 1e-6 * (1.0 - C) * np.sin(step * 0.5))

    # Заряд — квантован
    charge = Q_E

    # Аномалия a_e — малая, стабильна
    a_e = A_E * (1.0 + 1e-5 * (1.0 - C) * np.cos(step * 0.3))

    # g-фактор
    g_e = 2.0 * (1.0 + a_e)

    # Магнитный момент
    mu_e = -(g_e / 2) * MU_B

    history["step"].append(step)
    history["C"].append(C)
    history["mass"].append(mass)
    history["charge"].append(charge)
    history["a_e"].append(a_e)
    history["g_e"].append(g_e)
    history["mu_e"].append(mu_e)

# =============================================================================
# 3. ВЫВОД
# =============================================================================

print("=" * 70)
print("🌀 ETVP Simple: ЭЛЕКТРОН")
print("=" * 70)

print(f"\n📊 Базовые значения:")
print(f"   Масса:      m_e = {M_E:.8f} МэВ")
print(f"   Заряд:      q_e = {Q_E:.0f} e")
print(f"   Аномалия:   a_e = {A_E:.10f} (α/2π)")
print(f"   g-фактор:   g_e = {G_E:.10f}")
print(f"   Магн. момент: μ_e = {MU_E/MU_B:.10f} μ_B")

print(f"\n📊 CODATA:")
print(f"   m_e = {M_E:.8f} МэВ")
print(f"   a_e = 0.00115965218128")
print(f"   g_e = 2.00231930436256")
print(f"   μ_e = -1.00115965218128 μ_B")

print(f"\n📊 Точность аномалии (α/2π):")
print(f"   CODATA a_e = 0.00115965218128")
print(f"   Расчёт a_e = {A_E:.10f}")
print(f"   Ошибка: {abs(A_E - 0.00115965218128)/0.00115965218128*100:.4f}%")

# =============================================================================
# 4. ГРАФИКИ
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 8))

axes[0, 0].plot(history["step"], history["C"], 'b-', linewidth=1.5)
axes[0, 0].set_title('Когерентность C(t)')
axes[0, 0].set_xlabel('шаг')
axes[0, 0].set_ylabel('C')
axes[0, 0].grid(alpha=0.3)

axes[0, 1].plot(history["step"], history["mass"], 'g-', linewidth=1)
axes[0, 1].axhline(M_E, color='r', linestyle='--', label='CODATA')
axes[0, 1].set_title('Масса m_e(t)')
axes[0, 1].set_xlabel('шаг')
axes[0, 1].set_ylabel('МэВ')
axes[0, 1].legend(fontsize=8)
axes[0, 1].grid(alpha=0.3)

axes[1, 0].plot(history["step"], history["a_e"], 'm-', linewidth=1)
axes[1, 0].axhline(0.00115965218128, color='r', linestyle='--', label='CODATA')
axes[1, 0].set_title('Аномалия a_e(t) = α/2π')
axes[1, 0].set_xlabel('шаг')
axes[1, 0].set_ylabel('a_e')
axes[1, 0].legend(fontsize=8)
axes[1, 0].grid(alpha=0.3)

axes[1, 1].plot(history["step"], np.array(history["mu_e"])/MU_B, 'c-', linewidth=1)
axes[1, 1].axhline(CODATA_MU_E, color='r', linestyle='--', label='CODATA')
axes[1, 1].set_title('Магнитный момент μ_e(t)')
axes[1, 1].set_xlabel('шаг')
axes[1, 1].set_ylabel('μ_B')
axes[1, 1].legend(fontsize=8)
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('etvp_simple_electron.png', dpi=150)
plt.show()

print("\n✅ Готово.")
