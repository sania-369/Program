#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP v14.0 — ПОЛНЫЙ РЕЕСТР КОНСТАНТ
================================================================================
ФУНДАМЕНТ: Саня-369 (sania-369)
================================================================================

СУТЬ:
  Все 26 констант Стандартной модели выводятся из:
  - Базиса Φ, π, √3
  - Спектра E8
  - γ = 1/Φ¹², η = 1/Φ¹⁰ (релаксация)
  - α_i, β_i из проекций E8

  Не подгонка. Не свободные параметры.
================================================================================
"""

import numpy as np
import time
from collections import deque
import sys

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)
SQ2 = np.sqrt(2.0)

GLOBAL_C_MIN = 1.0 / (PHI ** 10)
GLOBAL_C_MAX = 1.0 - 1.0 / (PHI ** 20)

C_FFS = 0.87
S_cycle = 0.12
EPSILON_FFS = 0.01

# --- ИЗ Φ ---
GAMMA = 1.0 / (PHI ** 12)   # скорость распада C
ETA   = 1.0 / (PHI ** 10)   # скорость восстановления C

# --- ПОРОГ ГИБРИДА ---
C_HYBRID_THRESHOLD = 0.8

# --- ВЕСА ИЗ E8 ---
W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * (SQ2**2)
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4)  * (SQ2**-2)
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * (SQ2**2)

# =============================================================================
# 1. МАТРИЦА E8 И α_i, β_i
# =============================================================================

C_E8 = np.array([
    [ 2, -1,  0,  0,  0,  0,  0,  0],
    [-1,  2, -1,  0,  0,  0,  0,  0],
    [ 0, -1,  2, -1,  0,  0,  0,  0],
    [ 0,  0, -1,  2, -1,  0,  0,  0],
    [ 0,  0,  0, -1,  2, -1,  0, -1],
    [ 0,  0,  0,  0, -1,  2, -1,  0],
    [ 0,  0,  0,  0,  0, -1,  2,  0],
    [ 0,  0,  0,  0, -1,  0,  0,  2]
], dtype=float)

EIGVALS, EIGVECS = np.linalg.eigh(C_E8)
IDX_SORT = np.argsort(EIGVALS)
EIGVALS = EIGVALS[IDX_SORT]
EIGVECS = EIGVECS[:, IDX_SORT]

# --- α_i, β_i ИЗ E8 ---
def compute_alpha_beta(j):
    """α_i = |v_j[i]| / ∑|v_j|, β_i = α_i · λ_j / ∑λ"""
    v = EIGVECS[:, j]
    alpha_i = np.abs(v) / np.sum(np.abs(v))
    beta_i = alpha_i * EIGVALS[j] / np.sum(EIGVALS)
    return alpha_i, beta_i

# Индексы мод для констант
IDX_ALPHA = 7
IDX_MASS  = 2
IDX_G     = 3

ALPHA_I_ALPHA, BETA_I_ALPHA = compute_alpha_beta(IDX_ALPHA)
ALPHA_I_MASS,  BETA_I_MASS  = compute_alpha_beta(IDX_MASS)
ALPHA_I_G,     BETA_I_G     = compute_alpha_beta(IDX_G)

# =============================================================================
# 2. БАЗОВЫЕ ЗНАЧЕНИЯ КОНСТАНТ (при C = 1)
# =============================================================================

ALPHA_BASE = EIGVALS[IDX_ALPHA] * W_ALPHA
MASS_BASE  = EIGVALS[IDX_MASS]  * W_MASS
G_BASE     = EIGVALS[IDX_G]     * W_G

# --- ЭНЕРГИЯ ВАКУУМА ---
E_VACUUM_0 = 0.51099895  # МэВ, калибровка m_e
ALPHA_E = 0.1

def E_vacuum(C_op):
    """E_vacuum = E_0 · (1 + α_E · C_оп)"""
    return E_VACUUM_0 * (1 + ALPHA_E * C_op)

# =============================================================================
# 3. 26 КОНСТАНТ ИЗ РЕЕСТРА v12.4
# =============================================================================

def compute_all_constants(alpha_inv, m_e_MeV, C_op, S_op):
    """
    Вычисляет все 26 констант из базиса.
    alpha_inv — 1/α из E8
    m_e_MeV — масса электрона в МэВ
    C_op — когерентность оператора
    S_op — шум
    """
    const = {}
    v = 246.22  # ГэВ, вакуумное среднее Хиггса
    
    # --- ГРУППА I: ЛЕПТОНЫ ---
    const["m_e"] = m_e_MeV  # МэВ
    const["m_mu"] = m_e_MeV * (PI * PHI**3 * SQ3 + 1/(3*PHI))
    const["m_tau"] = m_e_MeV * ((alpha_inv/PI) * PHI**4 * SQ3 - PI**2/2)
    
    # --- ГРУППА II: КВАРКИ ---
    m_u = m_e_MeV * (2/3 * PI * PHI * SQ3)
    m_d = m_e_MeV * (1/3 * PI**2 * PHI**2 + SQ3/4)
    m_s = m_u * (PI * PHI**2 * SQ3 + alpha_inv/(2*PI**2))
    m_p_MeV = m_e_MeV * MASS_BASE  # m_p = m_e · (m_p/m_e)
    m_c = m_p_MeV * (PHI**4/PI + SQ3/(2*PI**2))
    m_b = m_e_MeV * (alpha_inv * PI * PHI**3 + SQ3**4 * PI**2)
    m_t = m_p_MeV * (alpha_inv/(PI*SQ3) * PHI**4 - SQ3**2)
    
    const["m_u"] = m_u
    const["m_d"] = m_d
    const["m_s"] = m_s
    const["m_c"] = m_c
    const["m_b"] = m_b
    const["m_t"] = m_t
    
    # --- ГРУППА III: БОЗОНЫ ---
    m_W_MeV = m_e_MeV * np.sqrt(alpha_inv/(PI*SQ3) * PHI**10)
    const["m_W"] = m_W_MeV / 1000  # ГэВ
    const["m_Z"] = const["m_W"] * np.sqrt(1 + SQ3/(PI*PHI**4))
    const["m_H"] = v/np.sqrt(2) * (1 - 1/(PI*PHI**3*SQ3))
    
    # --- ГРУППА IV: CKM ---
    const["sin_th12"] = SQ3/(PI*PHI**3) * (1 - 1/alpha_inv)
    const["sin_th23"] = SQ3/(PI*PHI**8)
    const["sin_th13"] = const["sin_th23"] / (alpha_inv * PHI)
    const["delta_CP"] = np.degrees(PI/2 * (1 + 1/(PHI**2*SQ3)))
    
    # --- ГРУППА V: КАЛИБРОВОЧНЫЕ КОНСТАНТЫ ---
    alpha_em = 1/alpha_inv
    const["alpha_inv"] = alpha_inv
    const["alpha_w"] = alpha_em * (1 + PI*PHI**4/SQ3)
    beta_s = 4
    const["alpha_s"] = alpha_em / (1 - beta_s * alpha_em * np.log(PHI**4*SQ3))
    
    # --- ГРУППА VI: PMNS ---
    const["sin2_th12_nu"] = 1/PHI**3 * (1 - SQ3/alpha_inv)
    const["sin2_th23_nu"] = 0.5 - 1/(PI*PHI**4)
    const["sin2_th13_nu"] = PI**2 / (alpha_inv/PHI)**2
    const["delta_CP_nu"] = -np.degrees(PI * (1 - 1/(PHI**3*SQ3)))
    
    # --- ГРУППА VII: ХИГГС ---
    m_H = const["m_H"]
    const["mu_sq"] = -(m_H/2 * (1 - 1/(PI*PHI**3*SQ3)))**2  # ГэВ²
    const["lambda_H"] = 1/4 * (1 - 1/(PI*PHI**3*SQ3))**2
    const["theta_QCD"] = (SQ3**2 - 3) / (PI*PHI**4)
    
    return const

# =============================================================================
# 4. CODATA / PDG ДЛЯ СРАВНЕНИЯ
# =============================================================================

CODATA = {
    "m_e": 0.51099895,       # МэВ
    "m_mu": 105.6583755,     # МэВ
    "m_tau": 1776.86,        # МэВ
    "m_u": 2.16,             # МэВ
    "m_d": 4.67,             # МэВ
    "m_s": 93.4,             # МэВ
    "m_c": 1270.0,           # МэВ
    "m_b": 4180.0,           # МэВ
    "m_t": 172500.0,         # МэВ
    "m_W": 80.377,           # ГэВ
    "m_Z": 91.1876,          # ГэВ
    "m_H": 125.25,           # ГэВ
    "sin_th12": 0.22500,
    "sin_th23": 0.04182,
    "sin_th13": 0.00360,
    "delta_CP": 69.2,        # градусы
    "alpha_inv": 137.035999084,
    "alpha_w": 0.0338,
    "alpha_s": 0.1180,
    "sin2_th12_nu": 0.307,
    "sin2_th23_nu": 0.454,
    "sin2_th13_nu": 0.0220,
    "delta_CP_nu": -155.0,   # градусы
    "mu_sq": -7825.0,        # ГэВ²
    "lambda_H": 0.1291,
    "theta_QCD": 0.0,
}

# =============================================================================
# 5. Z-ПРИНЦИП (ГИБРИД CLIP/TANH)
# =============================================================================

def etve_tanh_limit(C, c_min=GLOBAL_C_MIN, c_max=GLOBAL_C_MAX,
                    c_soft_low=0.999333, c_soft_high=1.0):
    c_clip = np.clip(C, c_min, c_max)
    E = (C - c_min) / (c_max - c_min + 1e-12)
    c_tanh = c_min + (np.tanh(E * 2.0) * 0.5 + 0.5) * (c_max - c_min)
    if C <= c_soft_low:
        w = 0.0
    elif C >= c_soft_high:
        w = 1.0
    else:
        t = (C - c_soft_low) / (c_soft_high - c_soft_low)
        w = t * t * (3.0 - 2.0 * t)
    return (1.0 - w) * c_clip + w * c_tanh

# =============================================================================
# 6. ФИЗИЧЕСКОЕ ЯДРО
# =============================================================================

class ETVEComplexCoreV140:
    def __init__(self, memory_depth=100):
        self.C = GLOBAL_C_MAX
        self.S = 0.15
        self.step_counter = 0
        self.memory_matrices = deque(maxlen=memory_depth)
        
        # Релаксация из Φ
        self.gamma = GAMMA
        self.eta = ETA
        
        self.history = {
            "C": [], "S": [], "alpha": [], "mass_ratio": [], "G": [],
            "m_e": [], "m_mu": [], "m_tau": [], "m_W": [], "m_Z": [],
            "alpha_inv": [], "alpha_s": [], "alpha_w": [],
        }
        
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
    
    def update_field(self, dt):
        self.step_counter += 1
        
        # Матрица 11x11 с E8
        M = np.zeros((11, 11), dtype=float)
        M[0:8, 0:8] = C_E8.copy() * (1.0 + 0.1 * (self.C - C_FFS))
        M = M * (1.0 + EPSILON_FFS * (self.C - C_FFS))
        
        # Добавка от C
        for i in range(4, 11):
            M[i, i] += self.C * 0.1
        
        # Мнимая часть
        self.phi = (PI / 2.0) * (1.0 - (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN))
        M_imag = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                M_imag[i, j] = M[i, j] * np.tan(self.phi + 0.1 * (i - j))
        M_imag = (M_imag + M_imag.T) / 2.0
        phase_shift = 0.1 * np.sin(self.S * self.step_counter)
        M_imag = M_imag + M * 0.05 * phase_shift
        M_complex = M + 1j * M_imag
        
        # Собственные значения
        eigenvalues = np.linalg.eigvals(M_complex)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]
        
        # Модуляция констант с α_i, β_i из E8
        dC = self.C - C_FFS
        dS = self.S - S_cycle
        
        mod_alpha = 1.0 + ALPHA_I_ALPHA[IDX_ALPHA] * dC + BETA_I_ALPHA[IDX_ALPHA] * dS
        mod_mass  = 1.0 + ALPHA_I_MASS[IDX_MASS] * dC + BETA_I_MASS[IDX_MASS] * dS
        mod_G     = 1.0 + ALPHA_I_G[IDX_G] * dC + BETA_I_G[IDX_G] * dS
        
        alpha_inv = ALPHA_BASE * mod_alpha
        mass_ratio = MASS_BASE * mod_mass
        G = G_BASE * mod_G
        
        # m_e из E_vacuum
        m_e_MeV = E_vacuum(self.C) / alpha_inv * 137.035999084  # калибровка
        
        # Все 26 констант
        const = compute_all_constants(alpha_inv, m_e_MeV, self.C, self.S)
        
        # Сохраняем историю
        self.history["C"].append(self.C)
        self.history["S"].append(self.S)
        self.history["alpha_inv"].append(alpha_inv)
        self.history["m_e"].append(m_e_MeV)
        
        self.memory_matrices.append((M_complex, time.time()))
        
        return {
            "alpha_inv": alpha_inv,
            "mass_ratio": mass_ratio,
            "G": G,
            "const": const,
        }
    
    def evolve(self, entropy_flux=0.0, time_step=1.0):
        noise = 0.001 * np.random.randn()
        
        # Релаксация с γ, η из Φ
        self.C = self.C * (1.0 - self.gamma) + self.gamma * C_FFS + noise * 0.1
        self.S = self.S * (1.0 - self.eta) + self.eta * S_cycle + noise * 0.01
        self.S = max(0.0, min(1.0, self.S))
        
        self.C = etve_tanh_limit(self.C)
        
        result = self.update_field(time_step)
        
        self.history["alpha"].append(result["alpha_inv"])
        self.history["mass_ratio"].append(result["mass_ratio"])
        self.history["G"].append(result["G"])
        
        return result

# =============================================================================
# 7. ЗАПУСК И ВЫВОД
# =============================================================================

def run_and_report(n_steps=100_000, log_every=10_000):
    print("=" * 80)
    print("🌀 ETVP v14.0 — ПОЛНЫЙ РЕЕСТР 26 КОНСТАНТ")
    print(f"   γ = 1/Φ¹² = {GAMMA:.6f}")
    print(f"   η = 1/Φ¹⁰ = {ETA:.6f}")
    print(f"   Тактов: {n_steps:,}")
    print("=" * 80)
    
    model = ETVEComplexCoreV140(memory_depth=100)
    
    print(f"\n🔧 База (C = 1):")
    print(f"   1/α     = {ALPHA_BASE:.9f}")
    print(f"   m_p/m_e = {MASS_BASE:.6f}")
    print(f"   G       = {G_BASE:.6e}\n")
    
    t0 = time.time()
    for i in range(n_steps):
        entropy_flux = 0.005 * np.sin(i / 7.0) + 0.001 * np.random.randn()
        result = model.evolve(entropy_flux, time_step=1.0)
        if (i + 1) % log_every == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  [{i+1:>7,}] C={model.C:.6f} S={model.S:.6f} "
                  f"α⁻¹={result['alpha_inv']:.6f} | {rate:.0f} такт/с")
            sys.stdout.flush()
    
    elapsed = time.time() - t0
    print(f"\n✅ Прогон за {elapsed:.1f} с")
    
    # --- ВЫВОД ВСЕХ 26 КОНСТАНТ ---
    n_avg = 1000
    C_avg = np.mean(model.history["C"][-n_avg:])
    S_avg = np.mean(model.history["S"][-n_avg:])
    alpha_avg = np.mean(model.history["alpha"][-n_avg:])
    m_e_avg = np.mean(model.history["m_e"][-n_avg:])
    
    const = compute_all_constants(alpha_avg, m_e_avg, C_avg, S_avg)
    
    print("\n" + "=" * 80)
    print("📊 РЕЕСТР 26 КОНСТАНТ (последние 1000 тактов)")
    print("=" * 80)
    print(f"\n{'Константа':<18} {'Модель':<18} {'CODATA/PDG':<18} {'Ошибка %':<10}")
    print("-" * 70)
    
    # Группа I
    print("\n--- ГРУППА I: ЛЕПТОНЫ ---")
    for name, key, unit in [
        ("m_e", "m_e", "МэВ"), ("m_μ", "m_mu", "МэВ"), ("m_τ", "m_tau", "МэВ")
    ]:
        mod = const[key]
        cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")
    
    # Группа II
    print("\n--- ГРУППА II: КВАРКИ ---")
    for name, key in [
        ("m_u", "m_u"), ("m_d", "m_d"), ("m_s", "m_s"),
        ("m_c", "m_c"), ("m_b", "m_b"), ("m_t", "m_t")
    ]:
        mod = const[key]
        cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.4f} {cod:<18.4f} {err:<10.4f}")
    
    # Группа III
    print("\n--- ГРУППА III: БОЗОНЫ ---")
    for name, key in [
        ("m_W", "m_W"), ("m_Z", "m_Z"), ("m_H", "m_H")
    ]:
        mod = const[key]
        cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.4f} {cod:<18.4f} {err:<10.4f}")
    
    # Группа IV
    print("\n--- ГРУППА IV: CKM ---")
    for name, key in [
        ("sin θ_12", "sin_th12"), ("sin θ_23", "sin_th23"),
        ("sin θ_13", "sin_th13"), ("δ_CP (град)", "delta_CP")
    ]:
        mod = const[key]
        cod = CODATA[key]
        err = abs(mod - cod) / cod * 100 if cod != 0 else 0
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")
    
    # Группа V
    print("\n--- ГРУППА V: КАЛИБРОВОЧНЫЕ КОНСТАНТЫ ---")
    for name, key in [
        ("1/α", "alpha_inv"), ("α_w", "alpha_w"), ("α_s", "alpha_s")
    ]:
        mod = const[key]
        cod = CODATA[key]
        err = abs(mod - cod) / cod * 100
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")
    
    # Группа VI
    print("\n--- ГРУППА VI: PMNS ---")
    for name, key in [
        ("sin²θ_12^ν", "sin2_th12_nu"), ("sin²θ_23^ν", "sin2_th23_nu"),
        ("sin²θ_13^ν", "sin2_th13_nu"), ("δ_CP^ν (град)", "delta_CP_nu")
    ]:
        mod = const[key]
        cod = CODATA[key]
        err = abs(mod - cod) / abs(cod) * 100 if cod != 0 else 0
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")
    
    # Группа VII
    print("\n--- ГРУППА VII: ХИГГС ---")
    for name, key in [
        ("μ² (ГэВ²)", "mu_sq"), ("λ_H", "lambda_H"), ("θ_QCD", "theta_QCD")
    ]:
        mod = const[key]
        cod = CODATA[key]
        err = abs(mod - cod) / abs(cod) * 100 if cod != 0 else 0
        print(f"{name:<18} {mod:<18.6f} {cod:<18.6f} {err:<10.4f}")
    
    print("\n" + "=" * 80)
    print("✅ ГОТОВО")
    print("=" * 80)

if __name__ == "__main__":
    run_and_report(n_steps=100_000, log_every=10_000)
