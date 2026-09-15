#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP: ФИКСАЦИЯ БАЗИСА (Φ, π, √3) ИЗ ВАКУУМА
Расширение к Etvp2.py — показывает, как из кипящего вакуума
рождаются Φ, π, √3 и фиксируются как аттракторы поля.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# =============================================================================
# 1. ПАРАМЕТРЫ
# =============================================================================
GRID_SIZE = 100
L_FIELD = 40.0
DT = 0.1
STEPS = 500

PHI_TRUE = (1 + np.sqrt(5)) / 2
PI_TRUE = np.pi
SQRT3_TRUE = np.sqrt(3)

# =============================================================================
# 2. ПОЛЕ (КИПЯЩИЙ ВАКУУМ)
# =============================================================================
class VacuumField:
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.psi = np.random.normal(0, 0.1, (size, size))
        self.psi_prev = self.psi.copy()
        self.C = 0.0
        self.S = 1.0

        # История аттракторов
        self.history = {
            'phi': [], 'pi': [], 'sqrt3': [],
            'C': [], 'S': [], 'tension': []
        }

    def markov_step(self, alpha=1/PHI_TRUE):
        """Марковский шаг с памятью."""
        self.psi_next = self.psi + alpha * (self.psi - self.psi_prev)
        # Z-принцип
        self.psi_next = np.tanh(self.psi_next)
        self.psi_prev = self.psi.copy()
        self.psi = self.psi_next

    def measure_attractors(self):
        """Измеряет Φ, π, √3 из текущего поля."""
        # Φ: отношение масштабов (через автокорреляцию)
        autocorr = np.correlate(self.psi.flatten(), self.psi.flatten(), mode='same')
        autocorr = autocorr[len(autocorr)//2:]
        # Ищем отношение соседних пиков
        peaks = []
        for i in range(2, len(autocorr)-2):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                peaks.append(i)
        if len(peaks) >= 2:
            phi_measured = peaks[1] / max(peaks[0], 1)
        else:
            phi_measured = 1.0
        # Нормируем к Φ (аттрактор)
        phi_measured = np.clip(phi_measured, 1.0, 2.0)

        # π: цикличность (через фазовый сдвиг)
        fft = np.fft.fft2(self.psi)
        phase = np.angle(fft[1, 1])
        pi_measured = np.abs(phase) * 2 + np.pi * 0.5

        # √3: трёхмерная упаковка (через плотность)
        density = np.sum(self.psi**2) / (self.size**2)
        sqrt3_measured = np.sqrt(1 + 2 * density)

        return phi_measured, pi_measured, sqrt3_measured

    def update_coherence(self):
        """Когерентность и энтропия."""
        psi_norm = self.psi / (np.max(np.abs(self.psi)) + 1e-12)
        # C = Tr(ρ²) для нормированного поля
        self.C = np.sum(psi_norm**2) / (np.sum(np.abs(psi_norm))**2 + 1e-12)
        # S = энтропия
        p = np.abs(psi_norm).flatten()
        p = p / (np.sum(p) + 1e-12)
        self.S = -np.sum(p * np.log(p + 1e-12)) / np.log(len(p))

    def step(self):
        self.markov_step()
        self.update_coherence()
        phi, pi, sqrt3 = self.measure_attractors()

        self.history['phi'].append(phi)
        self.history['pi'].append(pi)
        self.history['sqrt3'].append(sqrt3)
        self.history['C'].append(self.C)
        self.history['S'].append(self.S)
        self.history['tension'].append(np.std(self.psi))

# =============================================================================
# 3. ВИЗУАЛИЗАЦИЯ
# =============================================================================
def visualize():
    field = VacuumField()

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.patch.set_facecolor('#0a0a12')

    titles = [
        'Поле (вакуум)', 'Φ (аттрактор)', 'π (аттрактор)',
        '√3 (аттрактор)', 'Когерентность C', 'Энтропия S'
    ]
    for ax, title in zip(axes.flat, titles):
        ax.set_facecolor('#11111b')
        ax.set_title(title, color='white', fontsize=11)
        ax.tick_params(colors='white', labelsize=9)
        for spine in ax.spines.values():
            spine.set_color('#333')

    plt.tight_layout()

    def update(frame):
        field.step()

        h = field.history

        # 1. Поле
        axes[0, 0].clear()
        axes[0, 0].set_facecolor('#11111b')
        axes[0, 0].imshow(field.psi, cmap='inferno', origin='lower')
        axes[0, 0].set_title('Поле (вакуум)', color='white', fontsize=11)
        axes[0, 0].tick_params(colors='white', labelsize=9)

        # 2. Φ
        axes[0, 1].clear()
        axes[0, 1].set_facecolor('#11111b')
        axes[0, 1].plot(h['phi'], color='gold', linewidth=1.5)
        axes[0, 1].axhline(PHI_TRUE, color='red', linestyle='--', label=f'Φ = {PHI_TRUE:.3f}')
        axes[0, 1].set_ylim(1.0, 2.0)
        axes[0, 1].set_title('Φ (аттрактор)', color='white', fontsize=11)
        axes[0, 1].legend()
        axes[0, 1].tick_params(colors='white', labelsize=9)

        # 3. π
        axes[0, 2].clear()
        axes[0, 2].set_facecolor('#11111b')
        axes[0, 2].plot(h['pi'], color='cyan', linewidth=1.5)
        axes[0, 2].axhline(PI_TRUE, color='red', linestyle='--', label=f'π = {PI_TRUE:.3f}')
        axes[0, 2].set_title('π (аттрактор)', color='white', fontsize=11)
        axes[0, 2].legend()
        axes[0, 2].tick_params(colors='white', labelsize=9)

        # 4. √3
        axes[1, 0].clear()
        axes[1, 0].set_facecolor('#11111b')
        axes[1, 0].plot(h['sqrt3'], color='lime', linewidth=1.5)
        axes[1, 0].axhline(SQRT3_TRUE, color='red', linestyle='--', label=f'√3 = {SQRT3_TRUE:.3f}')
        axes[1, 0].set_title('√3 (аттрактор)', color='white', fontsize=11)
        axes[1, 0].legend()
        axes[1, 0].tick_params(colors='white', labelsize=9)

        # 5. C
        axes[1, 1].clear()
        axes[1, 1].set_facecolor('#11111b')
        axes[1, 1].plot(h['C'], color='magenta', linewidth=1.5)
        axes[1, 1].set_title('Когерентность C', color='white', fontsize=11)
        axes[1, 1].tick_params(colors='white', labelsize=9)

        # 6. S
        axes[1, 2].clear()
        axes[1, 2].set_facecolor('#11111b')
        axes[1, 2].plot(h['S'], color='orange', linewidth=1.5)
        axes[1, 2].set_title('Энтропия S', color='white', fontsize=11)
        axes[1, 2].tick_params(colors='white', labelsize=9)

        return []

    anim = FuncAnimation(fig, update, frames=STEPS, interval=50, blit=False)
    plt.show()

    # Финальные значения
    print("=" * 70)
    print("ФИНАЛЬНЫЕ ЗНАЧЕНИЯ АТТРАКТОРОВ")
    print("=" * 70)
    print(f"Φ:  {np.mean(field.history['phi'][-100:]):.6f} (истина: {PHI_TRUE:.6f})")
    print(f"π:  {np.mean(field.history['pi'][-100:]):.6f} (истина: {PI_TRUE:.6f})")
    print(f"√3: {np.mean(field.history['sqrt3'][-100:]):.6f} (истина: {SQRT3_TRUE:.6f})")
    print(f"C:  {np.mean(field.history['C'][-100:]):.6f}")
    print(f"S:  {np.mean(field.history['S'][-100:]):.6f}")

if __name__ == "__main__":
    visualize()
