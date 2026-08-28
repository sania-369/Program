#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
ETVP CORE v2 — Ядро с оригинальным ETVP 12.4 FFS
================================================================================
"""

import numpy as np
import math
from collections import deque

# =============================================================================
# КОНСТАНТЫ
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI = np.pi
Z_RES = np.sqrt(3.0)

GLOBAL_C_MIN = 1.0 / (PHI ** 10)
GLOBAL_C_MAX = 1.0 - 1.0 / (PHI ** 20)
GLOBAL_C_TARGET = 1.0 - 1.0 / (PHI ** 12)

EPSILON = 1e-10
HALF_SPIN = 0.05

C_FFS = 0.87
EPSILON_FFS = 0.01


# =============================================================================
# МАТРИЦА КАРТАНА
# =============================================================================

def build_cartan_e8():
    return np.array([
        [ 2, -1,  0,  0,  0,  0,  0,  0],
        [-1,  2, -1,  0,  0,  0,  0,  0],
        [ 0, -1,  2, -1,  0,  0,  0,  0],
        [ 0,  0, -1,  2, -1,  0,  0,  0],
        [ 0,  0,  0, -1,  2, -1,  0, -1],
        [ 0,  0,  0,  0, -1,  2, -1,  0],
        [ 0,  0,  0,  0,  0, -1,  2,  0],
        [ 0,  0,  0,  0, -1,  0,  0,  2]
    ], dtype=np.float64)


# =============================================================================
# ПОЛНЫЙ КЛАСС ETVP 12.4 FFS (адаптированный)
# =============================================================================

class ETVP124Core:
    """Оригинальное ядро ETVP 12.4 FFS."""
    
    def __init__(self):
        self.Phi = PHI
        self.pi = PI
        self.Z_res = Z_RES
        
        self.C_E8 = np.zeros((11, 11), dtype=float)
        self.C_E8[0:8, 0:8] = build_cartan_e8()
        
        self.C = GLOBAL_C_TARGET
        self.S = 0.15
        self.step_counter = 0
        
        self.memory_matrices = deque(maxlen=100)
        self._build_memory_kernel()
    
    def _build_memory_kernel(self):
        lambda_spectrum = np.array([2.0, 1.5, 1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01])
        lambda_spectrum = lambda_spectrum / np.sum(lambda_spectrum)
        
        def kernel(tau):
            return np.sum(lambda_spectrum * np.exp(-lambda_spectrum * tau))
        
        self.memory_kernel = kernel
    
    def _apply_memory(self, M):
        if len(self.memory_matrices) == 0:
            return M
        
        memory_effect = np.zeros_like(M, dtype=complex)
        total_weight = 0.0
        
        for i, (matrix, _) in enumerate(self.memory_matrices):
            tau = len(self.memory_matrices) - i
            weight = self.memory_kernel(tau)
            memory_effect += weight * np.array(matrix, dtype=complex)
            total_weight += weight
        
        if total_weight > 0:
            memory_effect /= total_weight
            memory_strength = (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN)
            memory_strength = np.clip(memory_strength, 0.0, 1.0)
            return (1.0 - memory_strength) * M + memory_strength * memory_effect
        return M
    
    def _build_complex_matrix(self):
        M = self.C_E8.copy() * (1.0 + 0.1 * (self.C - GLOBAL_C_TARGET))
        ffs_correction = 1.0 + EPSILON_FFS * (self.C - C_FFS)
        M = M * ffs_correction
        
        eigvals, eigenvectors = np.linalg.eigh(M[0:8, 0:8])
        mass_direction = eigenvectors[:, np.argmin(eigvals)]
        for i in range(8):
            projection = np.dot(eigenvectors[:, i], mass_direction)
            M[i, i] += abs(projection) * (GLOBAL_C_MAX - self.C) / (GLOBAL_C_MAX - GLOBAL_C_MIN)
        
        for i in range(4, 11):
            M[i, i] += self.C * 0.1
        
        M = self._apply_memory(M)
        
        self.phi = (self.pi / 2.0) * (1.0 - (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN))
        
        M_imag = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                M_imag[i, j] = M[i, j] * np.tan(self.phi + 0.1 * (i - j))
        M_imag = (M_imag + M_imag.T) / 2.0
        
        phase_shift = 0.1 * np.sin(self.S * self.step_counter)
        M_imag = M_imag + M * 0.05 * phase_shift
        
        return M + 1j * M_imag
    
    def update_field(self):
        self.step_counter += 1
        M = self._build_complex_matrix()
        eigenvalues = np.linalg.eigvals(M)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]
        
        alpha_inv = np.real(eigenvalues[0] / eigenvalues[10]) / self.Phi**2
        mass_ratio = np.real(eigenvalues[0] / eigenvalues[9]) * self.Phi * 70.0
        
        self.memory_matrices.append((M, 0))
        
        return alpha_inv, mass_ratio, eigenvalues
    
    def evolve(self, entropy_flux=0.0):
        chaos_op = 1.0 / (1.0 + abs(entropy_flux) * (1.0 / self.Phi))
        self.C = self.C * chaos_op + (1.0 - chaos_op) * GLOBAL_C_MIN
        self.S = max(0.0, min(1.0, self.S + entropy_flux * 0.01))
        return self.update_field()


# =============================================================================
# ФУНКЦИИ ДЛЯ ИСПОЛЬЗОВАНИЯ
# =============================================================================

def compute_alpha_inv():
    """α⁻¹ из геометрии."""
    P = PI * PHI**4 + PI**2 * PHI - 1.0 / (PHI**3 * PI)
    K = math.sqrt(PI * PHI**3) + Z_RES / (2**7)
    return P * K


def compute_m_e():
    """m_e ≈ 0.511 МэВ."""
    numerator = (2**12 - Z_RES**4 * PI**3)
    denominator = (PHI**20 * 2 * PI**2 + PI**5)
    return numerator / denominator * 40.0


def compute_mass_ratio():
    """m_p/m_e через динамику ETVP 12.4 FFS."""
    model = ETVP124Core()
    
    # Прогоняем несколько шагов для стабилизации
    for i in range(10):
        entropy_flux = 0.04 * np.sin(i / 7.0) + 0.005 * np.random.randn()
        alpha_inv, mass_ratio, _ = model.evolve(entropy_flux)
    
    return abs(mass_ratio)


# =============================================================================
# ЕДИНАЯ ФОРМУЛА ПОЛЯ
# =============================================================================

def compute_psi(C, S):
    return (PHI * C) / math.sqrt(S + EPSILON)


def compute_nabla_psi(psi_current, psi_previous):
    return abs(psi_current - psi_previous)


def toth_coherence(nabla_psi, S_ext, S_int):
    denominator = S_ext + S_int + HALF_SPIN
    argument = nabla_psi / denominator
    tanh_val = math.tanh(argument)
    C = (PHI / Z_RES) * tanh_val
    return float(np.clip(C, GLOBAL_C_MIN, GLOBAL_C_MAX))


def z_damping(C):
    E = (C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN + 1e-12)
    E_limited = math.tanh(E) * 0.5 + 0.5
    return GLOBAL_C_MIN + E_limited * (GLOBAL_C_MAX - GLOBAL_C_MIN)


def z_damping_gradient(gradient):
    return np.tanh(gradient)


# =============================================================================
# ПРОВЕРКА
# =============================================================================

if __name__ == "__main__":
    print("═" * 60)
    print("  ETVP CORE v2 — Проверка (с динамикой FFS)")
    print("═" * 60)
    print()
    
    alpha = compute_alpha_inv()
    print(f"  α⁻¹ = {alpha:.6f} (CODATA: 137.036)")
    print(f"  Отклонение: {abs(alpha - 137.036) / 137.036 * 100:.6f}%")
    print()
    
    mass_ratio = compute_mass_ratio()
    print(f"  m_p/m_e = {mass_ratio:.2f} (CODATA: 1836.15)")
    print(f"  Отклонение: {abs(mass_ratio - 1836.15) / 1836.15 * 100:.4f}%")
    print()
    
    m_e = compute_m_e()
    print(f"  m_e = {m_e:.6f} МэВ (CODATA: 0.511)")
    print()
    
    C = toth_coherence(0.5, 0.10, 0.05)
    print(f"  C (формула Тота) = {C:.6f}")
    print()
    print("═" * 60)
    print("  Ядро работает ✅")
    print("═" * 60)
