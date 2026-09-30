#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP: Расширенный поиск формулы фиксации
================================================================================
Проверяем несколько формул.
Ищем максимальную корреляцию.
================================================================================
"""

import numpy as np

# =============================================================================
# 0. БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI = np.pi
SQ3 = np.sqrt(3.0)
C_FFS = 0.87
S_CYCLE = 0.12
SIGMA = 0.001

# =============================================================================
# 1. ДАННЫЕ
# =============================================================================

C_op_values = [0.3, 0.5, 0.7, 0.8, 0.87, 0.95, 1.0]
n_values = [3, 4, 5, 6, 7, 8]
S_values = [0.05, 0.10, 0.12, 0.20, 0.30]

data = []
for C_op in C_op_values:
    for n in n_values:
        for S in S_values:
            holding = C_op * n
            noise = abs(S - S_CYCLE) + SIGMA
            fixation = holding / noise
            data.append({
                "C_op": C_op,
                "n": n,
                "S": S,
                "holding": holding,
                "noise": noise,
                "fixation": fixation
            })

# =============================================================================
# 2. ФОРМУЛЫ
# =============================================================================

def formula_power(d, alpha, beta, gamma):
    return (d["C_op"] ** alpha) * (d["n"] ** beta) / (d["S"] ** gamma + SIGMA)

def formula_log(d):
    return np.log(d["C_op"] + 1e-12) * np.log(d["n"]) / (d["S"] + SIGMA)

def formula_exp(d):
    return np.exp(d["C_op"] * d["n"]) / (d["S"] + SIGMA)

def formula_phi(d):
    return (PHI ** (d["C_op"] * d["n"])) / (d["S"] + SIGMA)

def formula_triad(d):
    return (PI ** d["C_op"]) * (SQ3 ** d["n"]) / (d["S"] + SIGMA)

def formula_phi_power(d, alpha, beta):
    return (PHI ** (alpha * d["C_op"])) * (PHI ** (beta * d["n"])) / (d["S"] + SIGMA)

# =============================================================================
# 3. ПРОВЕРКА
# =============================================================================

print("=" * 80)
print("🌀 ETVP: Расширенный поиск формулы фиксации")
print("=" * 80)

fix_arr = np.array([d["fixation"] for d in data])

# 3.1. Степенная
print("\n📊 Степенная: C_оп^α · n^β / S^γ")
best_power = None
best_corr_power = -1
for alpha in np.linspace(0.1, 10.0, 30):
    for beta in np.linspace(0.1, 10.0, 30):
        for gamma in np.linspace(0.1, 5.0, 10):
            vals = np.array([formula_power(d, alpha, beta, gamma) for d in data])
            corr = np.corrcoef(vals, fix_arr)[0, 1]
            if corr > best_corr_power:
                best_corr_power = corr
                best_power = (alpha, beta, gamma)

print(f"  Лучшие: α = {best_power[0]:.2f}, β = {best_power[1]:.2f}, γ = {best_power[2]:.2f}")
print(f"  Корреляция: {best_corr_power:.6f}")

# 3.2. Логарифмическая
vals_log = np.array([formula_log(d) for d in data])
corr_log = np.corrcoef(vals_log, fix_arr)[0, 1]
print(f"\n📊 Логарифмическая: ln(C_оп)·ln(n)/S")
print(f"  Корреляция: {corr_log:.6f}")

# 3.3. Экспоненциальная
vals_exp = np.array([formula_exp(d) for d in data])
corr_exp = np.corrcoef(vals_exp, fix_arr)[0, 1]
print(f"\n📊 Экспоненциальная: exp(C_оп·n)/S")
print(f"  Корреляция: {corr_exp:.6f}")

# 3.4. Через Φ
vals_phi = np.array([formula_phi(d) for d in data])
corr_phi = np.corrcoef(vals_phi, fix_arr)[0, 1]
print(f"\n📊 Через Φ: Φ^(C_оп·n)/S")
print(f"  Корреляция: {corr_phi:.6f}")

# 3.5. Через триаду
vals_triad = np.array([formula_triad(d) for d in data])
corr_triad = np.corrcoef(vals_triad, fix_arr)[0, 1]
print(f"\n📊 Через триаду: π^C_оп · √3^n / S")
print(f"  Корреляция: {corr_triad:.6f}")

# 3.6. Φ-степенная
print("\n📊 Φ-степенная: Φ^(α·C_оп) · Φ^(β·n) / S")
best_phi = None
best_corr_phi = -1
for alpha in np.linspace(0.1, 10.0, 30):
    for beta in np.linspace(0.1, 10.0, 30):
        vals = np.array([formula_phi_power(d, alpha, beta) for d in data])
        corr = np.corrcoef(vals, fix_arr)[0, 1]
        if corr > best_corr_phi:
            best_corr_phi = corr
            best_phi = (alpha, beta)

print(f"  Лучшие: α = {best_phi[0]:.2f}, β = {best_phi[1]:.2f}")
print(f"  Корреляция: {best_corr_phi:.6f}")

# =============================================================================
# 4. ИТОГ
# =============================================================================

print("\n" + "=" * 80)
print("📌 ИТОГ")
print("=" * 80)
print(f"  Степенная:       {best_corr_power:.6f}")
print(f"  Логарифмическая: {corr_log:.6f}")
print(f"  Экспоненциальная:{corr_exp:.6f}")
print(f"  Через Φ:         {corr_phi:.6f}")
print(f"  Через триаду:    {corr_triad:.6f}")
print(f"  Φ-степенная:     {best_corr_phi:.6f}")

print("\n✅ Поиск завершён.")
