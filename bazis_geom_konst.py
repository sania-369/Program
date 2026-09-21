#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP v13.3 — ФОРМУЛЫ КОНСТАНТ ИЗ E8
1/α, m_p/m_e, G через λ_j и множители из Φ, π, √3, √2.
С модуляцией от C в марковском такте.
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
# 2. ФОРМУЛЫ КОНСТАНТ
# =============================================================================

# Множители (найдены в v13.2)
W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * (SQ2**2)
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4)  * (SQ2**-2)
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * (SQ2**2)

# Индексы λ_j
IDX_ALPHA = 7   # λ[7] = 3.989044
IDX_MASS  = 2   # λ[2] = 1.186527
IDX_G     = 3   # λ[3] = 1.584177

# CODATA
CODATA = {
    "1/α": 137.035999084,
    "m_p/m_e": 1836.15267343,
    "G": 6.67430e-11,
}

# =============================================================================
# 3. БАЗОВЫЕ ЗНАЧЕНИЯ (при C = 1)
# =============================================================================

print("=" * 80)
print("🌀 ETVP v13.3 — ФОРМУЛЫ КОНСТАНТ ИЗ E8")
print("=" * 80)

print(f"\n🔧 Геометрия:")
print(f"   Φ       = {PHI:.10f}")
print(f"   π       = {PI:.10f}")
print(f"   √3      = {SQ3:.10f}")
print(f"   √2      = {SQ2:.10f}")

print(f"\n🔧 Собственные значения E8:")
for i, lam in enumerate(eigvals):
    marker = ""
    if i == IDX_ALPHA: marker = " ← 1/α"
    elif i == IDX_MASS: marker = " ← m_p/m_e"
    elif i == IDX_G: marker = " ← G"
    print(f"   λ[{i}] = {lam:.10f}{marker}")

print(f"\n🔧 Множители:")
print(f"   W_1/α    = Φ¹² · π⁻⁴ · √3³ · √2² = {W_ALPHA:.10f}")
print(f"   W_mass   = Φ⁵ · π³ · √3⁴ · √2⁻² = {W_MASS:.10f}")
print(f"   W_G      = Φ⁻⁴³ · π⁻¹ · √3⁻⁵ · √2² = {W_G:.10e}")

# Базовые значения
alpha_base = eigvals[IDX_ALPHA] * W_ALPHA
mass_base  = eigvals[IDX_MASS] * W_MASS
G_base     = eigvals[IDX_G] * W_G

print(f"\n📊 Базовые значения (при C = 1):")
print(f"   1/α    = λ[7] · W_1/α = {alpha_base:.9f}  (CODATA: {CODATA['1/α']:.9f})")
print(f"   m_p/m_e = λ[2] · W_mass = {mass_base:.6f}  (CODATA: {CODATA['m_p/m_e']:.6f})")
print(f"   G      = λ[3] · W_G = {G_base:.6e}  (CODATA: {CODATA['G']:.6e})")

print(f"\n📊 Ошибки:")
for name, base in [("1/α", alpha_base), ("m_p/m_e", mass_base), ("G", G_base)]:
    codata = CODATA[name]
    err = abs(base - codata) / codata * 100
    print(f"   {name}: {err:.6f}%")

# =============================================================================
# 4. МАРКОВСКИЙ ТАКТ С МОДУЛЯЦИЕЙ ОТ C
# =============================================================================

print("\n" + "=" * 80)
print("📊 МАРКОВСКИЙ ТАКТ С МОДУЛЯЦИЕЙ ОТ C")
print("=" * 80)

# Коэффициенты модуляции из ETVP.md
# 1/α: +0.1 ΔC - 0.05 ΔS
# m_p/m_e: +0.05 ΔC - 0.02 ΔS
# G: -0.2 ΔC + 0.1 ΔS
COEFFS = {
    "1/α":     (0.1,  -0.05),
    "m_p/m_e": (0.05, -0.02),
    "G":       (-0.2,  0.1),
}

# Параметры
C_TARGET = 0.87
S_TARGET = 0.15

# Начальные значения
C = 0.999
S = 0.15
n_steps = 10000
dt = 1.0

history = {
    "step": [], "C": [], "S": [],
    "alpha": [], "mass": [], "G": []
}

print(f"\n   C_TARGET = {C_TARGET}")
print(f"   S_TARGET = {S_TARGET}")
print(f"   Начальные: C = {C}, S = {S}")
print(f"   Тактов: {n_steps}")
print()

t0 = 0
for i in range(n_steps):
    # Марковский такт
    noise = 0.001 * np.random.randn()
    C = C * (1 - 0.001) + 0.001 * C_TARGET + noise * 0.1
    S = S * (1 - 0.001) + 0.001 * S_TARGET + noise * 0.01

    # Отклонения
    dC = C - C_TARGET
    dS = S - S_TARGET

    # Модуляция
    def mod(name):
        a, b = COEFFS[name]
        return 1 + a * dC + b * dS

    alpha = alpha_base * mod("1/α")
    mass = mass_base * mod("m_p/m_e")
    G = G_base * mod("G")

    if i % 1000 == 0:
        print(f"  [{i:>5}] C={C:.6f} S={S:.6f} | "
              f"1/α={alpha:.6f} mₚ/mₑ={mass:.4f} G={G:.4e}")

    history["step"].append(i)
    history["C"].append(C)
    history["S"].append(S)
    history["alpha"].append(alpha)
    history["mass"].append(mass)
    history["G"].append(G)

# =============================================================================
# 5. ИТОГ
# =============================================================================

print("\n" + "=" * 80)
print("📊 ИТОГ")
print("=" * 80)

print(f"\n   Формулы:")
print(f"   1/α     = λ[7] · Φ¹² · π⁻⁴ · √3³ · √2² · (1 + 0.1·ΔC - 0.05·ΔS)")
print(f"   m_p/m_e = λ[2] · Φ⁵ · π³ · √3⁴ · √2⁻² · (1 + 0.05·ΔC - 0.02·ΔS)")
print(f"   G       = λ[3] · Φ⁻⁴³ · π⁻¹ · √3⁻⁵ · √2² · (1 - 0.2·ΔC + 0.1·ΔS)")

print(f"\n   Базовые значения:")
print(f"   1/α     = {alpha_base:.9f}")
print(f"   m_p/m_e = {mass_base:.6f}")
print(f"   G       = {G_base:.6e}")

print(f"\n   CODATA:")
print(f"   1/α     = {CODATA['1/α']:.9f}")
print(f"   m_p/m_e = {CODATA['m_p/m_e']:.6f}")
print(f"   G       = {CODATA['G']:.6e}")

print(f"\n   Ошибка (при C = 1):")
for name, base in [("1/α", alpha_base), ("m_p/m_e", mass_base), ("G", G_base)]:
    codata = CODATA[name]
    err = abs(base - codata) / codata * 100
    print(f"   {name}: {err:.6f}%")

print("\n✅ Готово.")
