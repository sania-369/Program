#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETVP CORE v3 — Живая динамика с визуализацией
"""

import numpy as np
import math
import random
import time
from collections import deque

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec

# =============================================================================
# КОНСТАНТЫ
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI = np.pi
Z_RES = np.sqrt(3.0)

GLOBAL_C_MIN = 1.0 / (PHI ** 10)
GLOBAL_C_MAX = 1.0 - 1.0 / (PHI ** 20)
GLOBAL_C_TARGET = 1.0 - 1.0 / (PHI ** 12)

C_FFS = 0.87
EPSILON_FFS = 0.01


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
# ЖИВОЙ КЛАСС
# =============================================================================

class ETVPLive:
    def __init__(self):
        self.C_E8 = np.zeros((11, 11), dtype=float)
        self.C_E8[0:8, 0:8] = build_cartan_e8()
        
        self.C = GLOBAL_C_TARGET
        self.S = 0.15
        self.step_counter = 0
        
        self.real_particles = []
        self.virtual_particles = []
        self.memory_matrices = deque(maxlen=100)
        self._build_memory_kernel()
        
        self.history = {'C': [], 'S': [], 'alpha': [], 'mass_ratio': [], 'G': []}
    
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
    
    def _update_particles(self):
        if self.C > 0.15 and len(self.real_particles) == 0:
            self.real_particles.append({"mass": 0.1, "charge": 0.1, "alive": True})
        if self.C < 0.05 and len(self.real_particles) > 0:
            self.real_particles = []
        if self.C > 0.10:
            if random.random() < 0.01 and len(self.virtual_particles) < 10:
                self.virtual_particles.append({"energy": random.uniform(0.1, 1.0), "age": 0, "alive": True})
        for v in self.virtual_particles[:]:
            v["age"] += 1
            if v["age"] > 5 or random.random() < 0.02:
                self.virtual_particles.remove(v)
    
    def step(self, entropy_flux=0.0):
        """Один шаг ЖИВОЙ динамики."""
        self.step_counter += 1
        
        # Обновление состояния
        chaos_op = 1.0 / (1.0 + abs(entropy_flux) * (1.0 / PHI))
        self.C = self.C * chaos_op + (1.0 - chaos_op) * GLOBAL_C_MIN
        self.S = max(0.0, min(1.0, self.S + entropy_flux * 0.01))
        
        self._update_particles()
        
        # Построение матрицы
        M = self.C_E8.copy() * (1.0 + 0.1 * (self.C - GLOBAL_C_TARGET))
        ffs_correction = 1.0 + EPSILON_FFS * (self.C - C_FFS)
        M = M * ffs_correction
        
        eigvals, eigvecs = np.linalg.eigh(M[0:8, 0:8])
        mass_direction = eigvecs[:, np.argmin(eigvals)]
        for i in range(8):
            projection = np.dot(eigvecs[:, i], mass_direction)
            M[i, i] += abs(projection) * (GLOBAL_C_MAX - self.C) / (GLOBAL_C_MAX - GLOBAL_C_MIN)
        
        for i in range(4, 11):
            M[i, i] += self.C * 0.1
        
        # Частицы
        particle_contribution = np.zeros(11)
        for p in self.real_particles:
            if p.get("alive", True):
                particle_contribution[0] += p.get("mass", 0.1) * 10
                particle_contribution[1] += p.get("charge", 0.1)
        M[0, :] += particle_contribution * 0.01
        
        M = self._apply_memory(M)
        
        # Мнимая часть
        phi_angle = (PI / 2.0) * (1.0 - (self.C - GLOBAL_C_MIN) / (GLOBAL_C_MAX - GLOBAL_C_MIN))
        M_imag = np.zeros_like(M)
        for i in range(11):
            for j in range(11):
                M_imag[i, j] = M[i, j] * np.tan(phi_angle + 0.1 * (i - j))
        M_imag = (M_imag + M_imag.T) / 2.0
        phase_shift = 0.1 * np.sin(self.S * self.step_counter)
        M_imag = M_imag + M * 0.05 * phase_shift
        
        M_complex = M + 1j * M_imag
        
        # Спектр
        eigenvalues = np.linalg.eigvals(M_complex)
        eigenvalues = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]
        
        # Константы
        alpha_inv = np.real(eigenvalues[0] / eigenvalues[10]) / PHI**2
        mass_ratio = np.real(eigenvalues[0] / eigenvalues[9]) * PHI * 70.0
        G = np.real(eigenvalues[0] / (eigenvalues[10] * eigenvalues[9] + 1e-12)) / (PHI**20) / 1e7
        
        # Память
        self.memory_matrices.append((M_complex, time.time()))
        
        # История
        self.history['C'].append(self.C)
        self.history['S'].append(self.S)
        self.history['alpha'].append(alpha_inv)
        self.history['mass_ratio'].append(abs(mass_ratio))
        self.history['G'].append(G)
        
        return alpha_inv, abs(mass_ratio), G


# =============================================================================
# ЖИВАЯ ВИЗУАЛИЗАЦИЯ
# =============================================================================

def run_live():
    model = ETVPLive()
    
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor('#0a0a0a')
    gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.4)
    
    ax_C = fig.add_subplot(gs[0, 0])
    ax_S = fig.add_subplot(gs[0, 1])
    ax_alpha = fig.add_subplot(gs[0, 2])
    ax_mass = fig.add_subplot(gs[1, 0])
    ax_G = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_subplot(gs[1, 2])
    
    for ax in [ax_C, ax_S, ax_alpha, ax_mass, ax_G, ax_info]:
        ax.set_facecolor('#111111')
        ax.tick_params(colors='white', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#333333')
    
    def update(frame):
        entropy_flux = 0.04 * np.sin(frame / 7.0) + 0.005 * np.random.randn()
        model.step(entropy_flux)
        
        hist = model.history
        x = np.arange(len(hist['C']))
        
        ax_C.clear()
        ax_C.set_facecolor('#111111')
        ax_C.plot(x, hist['C'], color='cyan', linewidth=1.5)
        ax_C.axhline(GLOBAL_C_TARGET, color='yellow', linestyle='--', linewidth=0.8)
        ax_C.set_title('Когерентность C(t)', color='white', fontsize=10)
        ax_C.tick_params(colors='white', labelsize=8)
        
        ax_S.clear()
        ax_S.set_facecolor('#111111')
        ax_S.plot(x, hist['S'], color='orange', linewidth=1.5)
        ax_S.set_title('Энтропия S(t)', color='white', fontsize=10)
        ax_S.set_ylim(0, 1)
        ax_S.tick_params(colors='white', labelsize=8)
        
        ax_alpha.clear()
        ax_alpha.set_facecolor('#111111')
        ax_alpha.plot(x, hist['alpha'], color='yellow', linewidth=1.5)
        ax_alpha.axhline(137.036, color='red', linestyle='--', linewidth=0.8)
        ax_alpha.set_title('α⁻¹(t)', color='white', fontsize=10)
        ax_alpha.tick_params(colors='white', labelsize=8)
        
        ax_mass.clear()
        ax_mass.set_facecolor('#111111')
        ax_mass.plot(x, hist['mass_ratio'], color='lime', linewidth=1.5)
        ax_mass.axhline(1836.15, color='red', linestyle='--', linewidth=0.8)
        ax_mass.set_title('m_p/m_e(t)', color='white', fontsize=10)
        ax_mass.tick_params(colors='white', labelsize=8)
        
        ax_G.clear()
        ax_G.set_facecolor('#111111')
        ax_G.plot(x, hist['G'], color='magenta', linewidth=1.5)
        ax_G.set_title('G(t)', color='white', fontsize=10)
        ax_G.tick_params(colors='white', labelsize=8)
        
        ax_info.clear()
        ax_info.set_facecolor('#0a0a0a')
        ax_info.axis('off')
        info_text = (
            f"ШАГ: {model.step_counter}\n"
            f"C = {model.C:.6f}\n"
            f"α⁻¹ = {hist['alpha'][-1]:.4f}\n"
            f"m_p/m_e = {hist['mass_ratio'][-1]:.2f}\n"
            f"Частиц: {len(model.real_particles)} реальных, "
            f"{len(model.virtual_particles)} виртуальных"
        )
        ax_info.text(0.1, 0.5, info_text, color='white', fontsize=11,
                     family='monospace', verticalalignment='center')
        
        fig.canvas.draw_idle()
        return []
    
    anim = animation.FuncAnimation(fig, update, frames=300, interval=50, blit=False, repeat=False)
    plt.show()
    
    # Финальный отчёт
    print("═" * 60)
    print("  ФИНАЛЬНЫЙ ОТЧЁТ (после 300 шагов):")
    print("═" * 60)
    print(f"  Средняя α⁻¹ = {np.mean(model.history['alpha']):.4f}")
    print(f"  Средняя m_p/m_e = {np.mean(model.history['mass_ratio']):.2f}")
    print(f"  Средняя G = {np.mean(model.history['G']):.6e}")
    print("═" * 60)


if __name__ == "__main__":
    run_live()
