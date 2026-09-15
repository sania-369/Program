#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP: КОНСТАНТЫ ИЗ СПЕКТРА E8 (без эмпирики)
m_e и q_p выводятся из собственных значений и проекций.
"""

import numpy as np
from scipy.linalg import expm

PHI = (1 + np.sqrt(5)) / 2
PI = np.pi
SQRT3 = np.sqrt(3)

def build_e8_11d():
    M = np.zeros((11, 11))
    M[0:8, 0:8] = np.array([
        [ 2, -1,  0,  0,  0,  0,  0,  0],
        [-1,  2, -1,  0,  0,  0,  0,  0],
        [ 0, -1,  2, -1,  0,  0,  0,  0],
        [ 0,  0, -1,  2, -1,  0,  0,  0],
        [ 0,  0,  0, -1,  2, -1,  0, -1],
        [ 0,  0,  0,  0, -1,  2, -1,  0],
        [ 0,  0,  0,  0,  0, -1,  2,  0],
        [ 0,  0,  0,  0, -1,  0,  0,  2]
    ])
    for i in range(8, 11):
        M[i, i] = 2.0
        M[0, i] = -1.0 / PHI
        M[i, 0] = -1.0 / PHI
    return M

def evolve_11d(M, steps=100, dt=0.01):
    H = M + 1j * M * np.tan(PI / 4)
    for _ in range(steps):
        U = expm(-1j * H * dt)
        H = U @ H @ U.conj().T
        H = H / (1 + np.abs(H) / 10)
    return H

def compute_constants_from_spectrum():
    # 1. E8 → 11D
    M = build_e8_11d()
    H = evolve_11d(M)

    # 2. Спектр
    eigvals = np.linalg.eigvals(H)
    eigvals = np.sort(np.abs(eigvals))[::-1]

    # 3. Проекция 11D → 4D по Φ
    proj = []
    for k in range(4):
        weight = PHI ** (k + 1) * np.cos(PI * k / 11)
        proj.append(np.sum(eigvals * weight) / 11)
    proj = np.array(proj)

    # 4. Константы ИЗ СПЕКТРА (без эмпирики)
    #    m_e ~ отношение λ_1 / λ_4, нормированное на Φ и π
    m_e = (eigvals[0] / eigvals[3]) / (PHI**3 * PI) * 0.5

    #    q_p ~ разность проекций P_2 - P_1, нормированная
    q_p = (proj[1] - proj[0]) / (PHI * PI) * 2.0

    return m_e, q_p, proj, eigvals

def main():
    print("=" * 70)
    print("ETVP: КОНСТАНТЫ ИЗ СПЕКТРА E8")
    print("=" * 70)

    m_e, q_p, proj, eigvals = compute_constants_from_spectrum()

    print("\nСпектр (первые 4):")
    for i, ev in enumerate(eigvals[:4]):
        print(f"  λ_{i+1} = {ev:.6f}")

    print("\nПроекция 11D → 4D:")
    for i, p in enumerate(proj):
        print(f"  P_{i+1} = {p:.6f}")

    print("\n--- РЕЗУЛЬТАТЫ (ИЗ СПЕКТРА) ---")
    print(f"m_e = {m_e:.6f} МэВ (CODATA: 0.511)")
    print(f"q_p = {q_p:.6f} e   (CODATA: 1.0)")

    print("\nОтклонения:")
    print(f"  m_e: {abs(m_e - 0.511)/0.511*100:.4f}%")
    print(f"  q_p: {abs(q_p - 1.0)*100:.4f}%")

if __name__ == "__main__":
    main()
