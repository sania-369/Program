#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP v13.1 — ПОИСК ГЕОМЕТРИЧЕСКИХ МНОЖИТЕЛЕЙ
K_i из проекций E8. Множитель из Φ, π, √3.
"""

import numpy as np
from itertools import product

# =============================================================================
# 0. ГЕОМЕТРИЯ
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
# 2. СУММЫ K_i
# =============================================================================

K = np.zeros(8)
for i in range(8):
    for j in range(8):
        K[i] += eigvals[j] * abs(eigvecs[i, j])

print("=" * 80)
print("🌀 ETVP v13.1 — ПОИСК ГЕОМЕТРИЧЕСКИХ МНОЖИТЕЛЕЙ")
print("=" * 80)
print("\n📊 Суммы K_i = Σ λ_j · |v_j[i]|:")
for i, k in enumerate(K):
    print(f"   K[{i}] = {k:.10f}")

# Уникальные значения
unique_K = np.unique(np.round(K, 8))
print(f"\n   Уникальные значения K:")
for k in unique_K:
    print(f"      {k:.10f}")

# =============================================================================
# 3. CODATA
# =============================================================================

CODATA = {
    "1/α": 137.035999084,
    "m_p/m_e": 1836.15267343,
    "G": 6.67430e-11,
}

# =============================================================================
# 4. ГЕНЕРАЦИЯ МНОЖИТЕЛЕЙ ИЗ Φ, π, √3
# =============================================================================

print("\n" + "=" * 80)
print("🔍 ГЕНЕРАЦИЯ МНОЖИТЕЛЕЙ")
print("=" * 80)

# Собираем все возможные комбинации: Φ^n · π^m · (√3)^k · (√2)^l
multipliers = {}

for n in range(-10, 11):
    for m in range(-3, 4):
        for k in range(-3, 4):
            for l in range(-2, 3):
                val = (PHI**n) * (PI**m) * (SQ3**k) * (SQ2**l)
                if 1e-30 < val < 1e30:
                    name = f"Φ^{n}·π^{m}·√3^{k}·√2^{l}"
                    multipliers[name] = val

print(f"   Сгенерировано множителей: {len(multipliers)}")

# =============================================================================
# 5. ПОИСК ЛУЧШЕГО МНОЖИТЕЛЯ ДЛЯ КАЖДОЙ КОНСТАНТЫ
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПОИСК МНОЖИТЕЛЯ ДЛЯ КАЖДОЙ КОНСТАНТЫ")
print("=" * 80)

for cname, cval in CODATA.items():
    print(f"\n{'='*80}")
    print(f"   {cname} = {cval:.9f}")
    print(f"{'='*80}")

    best_overall = None
    best_overall_diff = 1e10

    for kname, kval in multipliers.items():
        for i, Ki in enumerate(K):
            if abs(Ki) < 1e-12:
                continue
            predicted = Ki * kval
            if predicted < 1e-30:
                continue
            ratio = cval / predicted
            diff = abs(ratio - 1.0)
            if diff < best_overall_diff:
                best_overall_diff = diff
                best_overall = (i, Ki, kname, kval, predicted, ratio)

    if best_overall:
        i, Ki, kname, kval, predicted, ratio = best_overall
        print(f"\n   Лучший результат:")
        print(f"      K[{i}] = {Ki:.10f}")
        print(f"      Множитель = {kname} = {kval:.10f}")
        print(f"      K[{i}] · множитель = {predicted:.9f}")
        print(f"      CODATA = {cval:.9f}")
        print(f"      Отношение = {ratio:.10f}")
        print(f"      Ошибка = {abs(ratio-1)*100:.6f}%")

        # Топ-5
        print(f"\n   Топ-5 совпадений:")
        candidates = []
        for kname, kval in multipliers.items():
            for i, Ki in enumerate(K):
                if abs(Ki) < 1e-12:
                    continue
                predicted = Ki * kval
                if predicted < 1e-30:
                    continue
                ratio = cval / predicted
                diff = abs(ratio - 1.0)
                candidates.append((diff, i, Ki, kname, kval, predicted, ratio))
        candidates.sort(key=lambda x: x[0])
        for rank, (diff, i, Ki, kname, kval, predicted, ratio) in enumerate(candidates[:5]):
            print(f"      {rank+1}. K[{i}]·{kname} = {predicted:.9f}  (ошибка {diff*100:.4f}%)")

# =============================================================================
# 6. ПРОВЕРКА ГИПОТЕЗЫ: МНОЖИТЕЛЬ ИЗ ОТДЕЛЬНЫХ Φ, π, √3
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПРОВЕРКА ПРОСТЫХ ГИПОТЕЗ")
print("=" * 80)

simple_hyps = {
    "Φ⁵·π": PHI**5 * PI,
    "Φ⁶·√2": PHI**6 * SQ2,
    "Φ⁷": PHI**7,
    "Φ⁸/2": PHI**8 / 2,
    "Φ⁶·√3/2": PHI**6 * SQ3 / 2,
    "Φ⁵·π/√3": PHI**5 * PI / SQ3,
    "Φ⁷/√2": PHI**7 / SQ2,
    "Φ⁶·π/√3": PHI**6 * PI / SQ3,
    "Φ⁷·√3/π": PHI**7 * SQ3 / PI,
    "Φ⁸·√2/π": PHI**8 * SQ2 / PI,
    "Φ¹⁰": PHI**10,
    "Φ¹¹": PHI**11,
    "Φ¹²": PHI**12,
    "Φ¹³": PHI**13,
    "Φ¹⁴": PHI**14,
}

K_unique = np.unique(np.round(K, 6))
print(f"\n   Уникальные K: {K_unique}")

for cname, cval in CODATA.items():
    print(f"\n   {cname} = {cval:.9f}")
    for kname, kval in simple_hyps.items():
        for Ki in K_unique:
            if abs(Ki) < 1e-12:
                continue
            predicted = Ki * kval
            if predicted < 1e-30:
                continue
            ratio = cval / predicted
            if 0.9 < ratio < 1.1:
                print(f"      K={Ki:.4f} · {kname} = {predicted:.6f}  |  отношение = {ratio:.6f}")

# =============================================================================
# 7. ПРОВЕРКА ЧЕРЕЗ λ_j НАПРЯМУЮ
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПРОВЕРКА ЧЕРЕЗ λ_j")
print("=" * 80)

print(f"\n   Собственные значения E8:")
for j, lam in enumerate(eigvals):
    print(f"      λ[{j}] = {lam:.10f}")

for cname, cval in CODATA.items():
    print(f"\n   {cname} = {cval:.9f}")
    for j, lam in enumerate(eigvals):
        if abs(lam) < 1e-12:
            continue
        ratio = cval / lam
        for kname, kval in simple_hyps.items():
            r2 = ratio / kval
            if 0.9 < r2 < 1.1:
                print(f"      λ[{j}]·{kname} = {lam*kval:.6f}  |  отношение = {r2:.6f}")

print("\n✅ Анализ завершён.")
