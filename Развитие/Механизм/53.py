#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: Нелинейное уравнение удержания
================================================================================
Гипотеза: Удержание = C_оп^α · n^β
Фиксация = Удержание / шум

Ищем α, β, дающие максимальную корреляцию.
================================================================================
"""

import numpy as np

# =============================================================================
# 0. БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
C_MIN = 1.0 / (PHI ** 10)
C_MAX = 1.0 - 1.0 / (PHI ** 20)
C_FFS = 0.87
S_CYCLE = 0.12
EPSILON_FFS = 0.01

# =============================================================================
# 1. E8
# =============================================================================

def build_E8(n):
    """Строит матрицу Картана E8 размера n×n."""
    if n >= 8:
        return np.array([
            [ 2, -1,  0,  0,  0,  0,  0,  0],
            [-1,  2, -1,  0,  0,  0,  0,  0],
            [ 0, -1,  2, -1,  0,  0,  0,  0],
            [ 0,  0, -1,  2, -1,  0,  0,  0],
            [ 0,  0,  0, -1,  2, -1,  0, -1],
            [ 0,  0,  0,  0, -1,  2, -1,  0],
            [ 0,  0,  0,  0,  0, -1,  2,  0],
            [ 0,  0,  0,  0, -1,  0,  0,  2]
        ], dtype=float)[:n, :n]
    else:
        E8 = build_E8(8)
        return E8[:n, :n]

# =============================================================================
# 2. Û(C, n)
# =============================================================================

def build_U(C, n):
    """Строит оператор эволюции Û = exp(−i·M(C)·dt)."""
    E8 = build_E8(n)
    M = E8.copy() * (1.0 + 0.1 * (C - C_FFS))
    M = M * (1.0 + EPSILON_FFS * (C - C_FFS))
    
    eigvals, eigvecs = np.linalg.eigh(M)
    mass_direction = eigvecs[:, np.argmin(eigvals)]
    
    for i in range(n):
        projection = np.dot(eigvecs[:, i], mass_direction)
        M[i, i] += abs(projection) * (C_MAX - C) / (C_MAX - C_MIN)
    
    U = eigvecs @ np.diag(np.exp(-1j * eigvals * 0.1)) @ eigvecs.T.conj()
    return U

# =============================================================================
# 3. Ŵ(C_оп, n)
# =============================================================================

def build_W(C_op, n):
    """Строит оператор воли Ŵ."""
    w = np.zeros(n)
    w[0] = C_op
    if n > 1:
        w[1:] = (1 - C_op) / (n - 1)
    W = np.diag(w)
    return W

# =============================================================================
# 4. ПРОВЕРКА
# =============================================================================

print("=" * 80)
print("🌀 ETVP: Нелинейное уравнение удержания")
print("=" * 80)

C_op_values = [0.3, 0.5, 0.7, 0.8, 0.87, 0.95, 1.0]
n_values = [3, 4, 5, 6, 7, 8]
S_values = [0.05, 0.10, 0.12, 0.20, 0.30]

sigma = 0.001

# Собираем данные
data = []
for C_op in C_op_values:
    for n in n_values:
        for S in S_values:
            U = build_U(0.87, n)
            W = build_W(C_op, n)
            
            # Фиксация (из модели)
            holding = C_op * n
            noise = abs(S - S_CYCLE) + sigma
            fixation = holding / noise
            
            # Коммутатор (для проверки)
            comm = W @ U - U @ W
            comm_norm = np.linalg.norm(comm)
            
            data.append({
                "C_op": C_op,
                "n": n,
                "S": S,
                "holding": holding,
                "noise": noise,
                "fixation": fixation,
                "comm": comm_norm
            })

# Перебор α, β
print("\n🔍 Перебор α, β:")
print(f"{'α':<8} {'β':<8} {'Корреляция':<12}")
print("-" * 28)

best = None
best_corr = -1

for alpha in np.linspace(0.1, 5.0, 50):
    for beta in np.linspace(0.1, 5.0, 50):
        holdings = []
        fixations = []
        for d in data:
            h = (d["C_op"] ** alpha) * (d["n"] ** beta)
            f = h / d["noise"]
            holdings.append(h)
            fixations.append(f)
        
        corr = np.corrcoef(holdings, fixations)[0, 1]
        if corr > best_corr:
            best_corr = corr
            best = (alpha, beta)

print(f"\n  Лучшие: α = {best[0]:.4f}, β = {best[1]:.4f}")
print(f"  Корреляция: {best_corr:.6f}")

# Проверка с лучшими α, β
print(f"\n📊 Проверка с α = {best[0]:.4f}, β = {best[1]:.4f}:")

alpha, beta = best
holdings = []
fixations = []
for d in data:
    h = (d["C_op"] ** alpha) * (d["n"] ** beta)
    f = h / d["noise"]
    holdings.append(h)
    fixations.append(f)

print(f"  Корреляция holding vs fixation: {np.corrcoef(holdings, fixations)[0,1]:.6f}")

# Корреляции с отдельными переменными
C_arr = np.array([d["C_op"] for d in data])
n_arr = np.array([d["n"] for d in data])
S_arr = np.array([d["S"] for d in data])
fix_arr = np.array(fixations)

print(f"  Корреляция C_оп vs fixation: {np.corrcoef(C_arr, fix_arr)[0,1]:.6f}")
print(f"  Корреляция n vs fixation: {np.corrcoef(n_arr, fix_arr)[0,1]:.6f}")
print(f"  Корреляция S vs fixation: {np.corrcoef(S_arr, fix_arr)[0,1]:.6f}")

print("\n✅ Проверка завершена.")
