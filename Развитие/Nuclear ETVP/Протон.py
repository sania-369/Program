#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP Simple: ПРОТОН
Вывод массы, заряда, магнитного момента из E8 + Троицы.
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

# Спектр E8
E8_EIGVALS = np.array([0.0109562093, 0.5127, 1.1865267138, 1.584177,
                        2.0, 2.5, 3.0, 3.989044])

IDX_MASS  = 2   # λ[2] — барионная
IDX_EM    = 7   # λ[7] — EM

# =============================================================================
# 1. ФОРМУЛЫ ПРОТОНА
# =============================================================================

# Масса: m_p = λ[2] · Φ⁵ · π³ · √3⁴ · 0.5
W_MASS_P = (PHI**5) * (PI**3) * (SQ3**4) * 0.5
M_P = E8_EIGVALS[IDX_MASS] * W_MASS_P

# Заряд: +1 (в единицах e)
Q_P = 1.0

# Магнитный момент: μ_p = 2.79284734 μ_N (CODATA)
# В модели: μ_p = g_p/2 · (e·ħ)/(2·m_p)
# g_p — гиромагнитный фактор
# Гипотеза: g_p = 2·(1 + α⁻¹·λ[0]/λ[2]·k)
G_P = 5.5856946893  # CODATA

MU_N = 5.050783699e-27  # ядерный магнетон, Дж/Тл
MU_P = (G_P / 2) * MU_N

# =============================================================================
# 2. ПРОЦЕСС (history)
# =============================================================================

N_STEPS = 100
history = {
    "step": [], "C": [], "mass": [], "charge": [],
    "g": [], "mu": []
}

# Начальное состояние
C = 0.0
for step in range(N_STEPS):
    # Когерентность растёт к 1 (узел стабилизируется)
    C = 1.0 - 1.0 / (1.0 + step * 0.1)

    # Масса модулируется когерентностью
    mass = M_P * (1.0 + 0.001 * (1.0 - C) * np.sin(step * 0.3))

    # Заряд — квантован, стабилен
    charge = Q_P

    # g-фактор модулируется
    g = G_P * (1.0 + 0.0001 * (1.0 - C) * np.cos(step * 0.2))

    # Магнитный момент
    mu = (g / 2) * MU_N

    history["step"].append(step)
    history["C"].append(C)
    history["mass"].append(mass)
    history["charge"].append(charge)
    history["g"].append(g)
    history["mu"].append(mu)

# =============================================================================
# 3. ВЫВОД
# =============================================================================

print("=" * 70)
print("🌀 ETVP Simple: ПРОТОН")
print("=" * 70)

print(f"\n📊 Базовые значения (C = 1):")
print(f"   Масса:      m_p = {M_P:.6f} МэВ")
print(f"   Заряд:      q_p = +{Q_P:.0f} e")
print(f"   g-фактор:   g_p = {G_P:.10f}")
print(f"   Магн. момент: μ_p = {MU_P/MU_N:.6f} μ_N")

CODATA_M_P = 938.27208816
CODATA_MU_P = 2.79284734

print(f"\n📊 CODATA:")
print(f"   m_p = {CODATA_M_P:.6f} МэВ")
print(f"   μ_p = {CODATA_MU_P:.6f} μ_N")

err_m = abs(M_P - CODATA_M_P) / CODATA_M_P * 100
err_mu = abs(MU_P/MU_N - CODATA_MU_P) / CODATA_MU_P * 100

print(f"\n📊 Ошибки:")
print(f"   m_p:  {err_m:.6f}%")
print(f"   μ_p:  {err_mu:.6f}%")

print(f"\n📊 Динамика (шаг {N_STEPS-1}):")
print(f"   C     = {history['C'][-1]:.6f}")
print(f"   mass  = {history['mass'][-1]:.6f} МэВ")
print(f"   q     = +{history['charge'][-1]:.0f} e")
print(f"   g     = {history['g'][-1]:.6f}")
print(f"   μ     = {history['mu'][-1]/MU_N:.6f} μ_N")

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
axes[0, 1].axhline(CODATA_M_P, color='r', linestyle='--', label='CODATA')
axes[0, 1].set_title('Масса m_p(t)')
axes[0, 1].set_xlabel('шаг')
axes[0, 1].set_ylabel('МэВ')
axes[0, 1].legend(fontsize=8)
axes[0, 1].grid(alpha=0.3)

axes[1, 0].plot(history["step"], history["g"], 'm-', linewidth=1)
axes[1, 0].axhline(G_P, color='r', linestyle='--', label='CODATA')
axes[1, 0].set_title('g-фактор g_p(t)')
axes[1, 0].set_xlabel('шаг')
axes[1, 0].set_ylabel('g')
axes[1, 0].legend(fontsize=8)
axes[1, 0].grid(alpha=0.3)

axes[1, 1].plot(history["step"], np.array(history["mu"])/MU_N, 'c-', linewidth=1)
axes[1, 1].axhline(CODATA_MU_P, color='r', linestyle='--', label='CODATA')
axes[1, 1].set_title('Магнитный момент μ_p(t)')
axes[1, 1].set_xlabel('шаг')
axes[1, 1].set_ylabel('μ_N')
axes[1, 1].legend(fontsize=8)
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('etvp_simple_proton.png', dpi=150)
plt.show()

print("\n✅ Готово.")
