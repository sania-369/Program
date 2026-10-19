"""
Поиск формул для масс поколений через спектр E8 и триаду (Φ, π, √3).

Идея: отношения масс фермионов могут выражаться через
отношения собственных значений E8, домноженные на степени Φ, π, √3.

Перебираем малые целые показатели a, b, c ∈ [-20, 20] и ищем
комбинации с точностью < 1%.
"""

import numpy as np
from itertools import product

# ============================================================
# 1. КОНСТАНТЫ
# ============================================================

PHI  = (1 + np.sqrt(5)) / 2
PI   = np.pi
SQRT3 = np.sqrt(3)

# Полный спектр E8 (из формулы Кокстера)
EXPS = [1, 7, 11, 13, 17, 19, 23, 29]
H_COX = 30

LAM = [2 - 2*np.cos(np.pi * m / H_COX) for m in EXPS]

print("=" * 70)
print("ПОЛНЫЙ СПЕКТР E8")
print("=" * 70)
for i, l in enumerate(LAM):
    print(f"  λ[{i}] = {l:.10f}   (m_k = {EXPS[i]})")
print()

# ============================================================
# 2. ЭКСПЕРИМЕНТАЛЬНЫЕ ОТНОШЕНИЯ МАСС
# ============================================================

# CODATA 2022 / PDG
M_E   = 0.51099895000    # МэВ
M_MU  = 105.6583755      # МэВ
M_TAU = 1776.86          # МэВ
M_P   = 938.27208816     # МэВ

TARGETS = {
    "m_e / m_p":   M_E / M_P,
    "m_mu / m_e":  M_MU / M_E,
    "m_tau / m_mu": M_TAU / M_MU,
}

print("=" * 70)
print("ЦЕЛЕВЫЕ ОТНОШЕНИЯ")
print("=" * 70)
for name, val in TARGETS.items():
    print(f"  {name:12s} = {val:.10f}")
print()

# ============================================================
# 3. ПОИСК КОМБИНАЦИЙ
# ============================================================

def search_combination(base, target, max_power=20, tol=0.01):
    """
    Ищем a, b, c такие, что
        base * Φ^a * π^b * √3^c  ≈  target
    с относительной ошибкой < tol.
    """
    results = []
    for a, b, c in product(range(-max_power, max_power+1), repeat=3):
        try:
            val = base * (PHI**a) * (PI**b) * (SQRT3**c)
        except (OverflowError, ZeroDivisionError):
            continue
        if target == 0 or not np.isfinite(val):
            continue
        err = abs(val - target) / abs(target)
        if err < tol:
            results.append((err, a, b, c, val))
    results.sort(key=lambda x: x[0])
    return results


# ============================================================
# 4. ПОИСК ДЛЯ КАЖДОГО ОТНОШЕНИЯ
# ============================================================

# --- (A) m_e / m_p ---
print("=" * 70)
print("ПОИСК: m_e / m_p")
print("=" * 70)
base = LAM[1] / LAM[2]  # лептонная / барионная мода
res = search_combination(base, TARGETS["m_e / m_p"], max_power=20, tol=0.05)
if res:
    for err, a, b, c, val in res[:5]:
        print(f"  Φ^{a:+d} · π^{b:+d} · √3^{c:+d}  →  {val:.10f}   (ошибка {err*100:.4f}%)")
else:
    print("  Не найдено в пределах ±20 и tol=5%")
print()

# --- (B) m_mu / m_e ---
print("=" * 70)
print("ПОИСК: m_mu / m_e")
print("=" * 70)
base = LAM[4] / LAM[1]  # III / I (или II / I — проверим оба)
print(f"  База λ[4]/λ[1] = {base:.6f}")
res = search_combination(base, TARGETS["m_mu / m_e"], max_power=10, tol=0.01)
if res:
    for err, a, b, c, val in res[:5]:
        print(f"  Φ^{a:+d} · π^{b:+d} · √3^{c:+d}  →  {val:.6f}   (ошибка {err*100:.4f}%)")
else:
    print("  Не найдено. Пробуем другие базы...")

# Перебор баз: все пары λ[i]/λ[j]
print("\n  Перебор всех баз λ[i]/λ[j]:")
for i in range(8):
    for j in range(8):
        if i == j or LAM[j] < 1e-6:
            continue
        base_ij = LAM[i] / LAM[j]
        res = search_combination(base_ij, TARGETS["m_mu / m_e"], max_power=8, tol=0.005)
        if res:
            err, a, b, c, val = res[0]
            print(f"    λ[{i}]/λ[{j}] · Φ^{a:+d} · π^{b:+d} · √3^{c:+d} = {val:.6f}  (ошибка {err*100:.4f}%)")
print()

# --- (C) m_tau / m_mu ---
print("=" * 70)
print("ПОИСК: m_tau / m_mu")
print("=" * 70)
target = TARGETS["m_tau / m_mu"]
print(f"  Цель: {target:.6f}")
for i in range(8):
    for j in range(8):
        if i == j or LAM[j] < 1e-6:
            continue
        base_ij = LAM[i] / LAM[j]
        res = search_combination(base_ij, target, max_power=8, tol=0.005)
        if res:
            err, a, b, c, val = res[0]
            print(f"    λ[{i}]/λ[{j}] · Φ^{a:+d} · π^{b:+d} · √3^{c:+d} = {val:.6f}  (ошибка {err*100:.4f}%)")
print()

# ============================================================
# 5. ДОПОЛНИТЕЛЬНО: m_e/m_p через ВСЕ базы
# ============================================================
print("=" * 70)
print("ПОИСК (расширенный): m_e / m_p через все базы λ[i]/λ[j]")
print("=" * 70)
target = TARGETS["m_e / m_p"]
print(f"  Цель: {target:.10f}")
for i in range(8):
    for j in range(8):
        if i == j or LAM[j] < 1e-6:
            continue
        base_ij = LAM[i] / LAM[j]
        res = search_combination(base_ij, target, max_power=15, tol=0.002)
        if res:
            err, a, b, c, val = res[0]
            print(f"    λ[{i}]/λ[{j}] · Φ^{a:+d} · π^{b:+d} · √3^{c:+d} = {val:.10f}  (ошибка {err*100:.4f}%)")
print()

print("=" * 70)
print("ГОТОВО")
print("=" * 70)
