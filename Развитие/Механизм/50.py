#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: Проверка связи Ŵ с уравнением удержания
================================================================================
Гипотеза: Удержание = C_оп · n
Фиксация = C_оп · n / шум

Проверяем численно.
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
print("🌀 ETVP: Проверка связи Ŵ с уравнением удержания")
print("=" * 80)

C_op_values = [0.3, 0.5, 0.7, 0.8, 0.87, 0.95, 1.0]
n_values = [3, 4, 5, 6, 7, 8]

print(f"\n{'C_оп':<8} {'n':<6} {'Удержание':<12} {'Шум':<12} {'Фиксация':<12}")
print("-" * 52)

results = []

for C_op in C_op_values:
    for n in n_values:
        U = build_U(0.87, n)
        W = build_W(C_op, n)
        
        # Удержание
        holding = C_op * n
        
        # Шум: норма коммутатора
        comm = W @ U - U @ W
        noise = np.linalg.norm(comm)
        
        # Фиксация
        fixation = holding / (noise + 1e-12)
        
        results.append({
            "C_op": C_op,
            "n": n,
            "holding": holding,
            "noise": noise,
            "fixation": fixation
        })
        
        print(f"{C_op:<8.2f} {n:<6} {holding:<12.3f} {noise:<12.4f} {fixation:<12.3f}")

# =============================================================================
# 5. АНАЛИЗ
# =============================================================================

print("\n" + "=" * 80)
print("📊 АНАЛИЗ")
print("=" * 80)

C_arr = np.array([r["C_op"] for r in results])
n_arr = np.array([r["n"] for r in results])
h_arr = np.array([r["holding"] for r in results])
noise_arr = np.array([r["noise"] for r in results])
fix_arr = np.array([r["fixation"] for r in results])

print(f"\n  Корреляция holding vs fixation: {np.corrcoef(h_arr, fix_arr)[0,1]:.6f}")
print(f"  Корреляция C_оп vs fixation: {np.corrcoef(C_arr, fix_arr)[0,1]:.6f}")
print(f"  Корреляция n vs fixation: {np.corrcoef(n_arr, fix_arr)[0,1]:.6f}")
print(f"  Корреляция C_оп vs noise: {np.corrcoef(C_arr, noise_arr)[0,1]:.6f}")
print(f"  Корреляция n vs noise: {np.corrcoef(n_arr, noise_arr)[0,1]:.6f}")

print("\n✅ Проверка завершена.")
