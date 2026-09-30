#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: Проверка уравнения удержания
================================================================================
Гипотеза: Удержание = Плотность × Объём
Фиксация = Удержание / Шум

Проверяем: число минимумов V зависит от C и объёма?
================================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    if n == 8:
        return np.array([
            [ 2, -1,  0,  0,  0,  0,  0,  0],
            [-1,  2, -1,  0,  0,  0,  0,  0],
            [ 0, -1,  2, -1,  0,  0,  0,  0],
            [ 0,  0, -1,  2, -1,  0,  0,  0],
            [ 0,  0,  0, -1,  2, -1,  0, -1],
            [ 0,  0,  0,  0, -1,  2, -1,  0],
            [ 0,  0,  0,  0,  0, -1,  2,  0],
            [ 0,  0,  0,  0, -1,  0,  0,  2]
        ], dtype=float)
    else:
        # Урезанная версия для n < 8
        E8 = build_E8(8)
        return E8[:n, :n]

# =============================================================================
# 2. ПОСТРОЕНИЕ M(C, n)
# =============================================================================

def build_M(C, n):
    """Строит матрицу M для данного C и размера n."""
    E8 = build_E8(n)
    M = E8.copy() * (1.0 + 0.1 * (C - C_FFS))
    M = M * (1.0 + EPSILON_FFS * (C - C_FFS))
    
    eigvals, eigvecs = np.linalg.eigh(M)
    mass_direction = eigvecs[:, np.argmin(eigvals)]
    
    for i in range(n):
        projection = np.dot(eigvecs[:, i], mass_direction)
        M[i, i] += abs(projection) * (C_MAX - C) / (C_MAX - C_MIN)
    
    return M

# =============================================================================
# 3. УДЕРЖАНИЕ
# =============================================================================

def compute_holding(C, n, n_samples=5000):
    """
    Удержание = Плотность × Объём.
    Плотность = C (или функция от C).
    Объём = n (размер системы).
    """
    M = build_M(C, n)
    eigvals, eigvecs = np.linalg.eigh(M)
    
    Psi = np.random.randn(n, n_samples)
    Psi = Psi / np.linalg.norm(Psi, axis=0)
    
    A = eigvecs.T @ Psi
    V = np.sum(eigvals[:, None] * np.abs(A)**2, axis=0)
    
    # Удержание
    density = C
    volume = n
    holding = density * volume
    
    # Шум
    noise = np.std(V) / np.mean(V) if np.mean(V) > 0 else 0
    
    # Фиксация
    fixation = holding / (noise + 1e-12)
    
    return {
        "C": C,
        "n": n,
        "V_mean": np.mean(V),
        "V_std": np.std(V),
        "noise": noise,
        "holding": holding,
        "fixation": fixation
    }

# =============================================================================
# 4. ПРОГОН
# =============================================================================

print("=" * 80)
print("🌀 ETVP: Проверка уравнения удержания")
print("=" * 80)

C_values = [0.5, 0.6, 0.7, 0.8, 0.87, 0.9, 0.95, 0.99, 1.0]
n_values = [3, 4, 5, 6, 7, 8]

results = []

for n in n_values:
    for C in C_values:
        r = compute_holding(C, n, n_samples=3000)
        results.append(r)
        print(f"  n={n} | C={C:.2f} | holding={r['holding']:.3f} | noise={r['noise']:.4f} | fixation={r['fixation']:.3f}")

# =============================================================================
# 5. АНАЛИЗ
# =============================================================================

print("\n" + "=" * 80)
print("📊 АНАЛИЗ")
print("=" * 80)

# Проверка: зависит ли fixation от holding?
holdings = [r["holding"] for r in results]
fixations = [r["fixation"] for r in results]

corr = np.corrcoef(holdings, fixations)[0, 1]
print(f"\n  Корреляция holding vs fixation: {corr:.6f}")

# Проверка: зависит ли noise от C?
C_arr = np.array([r["C"] for r in results])
noise_arr = np.array([r["noise"] for r in results])
corr_C_noise = np.corrcoef(C_arr, noise_arr)[0, 1]
print(f"  Корреляция C vs noise: {corr_C_noise:.6f}")

# Проверка: зависит ли fixation от C?
corr_C_fix = np.corrcoef(C_arr, np.array(fixations))[0, 1]
print(f"  Корреляция C vs fixation: {corr_C_fix:.6f}")

# Проверка: зависит ли fixation от n?
n_arr = np.array([r["n"] for r in results])
corr_n_fix = np.corrcoef(n_arr, np.array(fixations))[0, 1]
print(f"  Корреляция n vs fixation: {corr_n_fix:.6f}")

print("\n✅ Анализ завершён.")
