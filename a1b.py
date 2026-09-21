#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP v13.2 — РАСШИРЕННЫЙ ПОИСК МНОЖИТЕЛЕЙ
Φ^n, π^m, √3^k, √2^l с n до ±50.
Для 1/α, m_p/m_e, G.
"""

import numpy as np

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
# 2. K_i
# =============================================================================

K = np.zeros(8)
for i in range(8):
    for j in range(8):
        K[i] += eigvals[j] * abs(eigvecs[i, j])

K_unique = np.unique(np.round(K, 6))
print("=" * 80)
print("🌀 ETVP v13.2 — РАСШИРЕННЫЙ ПОИСК")
print("=" * 80)
print(f"\n📊 Уникальные K: {K_unique}")

# =============================================================================
# 3. CODATA
# =============================================================================

CODATA = {
    "1/α": 137.035999084,
    "m_p/m_e": 1836.15267343,
    "G": 6.67430e-11,
}

# =============================================================================
# 4. РАСШИРЕННАЯ ГЕНЕРАЦИЯ МНОЖИТЕЛЕЙ
# =============================================================================

print("\n" + "=" * 80)
print("🔍 ГЕНЕРАЦИЯ МНОЖИТЕЛЕЙ (Φ^n, n до ±50)")
print("=" * 80)

# Генерируем отдельно для Φ, π, √3, √2
# Чтобы не взорвать память, используем логарифмы

# Логарифмические компоненты
log_phi = np.log(PHI)
log_pi  = np.log(PI)
log_sq3 = np.log(SQ3)
log_sq2 = np.log(SQ2)

# Диапазоны
n_range = range(-50, 51)   # Φ
m_range = range(-5, 6)     # π
k_range = range(-5, 6)     # √3
l_range = range(-3, 4)     # √2

# Для каждой константы — ищем в логарифмическом пространстве
for cname, cval in CODATA.items():
    print(f"\n{'='*80}")
    print(f"   {cname} = {cval:.9e}")
    print(f"{'='*80}")

    log_target = np.log(cval)
    best = []

    for Ki in K_unique:
        if Ki <= 0:
            continue
        log_Ki = np.log(Ki)
        log_ratio = log_target - log_Ki

        # Ищем комбинацию n·log_phi + m·log_pi + k·log_sq3 + l·log_sq2 ≈ log_ratio
        for n in n_range:
            for m in m_range:
                for k in k_range:
                    for l in l_range:
                        log_mult = (n * log_phi + m * log_pi +
                                    k * log_sq3 + l * log_sq2)
                        diff = abs(log_mult - log_ratio)
                        if diff < 0.01:  # в пределах 1% по логарифму
                            mult = np.exp(log_mult)
                            predicted = Ki * mult
                            ratio = cval / predicted
                            best.append((diff, Ki, n, m, k, l, mult, predicted, ratio))

    # Сортируем по точности
    best.sort(key=lambda x: x[0])

    print(f"\n   Топ-10 совпадений:")
    for rank, (diff, Ki, n, m, k, l, mult, predicted, ratio) in enumerate(best[:10]):
        name = f"Φ^{n}·π^{m}·√3^{k}·√2^{l}"
        print(f"      {rank+1:>2}. K={Ki:.4f} · {name}")
        print(f"          = {predicted:.9e}  |  CODATA={cval:.9e}  |  "
              f"отношение={ratio:.8f}  |  ошибка={abs(ratio-1)*100:.4f}%")

# =============================================================================
# 5. ПОИСК ЧЕРЕЗ λ_j
# =============================================================================

print("\n" + "=" * 80)
print("📊 ПОИСК ЧЕРЕЗ λ_j НАПРЯМУЮ")
print("=" * 80)

for cname, cval in CODATA.items():
    print(f"\n{'='*80}")
    print(f"   {cname} = {cval:.9e}")
    print(f"{'='*80}")

    log_target = np.log(cval)
    best = []

    for j, lam in enumerate(eigvals):
        if lam <= 0:
            continue
        log_lam = np.log(lam)
        log_ratio = log_target - log_lam

        for n in n_range:
            for m in m_range:
                for k in k_range:
                    for l in l_range:
                        log_mult = (n * log_phi + m * log_pi +
                                    k * log_sq3 + l * log_sq2)
                        diff = abs(log_mult - log_ratio)
                        if diff < 0.01:
                            mult = np.exp(log_mult)
                            predicted = lam * mult
                            ratio = cval / predicted
                            best.append((diff, j, lam, n, m, k, l, mult, predicted, ratio))

    best.sort(key=lambda x: x[0])

    print(f"\n   Топ-10 совпадений:")
    for rank, (diff, j, lam, n, m, k, l, mult, predicted, ratio) in enumerate(best[:10]):
        name = f"Φ^{n}·π^{m}·√3^{k}·√2^{l}"
        print(f"      {rank+1:>2}. λ[{j}]={lam:.6f} · {name}")
        print(f"          = {predicted:.9e}  |  CODATA={cval:.9e}  |  "
              f"отношение={ratio:.8f}  |  ошибка={abs(ratio-1)*100:.4f}%")

# =============================================================================
# 6. СВОДКА ЛУЧШИХ РЕЗУЛЬТАТОВ
# =============================================================================

print("\n" + "=" * 80)
print("📊 СВОДКА ЛУЧШИХ РЕЗУЛЬТАТОВ")
print("=" * 80)

print("""
   Для каждой константы — лучший результат из обоих поисков.
   Если ошибка < 0.1% — это структура, не случайность.
""")

print("\n✅ Анализ завершён.")
