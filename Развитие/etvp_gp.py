#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: Магнитный момент протона из E8
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================

ЦЕЛЬ:
  Найти формулу для a_p = g_p/2 - 1 из спектра E8.

ЦЕЛЬ:
  a_p = 1.79284734465 (CODATA)
  g_p = 5.5856946893
================================================================================
"""

import numpy as np
from itertools import combinations

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
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

eigvals, eigvecs = np.linalg.eigh(E8)
idx = np.argsort(eigvals)
eigvals = eigvals[idx]
eigvecs = eigvecs[:, idx]

# =============================================================================
# 2. ЦЕЛЬ
# =============================================================================

a_p_target = 1.79284734465

print("=" * 80)
print("🌀 ETVP: Магнитный момент протона из E8")
print("=" * 80)

print(f"\n🎯 Цель: a_p = {a_p_target:.10f}")
print(f"   g_p = 2·(1 + a_p) = {2*(1+a_p_target):.10f}")

print(f"\n📊 Спектр E8:")
for i, lam in enumerate(eigvals):
    print(f"   λ[{i}] = {lam:.10f}")

# =============================================================================
# 3. ГЕНЕРАЦИЯ КОМБИНАЦИЙ Φ, π, √3
# =============================================================================

print("\n" + "=" * 80)
print("📊 ГЕНЕРАЦИЯ КОМБИНАЦИЙ Φ, π, √3")
print("=" * 80)

combos = {}

for n in range(-5, 6):
    for m in range(-3, 4):
        for k in range(-3, 4):
            val = (PHI**n) * (PI**m) * (SQ3**k)
            if 0.5 < val < 3.0:
                name = f"Φ^{n}·π^{m}·√3^{k}"
                combos[name] = val

print(f"   Сгенерировано комбинаций: {len(combos)}")

# Сортируем по близости к цели
sorted_combos = sorted(combos.items(), key=lambda x: abs(x[1] - a_p_target))

print(f"\n   Топ-20 по близости к a_p = {a_p_target:.6f}:")
for name, val in sorted_combos[:20]:
    err = abs(val - a_p_target) / a_p_target * 100
    marker = " ←" if err < 1 else ""
    print(f"      {name:<25} = {val:.6f}  (откл. {err:.4f}%){marker}")

# =============================================================================
# 4. ПОИСК КОМБИНАЦИЙ λ
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПОИСК КОМБИНАЦИЙ λ")
print("=" * 80)

target = a_p_target
found = []

# Одиночные λ
print(f"\n   Одиночные λ:")
for i in range(8):
    r = eigvals[i]
    if abs(r - target) / target < 0.3:
        found.append((f"λ[{i}]", r, abs(r-target)/target*100))
        print(f"      λ[{i}] = {r:.6f}  (откл. {abs(r-target)/target*100:.3f}%)")

# Пары: λ_i + λ_j
print(f"\n   Пары: λ_i + λ_j:")
for i, j in combinations(range(8), 2):
    s = eigvals[i] + eigvals[j]
    if abs(s - target) / target < 0.1:
        found.append((f"λ[{i}]+λ[{j}]", s, abs(s-target)/target*100))
        print(f"      λ[{i}]+λ[{j}] = {s:.6f}  (откл. {abs(s-target)/target*100:.3f}%)")

# Пары: λ_i - λ_j
print(f"\n   Пары: λ_i - λ_j:")
for i in range(8):
    for j in range(8):
        if i != j:
            d = eigvals[i] - eigvals[j]
            if 1.5 < d < 2.1:
                if abs(d - target) / target < 0.05:
                    found.append((f"λ[{i}]-λ[{j}]", d, abs(d-target)/target*100))
                    print(f"      λ[{i}]-λ[{j}] = {d:.6f}  (откл. {abs(d-target)/target*100:.4f}%)")

# Тройки: λ_i + λ_j - λ_k
print(f"\n   Тройки: λ_i + λ_j - λ_k:")
for i in range(8):
    for j in range(8):
        for k in range(8):
            if len({i,j,k}) == 3:
                s = eigvals[i] + eigvals[j] - eigvals[k]
                if 1.5 < s < 2.1:
                    if abs(s - target) / target < 0.02:
                        found.append((f"λ[{i}]+λ[{j}]-λ[{k}]", s, abs(s-target)/target*100))
                        print(f"      λ[{i}]+λ[{j}]-λ[{k}] = {s:.6f}  (откл. {abs(s-target)/target*100:.4f}%)")

# =============================================================================
# 5. ПОИСК СВЯЗИ λ · (Φ, π, √3)
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПОИСК СВЯЗИ λ · (Φ, π, √3)")
print("=" * 80)

print(f"\n   a_p = λ_j · f(Φ, π, √3):")
results_lambda_f = []
for i in range(8):
    ratio = target / eigvals[i]
    for name, val in sorted_combos[:50]:
        r2 = ratio / val
        if 0.99 < r2 < 1.01:
            err = abs(eigvals[i] * val - target) / target * 100
            results_lambda_f.append((f"λ[{i}]·{name}", eigvals[i]*val, err))
            
if results_lambda_f:
    results_lambda_f_sorted = sorted(results_lambda_f, key=lambda x: x[2])
    for name, val, err in results_lambda_f_sorted[:10]:
        print(f"      {name:<30} = {val:.6f}  (откл. {err:.4f}%)")
else:
    print(f"      Точных связей λ · f не найдено")

# =============================================================================
# 6. ГИПОТЕЗА: a_p = π/√3 + поправка
# =============================================================================

print("\n" + "=" * 80)
print("📊 ГИПОТЕЗА: a_p = π/√3 + поправка")
print("=" * 80)

pi_sq3 = PI / SQ3
diff = target - pi_sq3
print(f"\n   π/√3 = {pi_sq3:.6f}")
print(f"   a_p - π/√3 = {diff:.6f}")
print(f"   diff / λ[0] = {diff / eigvals[0]:.4f}")
print(f"   diff / λ[1] = {diff / eigvals[1]:.4f}")
print(f"   diff / λ[2] = {diff / eigvals[2]:.4f}")

# Может, diff = λ[0]·π/2?
print(f"\n   diff = λ[i]·f(Φ, π, √3):")
for i in range(8):
    ratio = diff / eigvals[i]
    for name, val in sorted_combos[:50]:
        r2 = ratio / val
        if 0.99 < r2 < 1.01:
            print(f"      diff = λ[{i}]·{name} = {eigvals[i]*val:.6f}")

# =============================================================================
# 7. ЛУЧШИЕ РЕЗУЛЬТАТЫ
# =============================================================================

print("\n" + "=" * 80)
print("📌 ЛУЧШИЕ РЕЗУЛЬТАТЫ")
print("=" * 80)

if found:
    found_sorted = sorted(found, key=lambda x: x[2])
    print(f"\n   Из E8:")
    for name, val, err in found_sorted[:10]:
        print(f"      {name:<25} = {val:.6f}  (откл. {err:.4f}%)")
else:
    print(f"\n   Из E8 — точных комбинаций не найдено")

print(f"\n   Из Φ, π, √3:")
for name, val in sorted_combos[:5]:
    err = abs(val - target) / target * 100
    print(f"      {name:<25} = {val:.6f}  (откл. {err:.4f}%)")

# =============================================================================
# 8. ИТОГ
# =============================================================================

print("\n" + "=" * 80)
print("📌 ИТОГ")
print("=" * 80)

best_phi = sorted_combos[0]
best_phi_err = abs(best_phi[1] - target) / target * 100

best_lambda = found_sorted[0] if found else None
best_lambda_err = best_lambda[2] if best_lambda else None

print(f"""
   Цель: a_p = {target:.10f}

   Лучшая комбинация Φ, π, √3:
      {best_phi[0]} = {best_phi[1]:.6f}
      Отклонение: {best_phi_err:.4f}%
""")

if best_lambda:
    print(f"""
   Лучшая комбинация E8:
      {best_lambda[0]} = {best_lambda[1]:.6f}
      Отклонение: {best_lambda_err:.4f}%
""")
else:
    print(f"""
   Комбинаций из E8 не найдено.
""")

print("\n✅ Анализ завершён.")
