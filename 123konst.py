#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP v13.4 — ГРАФИКИ КОНСТАНТ В МАРКОВСКОМ ТАКТЕ
1/α(t), m_p/m_e(t), G(t) + C(t) + фазовый портрет.
"""

import numpy as np
import matplotlib.pyplot as plt

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

eigvals, _ = np.linalg.eigh(E8)
eigvals = np.sort(eigvals)

# =============================================================================
# 2. ФОРМУЛЫ
# =============================================================================

W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * (SQ2**2)
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4)  * (SQ2**-2)
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * (SQ2**2)

alpha_base = eigvals[7] * W_ALPHA
mass_base  = eigvals[2] * W_MASS
G_base     = eigvals[3] * W_G

CODATA_ALPHA = 137.035999084
CODATA_MASS  = 1836.15267343
CODATA_G     = 6.67430e-11

# Коэффициенты модуляции
COEFFS = {
    "1/α":     (0.1,  -0.05),
    "m_p/m_e": (0.05, -0.02),
    "G":       (-0.2,  0.1),
}

C_TARGET = 0.87
S_TARGET = 0.15

# =============================================================================
# 3. СИМУЛЯЦИЯ
# =============================================================================

n_steps = 5000
C = 0.999
S = 0.15

history = {
    "step": [], "C": [], "S": [],
    "alpha": [], "mass": [], "G": []
}

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

    history["step"].append(i)
    history["C"].append(C)
    history["S"].append(S)
    history["alpha"].append(alpha)
    history["mass"].append(mass)
    history["G"].append(G)

# В массивы
steps = np.array(history["step"])
Cs = np.array(history["C"])
Ss = np.array(history["S"])
alphas = np.array(history["alpha"])
masses = np.array(history["mass"])
Gs = np.array(history["G"])

# =============================================================================
# 4. ГРАФИКИ
# =============================================================================

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# --- 1/α ---
ax = axes[0, 0]
ax.plot(steps, alphas, color='blue', linewidth=0.8, alpha=0.8)
ax.axhline(CODATA_ALPHA, color='red', linestyle='--', linewidth=2,
           label=f'CODATA = {CODATA_ALPHA:.6f}')
ax.axhline(alpha_base, color='green', linestyle=':', linewidth=1.5,
           label=f'База (C=1) = {alpha_base:.6f}')
ax.set_xlabel('Такт')
ax.set_ylabel('1/α')
ax.set_title('1/α(t) — марковский такт')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- m_p/m_e ---
ax = axes[0, 1]
ax.plot(steps, masses, color='green', linewidth=0.8, alpha=0.8)
ax.axhline(CODATA_MASS, color='red', linestyle='--', linewidth=2,
           label=f'CODATA = {CODATA_MASS:.4f}')
ax.axhline(mass_base, color='blue', linestyle=':', linewidth=1.5,
           label=f'База (C=1) = {mass_base:.4f}')
ax.set_xlabel('Такт')
ax.set_ylabel('m_p/m_e')
ax.set_title('m_p/m_e(t) — марковский такт')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- G ---
ax = axes[0, 2]
ax.plot(steps, Gs * 1e11, color='orange', linewidth=0.8, alpha=0.8)
ax.axhline(CODATA_G * 1e11, color='red', linestyle='--', linewidth=2,
           label=f'CODATA = {CODATA_G*1e11:.6f}e-11')
ax.axhline(G_base * 1e11, color='blue', linestyle=':', linewidth=1.5,
           label=f'База (C=1) = {G_base*1e11:.6f}e-11')
ax.set_xlabel('Такт')
ax.set_ylabel('G · 10¹¹')
ax.set_title('G(t) — марковский такт')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- C(t) ---
ax = axes[1, 0]
ax.plot(steps, Cs, color='purple', linewidth=0.8)
ax.axhline(C_TARGET, color='orange', linestyle='--', linewidth=2,
           label=f'C_TARGET = {C_TARGET}')
ax.set_xlabel('Такт')
ax.set_ylabel('C')
ax.set_title('C(t) — когерентность поля')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- S(t) ---
ax = axes[1, 1]
ax.plot(steps, Ss, color='red', linewidth=0.8)
ax.axhline(S_TARGET, color='orange', linestyle='--', linewidth=2,
           label=f'S_TARGET = {S_TARGET}')
ax.set_xlabel('Такт')
ax.set_ylabel('S')
ax.set_title('S(t) — энтропия')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

# --- Фазовый портрет C vs 1/α ---
ax = axes[1, 2]
ax.plot(Cs, alphas, color='blue', linewidth=0.5, alpha=0.6)
ax.axhline(CODATA_ALPHA, color='red', linestyle='--', linewidth=2)
ax.axvline(C_TARGET, color='orange', linestyle='--', linewidth=2)
ax.set_xlabel('C')
ax.set_ylabel('1/α')
ax.set_title('Фазовый портрет: C vs 1/α')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('etvp_constants_5000.png', dpi=150)
plt.show()

# =============================================================================
# 5. СТАТИСТИКА
# =============================================================================

print("=" * 80)
print("📊 СТАТИСТИКА (последние 1000 тактов)")
print("=" * 80)

n = 1000
for name, arr, codata in [
    ("1/α", alphas[-n:], CODATA_ALPHA),
    ("m_p/m_e", masses[-n:], CODATA_MASS),
    ("G", Gs[-n:], CODATA_G),
]:
    mean = np.mean(arr)
    std = np.std(arr)
    err = abs(mean - codata) / codata * 100
    print(f"\n   {name}:")
    print(f"      Среднее  = {mean:.9f}")
    print(f"      Std      = {std:.9f}")
    print(f"      CODATA   = {codata:.9f}")
    print(f"      Ошибка   = {err:.6f}%")

print(f"\n   C (среднее) = {np.mean(Cs[-n:]):.6f}")
print(f"   S (среднее) = {np.mean(Ss[-n:]):.6f}")

print("\n✅ Готово.")
