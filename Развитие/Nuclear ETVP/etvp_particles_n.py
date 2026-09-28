#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: Заряд, магнитный момент, масса — p, e, n
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================

ЦЕЛЬ:
  Вывести заряд, магнитный момент и массу для p, e, n.
  Сравнить с CODATA.

ФОРМУЛЫ:
  Заряд: Q = n · e
  Магнитный момент: a_e = α/(2π), a_p = a_e·(m_p/m_e)/λ[2]
  Магнитный момент нейтрона: g_n = g_p - 3·π
  Масса: m_p = m_e·(m_p/m_e), m_n = m_p + m_e·2·α⁻¹·λ[0]/λ[2]
================================================================================
"""

import numpy as np

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)
SQ2 = np.sqrt(2.0)

C_MIN = 1.0 / (PHI ** 10)
C_MAX = 1.0 - 1.0 / (PHI ** 20)

# =============================================================================
# 1. E8
# =============================================================================

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

eigvals, eigvecs = np.linalg.eigh(E8)
idx = np.argsort(eigvals)
eigvals = eigvals[idx]
eigvecs = eigvecs[:, idx]

# =============================================================================
# 2. ФИЗИЧЕСКИЕ КОНСТАНТЫ
# =============================================================================

E_CHARGE = 1.602176634e-19
MU_B = 9.2740100783e-24
MU_N = 5.050783699e-27

CODATA_ALPHA_INV = 137.035999084
CODATA_M_E = 0.51099895
CODATA_M_P = 938.27208816
CODATA_M_N = 939.56542052
CODATA_MASS_RATIO = 1836.15267343

CODATA_A_E = 0.00115965218128
CODATA_A_P = 1.79284734465
CODATA_A_N = -1.9130427  # g_n/2

CODATA_MU_E = -9.2847647043e-24
CODATA_MU_P = 1.41060679736e-26
CODATA_MU_N = -9.6623651e-27

# =============================================================================
# 3. ФОРМУЛЫ ИЗ E8
# =============================================================================

W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4) * 0.5
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * 2

alpha_inv_base = eigvals[7] * W_ALPHA
mass_ratio_base = eigvals[2] * W_MASS

print("=" * 80)
print("🌀 ETVP: Частицы — заряд, момент, масса")
print("=" * 80)

print(f"\n📊 Спектр E8:")
for i, lam in enumerate(eigvals):
    print(f"   λ[{i}] = {lam:.10f}")

# =============================================================================
# 4. ЭЛЕКТРОН
# =============================================================================

print("\n" + "=" * 80)
print("📊 ЭЛЕКТРОН")
print("=" * 80)

n_e = -1
Q_e = n_e * E_CHARGE
alpha_e = 1.0 / alpha_inv_base
a_e = alpha_e / (2.0 * PI)
g_e = 2.0 * (1.0 + a_e)
mu_e = -g_e * MU_B * 0.5
m_e = CODATA_M_E

print(f"\n   ЗАРЯД: Q_e = {Q_e:.6e} Кл (CODATA: {-E_CHARGE:.6e}) — ошибка 0%")
print(f"   a_e = {a_e:.10f} (CODATA: {CODATA_A_E:.10f}) — ошибка {abs(a_e-CODATA_A_E)/CODATA_A_E*100:.6f}%")
print(f"   μ_e = {mu_e:.6e} Дж/Тл (CODATA: {CODATA_MU_E:.6e}) — ошибка {abs(mu_e-CODATA_MU_E)/abs(CODATA_MU_E)*100:.6f}%")
print(f"   m_e = {m_e:.8f} МэВ (CODATA, база)")

# =============================================================================
# 5. ПРОТОН
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПРОТОН")
print("=" * 80)

n_p = +1
Q_p = n_p * E_CHARGE
a_p = a_e * (mass_ratio_base / eigvals[2])
g_p = 2.0 * (1.0 + a_p)
mu_p = g_p * MU_N * 0.5
m_p = m_e * mass_ratio_base

print(f"\n   ЗАРЯД: Q_p = {Q_p:.6e} Кл (CODATA: {E_CHARGE:.6e}) — ошибка 0%")
print(f"   a_p = {a_p:.10f} (CODATA: {CODATA_A_P:.10f}) — ошибка {abs(a_p-CODATA_A_P)/CODATA_A_P*100:.6f}%")
print(f"   g_p = {g_p:.10f}")
print(f"   μ_p = {mu_p:.6e} Дж/Тл (CODATA: {CODATA_MU_P:.6e}) — ошибка {abs(mu_p-CODATA_MU_P)/abs(CODATA_MU_P)*100:.6f}%")
print(f"   m_p = {m_p:.8f} МэВ (CODATA: {CODATA_M_P:.8f}) — ошибка {abs(m_p-CODATA_M_P)/CODATA_M_P*100:.6f}%")

# =============================================================================
# 6. НЕЙТРОН
# =============================================================================

print("\n" + "=" * 80)
print("📊 НЕЙТРОН")
print("=" * 80)

# Заряд
Q_n = 0.0

# Магнитный момент
# Формула: g_n = g_p - 3·π
g_n = g_p - 3.0 * PI
a_n = g_n / 2.0 - 1.0
mu_n = g_n * MU_N * 0.5

# Масса
E_binding = m_e * 2.0 * alpha_inv_base * eigvals[0] / eigvals[2]
m_n = m_p + E_binding

print(f"\n   ЗАРЯД: Q_n = {Q_n} (точно)")

print(f"\n   МАГНИТНЫЙ МОМЕНТ:")
print(f"   Формула: g_n = g_p - 3·π")
print(f"   g_p = {g_p:.10f}")
print(f"   3·π = {3.0*PI:.10f}")
print(f"   g_n = {g_n:.10f}")
print(f"   CODATA: g_n = {2*(1+CODATA_A_N):.10f}")
print(f"   Ошибка: {abs(g_n - 2*(1+CODATA_A_N))/abs(2*(1+CODATA_A_N))*100:.6f}%")
print(f"\n   a_n = g_n/2 - 1 = {a_n:.10f}")
print(f"   CODATA: {CODATA_A_N:.10f}")
print(f"   Ошибка: {abs(a_n - CODATA_A_N)/abs(CODATA_A_N)*100:.6f}%")
print(f"\n   μ_n = g_n · μ_N · S = {mu_n:.6e} Дж/Тл")
print(f"   CODATA: {CODATA_MU_N:.6e} Дж/Тл")
print(f"   Ошибка: {abs(mu_n - CODATA_MU_N)/abs(CODATA_MU_N)*100:.6f}%")

print(f"\n   МАССА:")
print(f"   Формула: m_n = m_p + m_e · 2·α⁻¹·λ[0]/λ[2]")
print(f"   E_связи = {E_binding:.8f} МэВ")
print(f"   m_n = {m_n:.8f} МэВ")
print(f"   CODATA: {CODATA_M_N:.8f} МэВ")
print(f"   Ошибка: {abs(m_n - CODATA_M_N)/CODATA_M_N*100:.6f}%")

# =============================================================================
# 7. СВОДКА
# =============================================================================

print("\n" + "=" * 80)
print("📌 СВОДКА")
print("=" * 80)

print(f"""
   ЭЛЕКТРОН:
   - Q_e = {Q_e:.6e} Кл (точно)
   - a_e = {a_e:.10f} (ошибка {abs(a_e-CODATA_A_E)/CODATA_A_E*100:.6f}%)
   - μ_e = {mu_e:.6e} (ошибка {abs(mu_e-CODATA_MU_E)/abs(CODATA_MU_E)*100:.6f}%)
   - m_e = {m_e:.8f} МэВ (CODATA, база)

   ПРОТОН:
   - Q_p = {Q_p:.6e} Кл (точно)
   - a_p = {a_p:.10f} (ошибка {abs(a_p-CODATA_A_P)/CODATA_A_P*100:.6f}%)
   - μ_p = {mu_p:.6e} (ошибка {abs(mu_p-CODATA_MU_P)/abs(CODATA_MU_P)*100:.6f}%)
   - m_p = {m_p:.8f} МэВ (ошибка {abs(m_p-CODATA_M_P)/CODATA_M_P*100:.6f}%)

   НЕЙТРОН:
   - Q_n = {Q_n} (точно)
   - g_n = {g_n:.10f} (ошибка {abs(g_n - 2*(1+CODATA_A_N))/abs(2*(1+CODATA_A_N))*100:.6f}%)
   - μ_n = {mu_n:.6e} (ошибка {abs(mu_n-CODATA_MU_N)/abs(CODATA_MU_N)*100:.6f}%)
   - m_n = {m_n:.8f} МэВ (ошибка {abs(m_n-CODATA_M_N)/CODATA_M_N*100:.6f}%)
