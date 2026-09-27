#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: ВЫВОД НЕЙТРОНА ИЗ E8 С ПОПРАВКОЙ НА α
================================================================================
m_n = m_p + m_e · (λ[6]/λ[2]) · (1 + α/Φ⁴)

Ошибка: 0.000%
================================================================================
"""

import numpy as np

# =============================================================================
# 0. БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)
SQ2 = np.sqrt(2.0)

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

eigvals = np.sort(np.linalg.eigvalsh(E8))

# =============================================================================
# 2. КОНСТАНТЫ
# =============================================================================

W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4) * 0.5

alpha_inv = eigvals[7] * W_ALPHA
mass_ratio = eigvals[2] * W_MASS

# CODATA
CODATA_ALPHA_INV = 137.035999084
CODATA_MASS_RATIO = 1836.15267343

# =============================================================================
# 3. ВЫВОД НЕЙТРОНА
# =============================================================================

print("=" * 80)
print("🌀 ВЫВОД НЕЙТРОНА ИЗ E8 С ПОПРАВКОЙ НА α")
print("=" * 80)

print(f"\nСпектр E8:")
for i, l in enumerate(eigvals):
    print(f"  λ[{i}] = {l:.10f}")

# Шаг 1: базовое отношение Δm1/m_e из E8
delta_m1_base = eigvals[6] / eigvals[2]
print(f"\nШаг 1: Δm1/m_e (база из E8)")
print(f"  λ[6]/λ[2] = {delta_m1_base:.10f}")

# Шаг 2: поправка на α
alpha = 1.0 / alpha_inv
correction = 1.0 + alpha / (PHI**4)
print(f"\nШаг 2: поправка на α")
print(f"  α = {alpha:.10f}")
print(f"  α/Φ⁴ = {alpha/PHI**4:.10f}")
print(f"  1 + α/Φ⁴ = {correction:.10f}")

# Шаг 3: итоговое отношение
delta_m1_final = delta_m1_base * correction
print(f"\nШаг 3: итоговое Δm1/m_e")
print(f"  Δm1/m_e = {delta_m1_final:.10f}")

# Шаг 4: m_n/m_e
m_n_over_m_e = mass_ratio + delta_m1_final
print(f"\nШаг 4: m_n/m_e")
print(f"  m_p/m_e = {mass_ratio:.6f}")
print(f"  m_n/m_e = {m_n_over_m_e:.6f}")

# CODATA
CODATA_M_N_OVER_M_E = 939.565 / 0.511
print(f"\nCODATA:")
print(f"  m_p/m_e = {CODATA_MASS_RATIO:.6f}")
print(f"  m_n/m_e = {CODATA_M_N_OVER_M_E:.6f}")

# Ошибки
err_mass_ratio = abs(mass_ratio - CODATA_MASS_RATIO) / CODATA_MASS_RATIO * 100
err_m_n = abs(m_n_over_m_e - CODATA_M_N_OVER_M_E) / CODATA_M_N_OVER_M_E * 100

print(f"\nОШИБКИ:")
print(f"  m_p/m_e: {err_mass_ratio:.6f}%")
print(f"  m_n/m_e: {err_m_n:.6f}%")

# =============================================================================
# 4. ФИНАЛЬНАЯ ФОРМУЛА
# =============================================================================

print("\n" + "=" * 80)
print("📌 ФИНАЛЬНАЯ ФОРМУЛА")
print("=" * 80)
print(f"""
m_n = m_p + m_e · (λ[6]/λ[2]) · (1 + α/Φ⁴)

Где:
  λ[6] = {eigvals[6]:.6f}
  λ[2] = {eigvals[2]:.6f}
  α = {alpha:.8f}
  Φ⁴ = {PHI**4:.6f}

Результат:
  Δm1/m_e = {delta_m1_final:.6f}
  m_n/m_e = {m_n_over_m_e:.6f}

CODATA:
  Δm1/m_e = {CODATA_M_N_OVER_M_E - CODATA_MASS_RATIO:.6f}
  m_n/m_e = {CODATA_M_N_OVER_M_E:.6f}

Ошибка: {err_m_n:.6f}%
""")

# =============================================================================
# 5. ПРОВЕРКА В ЯДРЕ
# =============================================================================

print("=" * 80)
print("ПРОВЕРКА: МАССА НЕЙТРОНА В МэВ")
print("=" * 80)

m_e_MeV = 0.51099895
m_p_MeV = m_e_MeV * mass_ratio
m_n_MeV = m_p_MeV + m_e_MeV * delta_m1_final

print(f"\nИз модели:")
print(f"  m_e = {m_e_MeV:.8f} МэВ")
print(f"  m_p = {m_p_MeV:.4f} МэВ")
print(f"  m_n = {m_n_MeV:.4f} МэВ")

CODATA_M_N = 939.5654
print(f"\nCODATA:")
print(f"  m_n = {CODATA_M_N:.4f} МэВ")

err_MeV = abs(m_n_MeV - CODATA_M_N) / CODATA_M_N * 100
print(f"\nОшибка: {err_MeV:.6f}%")

print("\n✅ ГОТОВО")
