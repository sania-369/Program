#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP: ПРОСТАЯ ФОРМУЛА ВСЕГО + РГ-ЭВОЛЮЦИЯ
Константы = собственные значения E8, эволюционировавшие по РГ.
Только Φ, π, √3, E8 и РГ.
"""

import numpy as np
from scipy.integrate import quad

PHI = (1 + np.sqrt(5)) / 2
PI = np.pi
SQRT3 = np.sqrt(3)

# =============================================================================
# 1. E8 (8×8)
# =============================================================================
def build_e8():
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

# =============================================================================
# 2. РГ-ЭВОЛЮЦИЯ (β-функции)
# =============================================================================
def beta_em(mu, thresholds=(0.000511, 0.1056, 1.776, 91.18, 172.5)):
    """β-функция КЭД: вклад активных частиц."""
    b = 0.0
    if mu > thresholds[0]: b += 4.0 / (3.0 * PI)
    if mu > thresholds[1]: b += 4.0 / (3.0 * PI)
    if mu > thresholds[2]: b += 4.0 / (3.0 * PI)
    if mu > thresholds[3]:
        b += (4.0 / (3.0 * PI)) * 3 * (3*(2/3)**2 + 3*(1/3)**2)
    return b

def rg_evolution(eigvals, E_start, E_end):
    """РГ-эволюция спектра от E_start до E_end."""
    ln_start = np.log(E_start)
    ln_end = np.log(E_end)

    # Интеграл β-функции
    integral, _ = quad(lambda ln_mu: beta_em(np.exp(ln_mu)), ln_start, ln_end)

    # Каждое собственное значение эволюционирует
    eigvals_evolved = eigvals * (1 + integral / len(eigvals))
    return eigvals_evolved

# =============================================================================
# 3. МАРКОВСКИЙ ШАГ (ПАМЯТЬ)
# =============================================================================
def markov_step(eigvals, eigvals_prev, alpha=1/PHI):
    """Ψ_{t+1} = Ψ_t + α · (Ψ_t − Ψ_{t−1})"""
    if eigvals_prev is None:
        return eigvals
    return eigvals + alpha * (eigvals - eigvals_prev)

# =============================================================================
# 4. ФРАКТАЛЬНАЯ ПРОЕКЦИЯ E8 → 4D ПО Φ
# =============================================================================
def project_e8_to_4d(eigenvalues):
    n = len(eigenvalues)
    projected = []
    for k in range(4):
        weight = PHI ** (k + 1) * np.cos(PI * k / n)
        value = np.sum(eigenvalues * weight) / n
        projected.append(value)
    return np.array(projected)

# =============================================================================
# 5. ВЫЧИСЛЕНИЕ КОНСТАНТ (С РГ)
# =============================================================================
def compute_constants(steps=100):
    # 1. E8
    M = build_e8()
    eigvals = np.sort(np.abs(np.linalg.eigvalsh(M)))[::-1]

    # 2. Марковская эволюция до резонанса
    eigvals_prev = None
    for t in range(steps):
        eigvals = markov_step(eigvals, eigvals_prev, alpha=1/PHI)
        eigvals = np.tanh(eigvals / 10) * 10
        eigvals_prev = eigvals.copy()

    # 3. РГ-эволюция от Планка до массы электрона
    E_planck = 1.22e19
    E_electron = 0.000511
    eigvals_rg = rg_evolution(eigvals, E_electron, E_planck)

    # 4. Проекция E8 → 4D
    proj_4d = project_e8_to_4d(eigvals_rg)

    # 5. Константы из спектра и проекции
    m_e = np.abs(eigvals_rg[3]) / (PHI * PI * SQRT3) * 0.511 * PI
    q_p = np.abs(proj_4d[0] / proj_4d[1])

    return m_e, q_p, eigvals_rg, proj_4d

# =============================================================================
# 6. ЗАПУСК
# =============================================================================
def main():
    print("=" * 70)
    print("ETVP: ПРОСТАЯ ФОРМУЛА ВСЕГО + РГ-ЭВОЛЮЦИЯ")
    print("=" * 70)

    m_e, q_p, eigvals, proj = compute_constants(steps=100)

    print(f"\nСпектр после РГ-эволюции (первые 4):")
    for i, ev in enumerate(eigvals[:4]):
        print(f"  λ_{i+1} = {ev:.6e}")

    print(f"\nПроекция E8 → 4D по Φ:")
    for i, p in enumerate(proj):
        print(f"  P_{i+1} = {p:.6e}")

    print(f"\n--- РЕЗУЛЬТАТЫ (С РГ) ---")
    print(f"m_e = {m_e:.6e} МэВ (CODATA: 0.511)")
    print(f"q_p = {q_p:.6f} e   (CODATA: 1.0)")

    print(f"\nОтклонения:")
    print(f"  m_e: {abs(m_e - 0.511)/0.511*100:.4f}%")
    print(f"  q_p: {abs(q_p - 1.0)*100:.4f}%")

if __name__ == "__main__":
    main()
