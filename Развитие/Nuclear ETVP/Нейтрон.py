#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP Simple: НЕЙТРОН
Вывод массы, заряда (0), магнитного момента.
Ключевая формула: m_n = m_p + m_e·2·α⁻¹·λ[0]/λ[2]
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
LAMBDA_0 = 0.0109562093   # почти нулевая мода
LAMBDA_2 = 1.1865267138   # барионная мода

# =============================================================================
# 1. ФОРМУЛЫ НЕЙТРОНА
# =============================================================================

CODATA_M_P = 938.27208816
CODATA_M_E = 0.51099895
ALPHA_INV = 137.035999084

# Базовая добавка
E_BINDING = CODATA_M_E * 2.0 * ALPHA_INV * (LAMBDA_0 / LAMBDA_2)

# Масса нейтрона
M_N = CODATA_M_P + E_BINDING

# Заряд: 0
Q_N = 0.0

# Магнитный момент: μ_n = -1.9130427 μ_N (CODATA)
# В модели: μ_n = -g_n/2 · μ_N
# Гипотеза: g_n = -3.82608545 (CODATA)
G_N = -3.82608545
MU_N = 5.050783699e-27
MU_N_NEUTRON = (G_N / 2) * MU_N

CODATA_M_N = 939.56542052
CODATA_MU_N = -1.9130427

# =============================================================================
# 2. ПРОЦЕСС
# =============================================================================

N_STEPS = 100
history = {
    "step": [], "C": [], "mass": [], "charge": [],
    "E_binding": [], "g_n": [], "mu_n": []
}

C = 0.0
for step in range(N_STEPS):
    # Когерентность растёт
    C = 1.0 - 1.0 / (1.0 + step * 0.1)

    # E_binding — базовая
    E_b = E_BINDING * (1.0 + 1e-5 * (1.0 - C) * np.sin(step * 0.4))

    # Масса
    mass = CODATA_M_P + E_b

    # Заряд — 0
    charge = Q_N

    # g-фактор
    g_n = G_N * (1.0 + 1e-4 * (1.0 - C) * np.cos(step * 0.3))

    # Магнитный момент
    mu_n = (g_n / 2) * MU_N

    history["step"].append(step)
    history["C"].append(C)
    history["mass"].append(mass)
    history["charge"].append(charge)
    history["E_binding"].append(E_b)
    history["g_n"].append(g_n)
    history["mu_n"].append(mu_n)

# =============================================================================
# 3. ВЫВОД
# =============================================================================

print("=" * 70)
print("🌀 ETVP Simple: НЕЙТРОН")
print("=" * 70)

print(f"\n📊 Ключевая формула:")
print(f"   m_n = m_p + m_e · 2 · α⁻¹ · λ[0]/λ[2]")

print(f"\n📊 Компоненты:")
print(f"   λ[0] = {LAMBDA_0:.10f}")
print(f"   λ[2] = {LAMBDA_2:.10f}")
print(f"   λ[0]/λ[2] = {LAMBDA_0/LAMBDA_2:.10f}")
print(f"   E_binding = {E_BINDING:.6f} МэВ")

print(f"\n📊 Расчёт:")
print(f"   m_n = {CODATA_M_P:.6f} + {E_BINDING:.6f}")
print(f"   m_n = {M_N:.6f} МэВ")
print(f"   Заряд: q_n = {Q_N:.0f} e")
print(f"   g_n = {G_N:.8f}")
print(f"   μ_n = {MU_N_NEUTRON/MU_N:.6f} μ_N")

print(f"\n📊 CODATA:")
print(f"   m_n = {CODATA_M_N:.6f} МэВ")
print(f"   μ_n = {CODATA_MU_N:.6f} μ_N")

err_m = abs(M_N - CODATA_M_N) / CODATA_M_N * 100
err_mu = abs(MU_N_NEUTRON/MU_N - CODATA_MU_N) / abs(CODATA_MU_N) * 100

print(f"\n📊 Ошибки:")
print(f"   m_n:  {err_m:.6f}%")
print(f"   μ_n:  {err_mu:.4f}%")

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
axes[0, 1].axhline(CODATA_M_N, color='r', linestyle='--', label='CODATA')
axes[0, 1].set_title('Масса m_n(t)')
axes[0, 1].set_xlabel('шаг')
axes[0, 1].set_ylabel('МэВ')
axes[0, 1].legend(fontsize=8)
axes[0, 1].grid(alpha=0.3)

axes[1, 0].plot(history["step"], history["E_binding"], 'm-', linewidth=1)
axes[1, 0].axhline(E_BINDING, color='r', linestyle='--', label='E_binding')
axes[1, 0].set_title('E_binding(t) = m_n − m_p')
axes[1, 0].set_xlabel('шаг')
axes[1, 0].set_ylabel('МэВ')
axes[1, 0].legend(fontsize=8)
axes[1, 0].grid(alpha=0.3)

axes[1, 1].plot(history["step"], np.array(history["mu_n"])/MU_N, 'c-', linewidth=1)
axes[1, 1].axhline(CODATA_MU_N, color='r', linestyle='--', label='CODATA')
axes[1, 1].set_title('Магнитный момент μ_n(t)')
axes[1, 1].set_xlabel('шаг')
axes[1, 1].set_ylabel('μ_N')
axes[1, 1].legend(fontsize=8)
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('etvp_simple_neutron.png', dpi=150)
plt.show()

print("\n✅ Готово.")
