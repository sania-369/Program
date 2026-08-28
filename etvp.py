#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
ETVP 12.5 VACUUM GENESIS v3 — Множественные локальные области
================================================================================
Абсолютный хаос + абсолютный потенциал = высокое давление вакуума.
Кванты рождаются и СРАЗУ взаимодействуют в разных локальных областях.

МОДЕЛЬ:
- 6 локальных областей (по 36 квантов в каждой)
- Высокая плотность вакуума
- Мгновенное взаимодействие
- Стремление к когерентности
================================================================================
"""

import numpy as np
import math
import random

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

# Параметры вакуума
VACUUM_PRESSURE = 0.9       # Высокое давление
VACUUM_POTENTIAL = 1.0      # Абсолютный потенциал
COHERENCE_DRIVE = 0.8       # Стремление к когерентности

# Количество
NUM_REGIONS = 6             # Локальных областей
QUANTA_PER_REGION = 36      # Квантов в каждой области

# Упругость
ELASTICITY = 0.15
ATTRACTION = 0.08
DAMPING = 0.005


# =============================================================================
# 1. ЛОКАЛЬНАЯ ОБЛАСТЬ
# =============================================================================

class LocalRegion:
    """
    Локальная область вакуума с квантами.
    """
    
    def __init__(self, region_id, size=20):
        self.id = region_id
        self.size = size
        
        # Высокое давление → сразу много квантов
        self.quanta = []
        
        # Рождаем 36 квантов сразу
        for _ in range(QUANTA_PER_REGION):
            self.quanta.append({
                'x': random.uniform(0, size),
                'y': random.uniform(0, size),
                'energy': random.uniform(0.1, 1.0) * VACUUM_POTENTIAL,
                'vx': random.uniform(-0.03, 0.03),
                'vy': random.uniform(-0.03, 0.03),
                'interactions': 0,
                'coherent': False
            })
        
        # Поле порядка в области
        self.order_field = np.zeros((size, size))
        
        # Метрики
        self.interactions_count = 0
        self.coherence_level = 0.0
        self.mean_distance = 0.0
    
    def apply_high_pressure(self):
        """
        Высокое давление вакуума — кванты СРАЗУ взаимодействуют.
        """
        # Вычисляем центр масс
        cx = np.mean([q['x'] for q in self.quanta])
        cy = np.mean([q['y'] for q in self.quanta])
        
        # Давление сжимает к центру
        for q in self.quanta:
            q['vx'] += (cx - q['x']) * VACUUM_PRESSURE * 0.01
            q['vy'] += (cy - q['y']) * VACUUM_PRESSURE * 0.01
        
        # Взаимодействие квантов
        self.interactions_count = 0
        
        for i in range(len(self.quanta)):
            for j in range(i+1, len(self.quanta)):
                q1 = self.quanta[i]
                q2 = self.quanta[j]
                
                dx = q2['x'] - q1['x']
                dy = q2['y'] - q1['y']
                dist = math.sqrt(dx**2 + dy**2) + 1e-6
                
                if dist < 3.0:
                    # ВЗАИМОДЕЙСТВИЕ (притяжение)
                    force = ATTRACTION / (dist ** 2) * VACUUM_PRESSURE
                    q1['vx'] += dx / dist * force
                    q1['vy'] += dy / dist * force
                    q2['vx'] -= dx / dist * force
                    q2['vy'] -= dy / dist * force
                    
                    q1['interactions'] += 1
                    q2['interactions'] += 1
                    
                    self.interactions_count += 1
                    
                    # Кванты становятся когерентными при взаимодействии
                    if q1['interactions'] > 3:
                        q1['coherent'] = True
                    if q2['interactions'] > 3:
                        q2['coherent'] = True
                    
                    # Усиление порядка
                    ox = int(q1['x']) % self.size
                    oy = int(q1['y']) % self.size
                    self.order_field[ox, oy] += 0.05
        
        # Обновление позиций
        distances = []
        for q in self.quanta:
            q['x'] += q['vx']
            q['y'] += q['vy']
            q['vx'] *= (1.0 - DAMPING)
            q['vy'] *= (1.0 - DAMPING)
            
            # Границы
            if q['x'] < 0: q['x'] = 0; q['vx'] *= -0.5
            if q['x'] >= self.size: q['x'] = self.size-1; q['vx'] *= -0.5
            if q['y'] < 0: q['y'] = 0; q['vy'] *= -0.5
            if q['y'] >= self.size: q['y'] = self.size-1; q['vy'] *= -0.5
            
            distances.append(math.sqrt((q['x']-cx)**2 + (q['y']-cy)**2))
        
        self.mean_distance = np.mean(distances) if distances else 0
        
        # Когерентность области
        coherent_count = sum(1 for q in self.quanta if q['coherent'])
        self.coherence_level = coherent_count / len(self.quanta)
        
        return self.interactions_count


# =============================================================================
# 2. АБСОЛЮТНЫЙ ВАКУУМ
# =============================================================================

class AbsoluteVacuum:
    """
    Абсолютный хаос с абсолютным потенциалом.
    Содержит множество локальных областей.
    """
    
    def __init__(self):
        self.regions = [LocalRegion(i) for i in range(NUM_REGIONS)]
        self.global_coherence = 0.0
        
        self.history = {
            'global_coherence': [], 'total_interactions': [],
            'mean_distance': [], 'coherent_quanta': []
        }
    
    def step(self):
        """Один шаг эволюции всех областей."""
        total_interactions = 0
        total_coherent = 0
        total_quanta = 0
        
        for region in self.regions:
            interactions = region.apply_high_pressure()
            total_interactions += interactions
            total_coherent += sum(1 for q in region.quanta if q['coherent'])
            total_quanta += len(region.quanta)
        
        # Глобальная когерентность
        self.global_coherence = total_coherent / total_quanta if total_quanta > 0 else 0
        
        # История
        self.history['global_coherence'].append(self.global_coherence)
        self.history['total_interactions'].append(total_interactions)
        self.history['mean_distance'].append(
            np.mean([r.mean_distance for r in self.regions])
        )
        self.history['coherent_quanta'].append(total_coherent)
        
        return {
            'coherence': self.global_coherence,
            'interactions': total_interactions,
            'coherent': total_coherent
        }


# =============================================================================
# 3. ВИЗУАЛИЗАЦИЯ
# =============================================================================

def run():
    vacuum = AbsoluteVacuum()
    
    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor('#0a0a0a')
    gs = GridSpec(3, 4, figure=fig, hspace=0.5, wspace=0.4)
    
    # 6 графиков локальных областей
    ax_regions = []
    for i in range(NUM_REGIONS):
        row = i // 2
        col = i % 2
        ax = fig.add_subplot(gs[row, col])
        ax.set_facecolor('#111111')
        ax.set_title(f'Область {i+1}', color='white', fontsize=9)
        ax.tick_params(colors='white', labelsize=6)
        for spine in ax.spines.values():
            spine.set_color('#333333')
        ax_regions.append(ax)
    
    # Глобальные графики
    ax_coh = fig.add_subplot(gs[2, 0])
    ax_int = fig.add_subplot(gs[2, 1])
    ax_dist = fig.add_subplot(gs[2, 2])
    ax_info = fig.add_subplot(gs[2, 3])
    
    for ax in [ax_coh, ax_int, ax_dist, ax_info]:
        ax.set_facecolor('#111111')
        ax.tick_params(colors='white', labelsize=7)
        for spine in ax.spines.values():
            spine.set_color('#333333')
    
    def update(frame):
        result = vacuum.step()
        
        hist = vacuum.history
        x = np.arange(len(hist['global_coherence']))
        
        # Локальные области
        for i, region in enumerate(vacuum.regions):
            ax = ax_regions[i]
            ax.clear()
            ax.set_facecolor('#111111')
            
            # Кванты
            qx = [q['x'] for q in region.quanta]
            qy = [q['y'] for q in region.quanta]
            coherent = [q['coherent'] for q in region.quanta]
            
            # Цвет: когерентные — cyan, некогерентные — red
            colors = ['cyan' if c else 'red' for c in coherent]
            
            ax.scatter(qx, qy, c=colors, s=20, alpha=0.7, edgecolors='white', linewidths=0.5)
            ax.set_xlim(0, region.size)
            ax.set_ylim(0, region.size)
            ax.set_title(f'Область {i+1} (C={region.coherence_level:.2f})', 
                        color='white', fontsize=9)
            ax.tick_params(colors='white', labelsize=6)
        
        # Глобальная когерентность
        ax_coh.clear()
        ax_coh.set_facecolor('#111111')
        ax_coh.plot(x, hist['global_coherence'], color='cyan', linewidth=1.5)
        ax_coh.set_ylim(0, 1)
        ax_coh.set_title('Глобальная когерентность', color='white', fontsize=9)
        ax_coh.tick_params(colors='white', labelsize=7)
        
        # Взаимодействия
        ax_int.clear()
        ax_int.set_facecolor('#111111')
        ax_int.plot(x, hist['total_interactions'], color='magenta', linewidth=1.5)
        ax_int.set_title('Взаимодействия', color='white', fontsize=9)
        ax_int.tick_params(colors='white', labelsize=7)
        
        # Расстояние
        ax_dist.clear()
        ax_dist.set_facecolor('#111111')
        ax_dist.plot(x, hist['mean_distance'], color='lime', linewidth=1.5)
        ax_dist.set_title('Среднее расстояние', color='white', fontsize=9)
        ax_dist.tick_params(colors='white', labelsize=7)
        
        # Инфо
        ax_info.clear()
        ax_info.set_facecolor('#0a0a0a')
        ax_info.axis('off')
        info_text = (
            f"ШАГ: {frame}\n"
            f"Областей: {NUM_REGIONS}\n"
            f"Квантов/область: {QUANTA_PER_REGION}\n"
            f"Всего: {NUM_REGIONS * QUANTA_PER_REGION}\n"
            f"Когерентных: {result['coherent']}\n"
            f"Взаимодействий: {result['interactions']}\n"
            f"C_global = {result['coherence']:.3f}"
        )
        ax_info.text(0.05, 0.5, info_text, color='white', fontsize=10,
                     family='monospace', verticalalignment='center')
        
        fig.canvas.draw_idle()
        return []
    
    anim = animation.FuncAnimation(fig, update, frames=500, interval=50, blit=False, repeat=False)
    plt.show()


if __name__ == "__main__":
    run()
