#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP v13.6 — k(C) + полный вывод таблицей
================================================================================
"""

import numpy as np
import time
from collections import deque
import sys

# =============================================================================
# 0. УПРАВЛЕНИЕ
# =============================================================================

C_FFS = 0.87
S_cycle = 0.87
K0 = 3.9
EPSILON_FFS = 0.01
NOISE_BASE = 0.001

# =============================================================================
# 1. БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

C_MIN = 1.0 / (PHI ** 10)
C_MAX = 1.0 - 1.0 / (PHI ** 20)

W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4) * 0.5
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * 2

IDX_ALPHA = 7
IDX_MASS  = 2
IDX_G     = 3

GAMMA = 1.0 / (PHI ** 12)
ETA   = 1.0 / (PHI ** 10)

# =============================================================================
# 2. НОВОЕ: k(C)
# =============================================================================

def k_of_C(C, k0=K0):
    """Упругость как функция когерентности. Защита от деления на ноль."""
    return k0 / (1.0 - C + 1e-6)

def etve_hyperbolic_dynamic(C):
    """Гиперболическая упругость с k(C)."""
    k = k_of_C(C)
    E = (C - C_MIN) / (C_MAX - C_MIN + 1e-12)
    E_norm = E / (1.0 + k * E) * (1.0 + k)
    return C_MIN + E_norm * (C_MAX - C_MIN)

# =============================================================================
# 3. CODATA
# =============================================================================

CODATA_ALPHA = 137.035999084
CODATA_MASS  = 1836.15267343
CODATA_G     = 6.67430e-11
CODATA_M_E   = 0.51099895
CODATA_M_P   = 938.27208816
CODATA_M_N   = 939.56542052
CODATA_A_E   = 0.00115965218128
CODATA_A_P   = 1.79284734465
CODATA_A_N   = -1.9130427
CODATA_MU_E  = -9.2847647043e-24
CODATA_MU_P  = 1.41060679736e-26
CODATA_MU_N  = -9.6623651e-27

E_CHARGE = 1.602176634e-19
MU_B = 9.2740100783e-24
MU_N = 5.050783699e-27

# =============================================================================
# 4. ЯДРО
# =============================================================================

class ETVEComplexCoreV136:
    def __init__(self, memory_depth=100):
        self.C_E8 = np.zeros((11, 11), dtype=float)
        self.C_E8[0:8, 0:8] = np.array([
            [ 2, -1,  0,  0,  0,  0,  0,  0],
            [-1,  2, -1,  0,  0,  0,  0,  0],
            [ 0, -1,  2, -1,  0,  0,  0,  0],
            [ 0,  0, -1,  2, -1,  0,  0,  0],
            [ 0,  0,  0, -1,  2, -1,  0, -1],
            [ 0,  0,  0,  0, -1,  2, -1,  0],
            [ 0,  0,  0,  0,  0, -1,  2,  0],
            [ 0,  0,  0,  0, -1,  0,  0,  2]
        ], dtype=float)

        eigvals_8, eigvecs_8 = np.linalg.eigh(self.C_E8[0:8, 0:8])
        idx = np.argsort(eigvals_8)
        self.E8_eigvals = eigvals_8[idx]
        self.E8_eigvecs = eigvecs_8[:, idx]

        self.alpha_base = self.E8_eigvals[IDX_ALPHA] * W_ALPHA
        self.mass_base  = self.E8_eigvals[IDX_MASS]  * W_MASS
        self.G_base     = self.E8_eigvals[IDX_G]     * W_G

        self.C = C_MAX
        self.S = 0.15
        self.step_counter = 0
        self.k_current = k_of_C(self.C)
        self.G = self.G_base

        self.m_e = CODATA_M_E
        self.m_p = CODATA_M_P
        self.m_n = CODATA_M_N
        self.Q_e = -E_CHARGE
        self.Q_p = +E_CHARGE
        self.Q_n = 0.0
        self.a_e = 0.0
        self.a_p = 0.0
        self.a_n = 0.0
        self.mu_e = 0.0
        self.mu_p = 0.0
        self.mu_n = 0.0

        self.real_particles = []
        self.virtual_particles = []
        self.memory_matrices = deque(maxlen=memory_depth)
        self.history = {k: [] for k in [
            "C", "S", "k", "alpha", "mass_ratio", "G",
            "m_p", "m_n", "m_e", "Q_e", "Q_p", "Q_n",
            "a_e", "a_p", "a_n", "mu_e", "mu_p", "mu_n"
        ]}
        self._build_memory_kernel()

    def _build_memory_kernel(self):
        lam = np.array([2.0, 1.5, 1.0, 0.8, 0.6, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01])
        lam = lam / np.sum(lam)
        def kernel(tau):
            return np.sum(lam * np.exp(-lam * tau))
        self.memory_kernel = kernel

    def _apply_memory(self, M):
        if len(self.memory_matrices) == 0:
            return M
        me = np.zeros_like(M, dtype=complex)
        tw = 0.0
        for i, (mat, _) in enumerate(self.memory_matrices):
            tau = len(self.memory_matrices) - i
            w = self.memory_kernel(tau)
            me += w * np.array(mat, dtype=complex)
            tw += w
        if tw > 0:
            me /= tw
            ms = (self.C - C_MIN) / (C_MAX - C_MIN)
            ms = np.clip(ms, 0.0, 1.0)
            return (1.0 - ms) * M + ms * me
        return M

    def _build_complex_matrix(self):
        M = self.C_E8.copy() * (1.0 + 0.1 * (self.C - C_FFS))
        M = M * (1.0 + EPSILON_FFS * (self.C - C_FFS))
        eigvals, eigvecs = np.linalg.eigh(M[0:8, 0:8])
        md = eigvecs[:, np.argmin(eigvals)]
        for i in range(8):
            M[i, i] += abs(np.dot(eigvecs[:, i], md)) * (C_MAX - self.C) / (C_MAX - C_MIN)
        for i in range(4, 11):
            M[i, i] += self.C * 0.1
        M = self._apply_memory(M)
        self.phi = (PI / 2.0) * (1.0 - (self.C - C_MIN) / (C_MAX - C_MIN))
        M_imag = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                M_imag[i, j] = M[i, j] * np.tan(self.phi + 0.1 * (i - j))
        M_imag = (M_imag + M_imag.T) / 2.0
        M_imag = M_imag + M * 0.05 * np.sin(self.S * self.step_counter)
        return M + 1j * M_imag

    def _update_particles(self):
        if self.C > C_MIN + (C_MAX - C_MIN) * 0.15 and len(self.real_particles) == 0:
            self.real_particles.append({"mass": 0.1, "charge": 0.1, "alive": True})
        if self.C < C_MIN + (C_MAX - C_MIN) * 0.05 and len(self.real_particles) > 0:
            self.real_particles = []
        if self.C > C_MIN + (C_MAX - C_MIN) * 0.10:
            if np.random.random() < 0.01 and len(self.virtual_particles) < 10:
                self.virtual_particles.append({"energy": np.random.uniform(0.1, 1.0), "age": 0, "alive": True})
        for v in self.virtual_particles[:]:
            v["age"] += 1
            if v["age"] > 5 or np.random.random() < 0.02:
                self.virtual_particles.remove(v)

    def update_field(self, dt):
        self.step_counter += 1
        M = self._build_complex_matrix()
        eigenvalues = np.linalg.eigvals(M)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]

        dC = self.C - C_FFS
        dS = self.S - S_cycle
        mod_alpha = 1.0 + 0.1 * dC - 0.05 * dS
        mod_mass  = 1.0 + 0.05 * dC - 0.02 * dS
        mod_G     = 1.0 - 0.2 * dC + 0.1 * dS

        alpha_inv = self.alpha_base * mod_alpha
        mass_ratio = self.mass_base * mod_mass
        G = self.G_base * mod_G
        alpha = 1.0 / alpha_inv

        m_p = self.m_e * mass_ratio
        E_binding = self.m_e * 2.0 * alpha_inv * self.E8_eigvals[0] / self.E8_eigvals[2]
        m_n = m_p + E_binding

        Q_e = -E_CHARGE
        Q_p = +E_CHARGE
        Q_n = 0.0

        a_e = alpha / (2.0 * PI)
        a_p = a_e * mass_ratio / self.E8_eigvals[2]
        a_n = -self.E8_eigvals[3] - 1.0/3.0

        g_e = 2.0 * (1.0 + a_e)
        g_p = 2.0 * (1.0 + a_p)
        g_n = 2.0 * a_n

        mu_e = -g_e * MU_B * 0.5
        mu_p = g_p * MU_N * 0.5
        mu_n = g_n * MU_N * 0.5

        self.m_p, self.m_n = m_p, m_n
        self.a_e, self.a_p, self.a_n = a_e, a_p, a_n
        self.mu_e, self.mu_p, self.mu_n = mu_e, mu_p, mu_n

        self.G = G
        self.alpha_inv = alpha_inv
        self.mass_ratio = mass_ratio
        self.memory_matrices.append((M, time.time()))

        return {
            "alpha_inv": alpha_inv, "mass_ratio": mass_ratio, "G": G,
            "m_e": self.m_e, "m_p": m_p, "m_n": m_n,
            "Q_e": Q_e, "Q_p": Q_p, "Q_n": Q_n,
            "a_e": a_e, "a_p": a_p, "a_n": a_n,
            "mu_e": mu_e, "mu_p": mu_p, "mu_n": mu_n
        }

    def evolve(self, entropy_flux=0.0, time_step=1.0):
        noise = NOISE_BASE * np.random.randn()
        self.C = self.C * (1.0 - GAMMA) + GAMMA * C_FFS + noise * 0.1
        self.S = self.S * (1.0 - ETA) + ETA * S_cycle + noise * 0.01
        self.S = max(0.0, min(1.0, self.S))

        self.k_current = k_of_C(self.C)
        self.C = etve_hyperbolic_dynamic(self.C)

        self._update_particles()
        result = self.update_field(time_step)

        self.history["C"].append(self.C)
        self.history["S"].append(self.S)
        self.history["k"].append(self.k_current)
        for key, val in result.items():
            self.history[key].append(val)
        return result


# =============================================================================
# 5. ТАБЛИЦА
# =============================================================================

def print_table(step, result, model):
    print("\n" + "=" * 80)
    print(f"📊 ТАКТ {step:,} | C = {model.C:.6f} | S = {model.S:.6f} | k = {model.k_current:.4f}")
    print("=" * 80)
    print(f"{'Величина':<18} {'Модель':<22} {'CODATA':<22} {'Ошибка %':<10}")
    print("-" * 75)

    rows = [
        ("1/α", result["alpha_inv"], CODATA_ALPHA),
        ("m_p/m_e", result["mass_ratio"], CODATA_MASS),
        ("G", result["G"], CODATA_G),
        ("m_e", result["m_e"], CODATA_M_E),
        ("m_p", result["m_p"], CODATA_M_P),
        ("m_n", result["m_n"], CODATA_M_N),
        ("Q_e", result["Q_e"], -E_CHARGE),
        ("Q_p", result["Q_p"], E_CHARGE),
        ("Q_n", result["Q_n"], 0.0),
        ("a_e", result["a_e"], CODATA_A_E),
        ("a_p", result["a_p"], CODATA_A_P),
        ("a_n", result["a_n"], CODATA_A_N),
        ("μ_e", result["mu_e"], CODATA_MU_E),
        ("μ_p", result["mu_p"], CODATA_MU_P),
        ("μ_n", result["mu_n"], CODATA_MU_N),
    ]

    for name, val, cod in rows:
        err = abs(val - cod) / abs(cod) * 100 if cod != 0 else 0
        print(f"{name:<18} {val:<22.6e} {cod:<22.6e} {err:<10.6f}")
    print("=" * 80)


# =============================================================================
# 6. ЗАПУСК
# =============================================================================

def run(n_steps=100_000, log_every=10_000):
    print("=" * 80)
    print("🌀 ETVP v13.6 — k(C), S ∝ |∇C|")
    print(f"   Тактов: {n_steps:,}, вывод каждые {log_every:,}")
    print(f"   C_FFS = {C_FFS}, S_cycle = {S_cycle}, k₀ = {K0}")
    print("=" * 80)

    model = ETVEComplexCoreV136(memory_depth=100)
    print(f"\n🔧 База (C = 1):")
    print(f"   1/α     = {model.alpha_base:.9f}")
    print(f"   m_p/m_e = {model.mass_base:.6f}")
    print(f"   G       = {model.G_base:.6e}")
    print(f"   k(0.87) = {k_of_C(0.87):.4f}")

    t0 = time.time()
    for i in range(n_steps):
        result = model.evolve(time_step=1.0)
        if (i + 1) % log_every == 0:
            print_table(i+1, result, model)
            elapsed = time.time() - t0
            print(f"  ⏱ {(i+1)/elapsed:.0f} такт/с | {elapsed:.1f} с")
            sys.stdout.flush()

    print("\n✅ ГОТОВО")


if __name__ == "__main__":
    run(n_steps=100_000, log_every=10_000)