""")

# =============================================================================
# 8. ОШИБКИ
# =============================================================================

print("\n" + "=" * 80)
print("📊 ОШИБКИ")
print("=" * 80)

print(f"\n   Заряд:")
print(f"      Q_e = 0.000000%")
print(f"      Q_p = 0.000000%")
print(f"      Q_n = 0.000000%")

print(f"\n   Магнитный момент:")
print(f"      a_e = {abs(a_e-CODATA_A_E)/CODATA_A_E*100:.6f}%")
print(f"      a_p = {abs(a_p-CODATA_A_P)/CODATA_A_P*100:.6f}%")
print(f"      a_n = {abs(a_n-CODATA_A_N)/abs(CODATA_A_N)*100:.6f}%")
print(f"      μ_e = {abs(mu_e-CODATA_MU_E)/abs(CODATA_MU_E)*100:.6f}%")
print(f"      μ_p = {abs(mu_p-CODATA_MU_P)/abs(CODATA_MU_P)*100:.6f}%")
print(f"      μ_n = {abs(mu_n-CODATA_MU_N)/abs(CODATA_MU_N)*100:.6f}%")

print(f"\n   Масса:")
print(f"      m_e = 0.000000% (CODATA, база)")
print(f"      m_p = {abs(m_p-CODATA_M_P)/CODATA_M_P*100:.6f}%")
print(f"      m_n = {abs(m_n-CODATA_M_N)/CODATA_M_N*100:.6f}%")

print("\n✅ Анализ завершён.")
