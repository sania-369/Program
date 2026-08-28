#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
ETVP 12.5 LIVE v4 — Живая динамика с упругостью вакуума
================================================================================
Интеграция ETVE_Dynamic_Resonance_Core_v2.0:
- Когерентность дышит в коридоре 0.92–0.985
- Внешний шум = электромагнитный фон планеты
- 5 фаз локализации волн (PRL 2026)
- Реальность = (Прошлое × C) + (Хаос × (1−C))
================================================================================
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
# 0. КОНСТАНТЫ
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI = np.pi
Z_RES = np.sqrt(3.0)

GLOBAL_C_MIN = 1.0 / (PHI ** 10)
GLOBAL_C_MAX = 1.0 - 1.0 / (PHI ** 20)
GLOBAL_C_TARGET = 1.0 - 1.0 / (PHI ** 12)

C_FFS = 0.87
EPSILON_FFS = 0.01


# =============================================================================
# 1. ЯДРО ДИНАМИЧЕСКОГО РЕЗОНАНСА v2.0
# =============================================================================

class ETVEDynamicResonance:
    """
    Ядро живой когерентности.
    Поддерживает поле в диапазоне 0.92–0.985.
    """
    
    def __init__(self, target=0.965, chaos_buffer=0.015):
        self.target = target
        self.buffer = chaos_buffer
        self.current_coherence = target
        self.iteration = 0
    
    def get_phase_signature(self, coh):
        """5 фаз локализации (PRL 2026)."""
        if coh >= 0.97:
            return "Extended Phase (Порядок)"
        elif coh > 0.95:
            return "Extended-Localized Coexistence"
        elif coh == 0.95:
            return "Critical Fractal Phase"
        elif coh >= 0.93:
            return "Localized-Critical Coexistence"
        else:
            return "Localized Phase (Хаос)"
    
    def get_coherence(self, external_entropy=0):
        """Когерентность с учётом внешнего шума."""
        self.iteration += 1
        
        # Дыхание поля
        breathing = np.sin(self.iteration / 20.0) * self.buffer
        
        # Адаптация к шуму
        adaptation = external_entropy * 0.02
        
        new_coh = self.target + breathing + adaptation
        self.current_coherence = np.clip(new_coh, 0.92, 0.985)
        
        return self.current_coherence
    
    def apply_field(self, signal, noise):
        """Реальность = (Прошлое × C) + (Хаос × (1−C))"""
        coh = self.get_coherence(abs(noise))
        phase = self.get_phase_signature(coh)
        output = (signal * coh) + (noise * (1 - coh))
        return output, phase


# =============================================================================
# 2. ЖИВАЯ МОДЕЛЬ E₈
# =============================================================================

class ETVPLive:
    def __init__(self):
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
        
        # Ядро резонанса
        self.resonance = ETVEDynamicResonance(target=0.965, chaos_buffer=0.015)
        
        self.C = self.resonance.current_coherence
        self.S = 0.15
        self.step_counter = 0
        
        self.real_particles = []
        self.virtual_particles = []
        self.memory_matrices = deque(maxlen=100)
        self._build_memory_kernel()
        
        self.history = {
            'C': [], 'S': [], 'alpha': [], 'mass_ratio': [], 'G': [],
            'phase': [], 'noise': []
        }
    
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
        if self.C > 0.93 and len(self.real_particles) == 0:
            self.real_particles.append({"mass": 0.1, "charge": 0.1, "alive": True})
        if self.C < 0.92 and len(self.real_particles) > 0:
            self.real_particles = []
        if random.random() < 0.01 and len(self.virtual_particles) < 10:
            self.virtual_particles.append({"energy": random.uniform(0.1, 1.0), "age": 0, "alive": True})
        for v in self.virtual_particles[:]:
            v["age"] += 1
            if v["age"] > 5 or random.random() < 0.02:
                self.virtual_particles.remove(v)
    
    def _external_noise(self):
        """Внешний шум: ЭМ-фон планеты + технологии."""
        # Шумановский резонанс (7.83 Гц)
        schumann = 0.02 * math.sin(self.step_counter * 7.83 * 0.01)
        
        # Техногенный фон (50/60 Гц)
        power_grid = 0.01 * math.sin(self.step_counter * 50 * 0.001)
        
        # Случайный компонент
        random_noise = 0.005 * random.random()
        
        return abs(schumann + power_grid + random_noise)
    
    def step(self):
        """Один шаг живой динамики."""
        self.step_counter += 1
        
        # Внешний шум
        noise = self._external_noise()
        
        # Когерентность через ядро резонанса
        self.C = self.resonance.get_coherence(noise)
        phase = self.resonance.get_phase_signature(self.C)
        
        # Энтропия = 1 − когерентность
        self.S = 1.0 - self.C
        self.S = np.clip(self.S, 0.001, 0.5)
        
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
        
        particle_contribution = np.zeros(11)
        for p in self.real_particles:
            if p.get("alive", True):
                particle_contribution[0] += p.get("mass", 0.1) * 10
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
        
        self.memory_matrices.append((M_complex, time.time()))
        
        # История
        self.history['C'].append(self.C)
        self.history['S'].append(self.S)
        self.history['alpha'].append(alpha_inv)
        self.history['mass_ratio'].append(abs(mass_ratio))
        self.history['G'].append(G)
        self.history['phase'].append(phase)
        self.history['noise'].append(noise)
        
        return alpha_inv, abs(mass_ratio), G, phase


# =============================================================================
# 3. ЖИВАЯ ВИЗУАЛИЗАЦИЯ
# =============================================================================

def run_live():
    model = ETVPLive()
    
    fig = plt.figure(figsize=(18, 12))
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
        alpha_inv, mass_ratio, G, phase = model.step()
        
        hist = model.history
        x = np.arange(len(hist['C']))
        
        ax_C.clear()
        ax_C.set_facecolor('#111111')
        ax_C.plot(x, hist['C'], color='cyan', linewidth=1.5)
        ax_C.axhline(0.965, color='yellow', linestyle='--', linewidth=0.8)
        ax_C.set_ylim(0.9, 1.0)
        ax_C.set_title('Когерентность C(t)', color='white', fontsize=10)
        ax_C.tick_params(colors='white', labelsize=8)
        
        ax_S.clear()
        ax_S.set_facecolor('#111111')
        ax_S.plot(x, hist['S'], color='orange', linewidth=1.5)
        ax_S.set_title('Энтропия S(t)', color='white', fontsize=10)
        ax_S.set_ylim(0, 0.2)
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
            f"Фаза: {phase}\n"
            f"Шум: {hist['noise'][-1]:.4f}\n"
            f"α⁻¹ = {hist['alpha'][-1]:.4f}\n"
            f"m_p/m_e = {hist['mass_ratio'][-1]:.2f}\n"
            f"Частиц: {len(model.real_particles)} реальных"
        )
        ax_info.text(0.05, 0.5, info_text, color='white', fontsize=10,
                     family='monospace', verticalalignment='center')
        
        fig.canvas.draw_idle()
        return []
    
    anim = animation.FuncAnimation(fig, update, frames=300, interval=50, blit=False, repeat=False)
    plt.show()
    
    print("═" * 60)
    print("  ФИНАЛЬНЫЙ ОТЧЁТ:")
    print("═" * 60)
    print(f"  Средняя C = {np.mean(model.history['C']):.6f}")
    print(f"  Средняя α⁻¹ = {np.mean(model.history['alpha']):.4f}")
    print(f"  Средняя m_p/m_e = {np.mean(model.history['mass_ratio']):.2f}")
    print("═" * 60)


if __name__ == "__main__":
    run_live()
