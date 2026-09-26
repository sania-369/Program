#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: Нейтрон из E8 через веса w_j
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================

ЦЕЛЬ:
  Понять, почему нейтрон имеет такую массу и энергию связи.
  Через спектр E8 и веса w_j — та же архитектура, что для констант.

КЛЮЧЕВЫЕ ФАКТЫ (CODATA):
  m_p = 938.27208816 МэВ
  m_e = 0.51099895 МэВ
  m_n = 939.56542052 МэВ
  E_связи = m_n - (m_p + m_e) = 0.782333 МэВ
  E_связи / m_e = 1.5310
================================================================================
"""

import numpy as np

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

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

print("=" * 80)
print("🌀 ETVP: Нейтрон из E8 через веса w_j")
print("=" * 80)

print(f"\n📊 Спектр E8:")
for i, lam in enumerate(eigvals):
    print(f"   λ[{i}] = {lam:.10f}")

print(f"\n   Сумма: {np.sum(eigvals):.10f}")
print(f"   Trace: {np.trace(E8):.10f}")

# =============================================================================
# 2. ВЕСА w_j (ТА ЖЕ АРХИТЕКТУРА, ЧТО ДЛЯ КОНСТАНТ)
# =============================================================================

print("\n" + "=" * 80)
print("📊 ВЕСА w_j ИЗ ПРОЕКЦИЙ E8")
print("=" * 80)

# Проекции для каждого индекса
def compute_weights(idx):
    """Считает веса для данного индекса λ_j."""
    v = np.abs(eigvecs[:, idx])
    return v / np.sum(v)

# Веса для разных мод
w_alpha = compute_weights(7)
w_mass  = compute_weights(2)
w_G     = compute_weights(3)

print(f"\n   Веса для 1/α (λ[7]):")
for i, w in enumerate(w_alpha):
    print(f"      w[{i}] = {w:.6f}")

print(f"\n   Веса для m_p/m_e (λ[2]):")
for i, w in enumerate(w_mass):
    print(f"      w[{i}] = {w:.6f}")

print(f"\n   Веса для G (λ[3]):")
for i, w in enumerate(w_G):
    print(f"      w[{i}] = {w:.6f}")

# =============================================================================
# 3. ПОИСК ВЕСОВ ДЛЯ НЕЙТРОНА
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПОИСК ВЕСОВ ДЛЯ НЕЙТРОНА")
print("=" * 80)

# CODATA
m_p_codata = 938.27208816
m_e_codata = 0.51099895
m_n_codata = 939.56542052
E_bind_codata = m_n_codata - m_p_codata - m_e_codata
ratio_codata = E_bind_codata / m_e_codata

print(f"\n   CODATA:")
print(f"   E_связи = {E_bind_codata:.6f} МэВ")
print(f"   E_связи / m_e = {ratio_codata:.6f}")

# Цель: найти комбинацию λ_j · w_j = 1.531
# Гипотеза: сумма λ_j · w_j, где w_j — проекции

print(f"\n   Гипотеза 1: ∑ λ_j · w_j (все моды)")
sum_all = np.sum(eigvals * w_mass)
print(f"   ∑ λ_j · w_mass = {sum_all:.6f}")
print(f"   Отношение к 1.531: {sum_all / ratio_codata:.6f}")

print(f"\n   Гипотеза 2: ∑ λ_j · w_j (с весами нейтрона)")
# Веса: ищем такие, чтобы сумма = 1.531
# Используем комбинацию w_mass и w_alpha

w_neutron = (w_mass + w_alpha) / 2
sum_neutron = np.sum(eigvals * w_neutron)
print(f"   ∑ λ_j · w_neutron = {sum_neutron:.6f}")
print(f"   Отношение к 1.531: {sum_neutron / ratio_codata:.6f}")

# =============================================================================
# 4. ПОИСК ТОЧНОЙ КОМБИНАЦИИ
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПОИСК ТОЧНОЙ КОМБИНАЦИИ")
print("=" * 80)

# Попробуем все пары λ_i · λ_j / λ_k
print(f"\n   Цель: 1.531")
print(f"\n   Простые комбинации:")

target = ratio_codata

# λ_i / λ_j
print(f"\n   λ_i / λ_j:")
for i in range(8):
    for j in range(8):
        if i != j and eigvals[j] > 0.01:
            r = eigvals[i] / eigvals[j]
            if 1.4 < r < 1.7:
                print(f"      λ[{i}]/λ[{j}] = {r:.6f}  (откл. {abs(r-target)/target*100:.3f}%)")

# λ_i - λ_j
print(f"\n   λ_i - λ_j:")
for i in range(8):
    for j in range(8):
        if i != j:
            d = eigvals[i] - eigvals[j]
            if 1.4 < d < 1.7:
                print(f"      λ[{i}]-λ[{j}] = {d:.6f}  (откл. {abs(d-target)/target*100:.3f}%)")

# λ_i + λ_j - λ_k
print(f"\n   λ_i + λ_j - λ_k:")
for i in range(8):
    for j in range(8):
        for k in range(8):
            if len({i,j,k}) == 3:
                s = eigvals[i] + eigvals[j] - eigvals[k]
                if 1.45 < s < 1.6:
                    print(f"      λ[{i}]+λ[{j}]-λ[{k}] = {s:.6f}  (откл. {abs(s-target)/target*100:.3f}%)")

# =============================================================================
# 5. ЧЕРЕЗ Φ, π, √3
# =============================================================================

print("\n" + "=" * 80)
print("📊 КОМБИНАЦИИ Φ, π, √3")
print("=" * 80)

print(f"\n   Цель: {target:.6f}")
print(f"\n   Простые комбинации:")

targets = {
    "π/2": PI/2,
    "Φ": PHI,
    "√3": SQ3,
    "Φ²/√3": PHI**2 / SQ3,
    "Φ + 1/Φ²": PHI + 1/PHI**2,
    "π/√3": PI / SQ3,
    "Φ · 1/√3": PHI / SQ3,
    "√3 - 1/Φ²": SQ3 - 1/PHI**2,
    "Φ - 1/Φ³": PHI - 1/PHI**3,
    "1 + 1/Φ²": 1 + 1/PHI**2,
    "1 + 1/√3": 1 + 1/SQ3,
    "1 + Φ/π": 1 + PHI/PI,
    "π/√3 - 1/4": PI/SQ3 - 0.25,
}

for name, val in targets.items():
    diff = abs(val - target) / target * 100
    marker = " ←" if diff < 2 else ""
    print(f"      {name:<20} = {val:.6f}  (откл. {diff:.3f}%){marker}")

# =============================================================================
# 6. ФОРМУЛА НЕЙТРОНА
# =============================================================================

print("\n" + "=" * 80)
print("📊 ФОРМУЛА НЕЙТРОНА")
print("=" * 80)

# Лучшая гипотеза: E_связи / m_e = λ[3] - λ[0] = 1.573
# Проверим точнее

print(f"\n   Гипотеза A: E_связи = m_e · (λ[3] - λ[0])")
E_bind_A = m_e_codata * (eigvals[3] - eigvals[0])
err_A = abs(E_bind_A - E_bind_codata) / E_bind_codata * 100
print(f"      E = {E_bind_A:.6f} МэВ")
print(f"      Ошибка = {err_A:.6f}%")

print(f"\n   Гипотеза B: E_связи = m_e · (λ[7] - λ[4])")
E_bind_B = m_e_codata * (eigvals[7] - eigvals[4])
err_B = abs(E_bind_B - E_bind_codata) / E_bind_codata * 100
print(f"      E = {E_bind_B:.6f} МэВ")
print(f"      Ошибка = {err_B:.6f}%")

print(f"\n   Гипотеза C: E_связи = m_e · (λ[5] - λ[2])")
E_bind_C = m_e_codata * (eigvals[5] - eigvals[2])
err_C = abs(E_bind_C - E_bind_codata) / E_bind_codata * 100
print(f"      E = {E_bind_C:.6f} МэВ")
print(f"      Ошибка = {err_C:.6f}%")

print(f"\n   Гипотеза D: E_связи = m_e · (Φ²/√3)")
E_bind_D = m_e_codata * (PHI**2 / SQ3)
err_D = abs(E_bind_D - E_bind_codata) / E_bind_codata * 100
print(f"      E = {E_bind_D:.6f} МэВ")
print(f"      Ошибка = {err_D:.6f}%")

# =============================================================================
# 7. ИТОГ
# =============================================================================

print("\n" + "=" * 80)
print("📌 ИТОГ")
print("=" * 80)

print(f"""
   CODATA: E_связи = {E_bind_codata:.6f} МэВ
           E_связи / m_e = {ratio_codata:.6f}

   Лучшие гипотезы из E8:
   A: λ[3] - λ[0] = {eigvals[3]-eigvals[0]:.6f}  (ошибка {err_A:.3f}%)
   B: λ[7] - λ[4] = {eigvals[7]-eigvals[4]:.6f}  (ошибка {err_B:.3f}%)
   C: λ[5] - λ[2] = {eigvals[5]-eigvals[2]:.6f}  (ошибка {err_C:.3f}%)
   D: Φ²/√3 = {PHI**2/SQ3:.6f}  (ошибка {err_D:.3f}%)

   Точной формулы пока нет. Но порядок — из E8.
""")

print("\n✅ Анализ завершён.")
