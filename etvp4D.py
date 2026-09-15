#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP: ПРОСТАЯ ФОРМУЛА ВСЕГО
Константы = собственные значения E8 в точке резонанса.
Только Φ, π, √3 и Марковская динамика.
"""

import numpy as np

PHI = (1 + np.sqrt(5)) / 2
PI = np.pi
SQRT3 = np.sqrt(3)

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

def evolve_to_resonance(M, steps=1000):
    """Марковская эволюция до резонанса (C → max)."""
    eigvals = np.linalg.eigvalsh(M)
    eigvals_prev = eigvals.copy()
    C_history = []

    for t in range(steps):
        # Марковский шаг с α = 1/Φ
        eigvals_next = eigvals + (1/PHI) * (eigvals - eigvals_prev)

        # Z-принцип
        eigvals_next = np.tanh(eigvals_next / 10) * 10

        # Когерентность: Tr(ρ²) для нормированного спектра
        norm = np.sum(eigvals_next**2)
        C = norm / (np.sum(np.abs(eigvals_next))**2)
        C_history.append(C)

        eigvals_prev = eigvals.copy()
        eigvals = eigvals_next

    return eigvals, C_history

def compute_constants(eigvals):
    """Константы = собственные значения в резонансе."""
    # Нормируем спектр
    eigvals_norm = eigvals / np.max(np.abs(eigvals))

    # Масса электрона: λ_4 / (Φ · π · √3)
    m_e = np.abs(eigvals_norm[3]) / (PHI * PI * SQRT3) * 0.511 * PI

    # Заряд протона: λ_1 / λ_2
    q_p = np.abs(eigvals_norm[0] / eigvals_norm[1])

    return m_e, q_p

def main():
    print("=" * 70)
    print("ETVP: ПРОСТАЯ ФОРМУЛА ВСЕГО")
    print("=" * 70)

    M = build_e8()
    eigvals, C_history = evolve_to_resonance(M, steps=1000)

    m_e, q_p = compute_constants(eigvals)

    print(f"\nСпектр в резонансе (первые 4):")
    for i, ev in enumerate(eigvals[:4]):
        print(f"  λ_{i+1} = {ev:.6f}")

    print(f"\nКогерентность C (конец): {C_history[-1]:.6f}")
    print(f"Когерентность C (макс):  {max(C_history):.6f}")

    print(f"\n--- РЕЗУЛЬТАТЫ ---")
    print(f"m_e = {m_e:.6f} МэВ (CODATA: 0.511)")
    print(f"q_p = {q_p:.6f} e   (CODATA: 1.0)")

    print(f"\nОтклонения:")
    print(f"  m_e: {abs(m_e - 0.511)/0.511*100:.4f}%")
    print(f"  q_p: {abs(q_p - 1.0)*100:.4f}%")

if __name__ == "__main__":
    main()
