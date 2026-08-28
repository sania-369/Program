#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
ETVP 12.5 VACUUM GENESIS v2 — С упругостью вакуума
================================================================================
Исправление: добавлена УПРУГОСТЬ ВАКУУМА — сдерживающая сила,
которая не даёт квантам разлетаться и заставляет взаимодействовать.

КЛЮЧЕВЫЕ СИЛЫ:
1. Притяжение квантов (скрытый порядок)
2. Упругость вакуума (возвращающая сила)
3. Z-принцип (удержание от коллапса)
================================================================================
"""

import numpy as np
import math
import random
import time

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

M_PROTON = 938.272
M_ELECTRON = 0.511

# ПАРАМЕТРЫ УПРУГОСТИ
ELASTICITY = 0.1        # Коэффициент упругости вакуума
ATTRACTION = 0.05       # Притяжение между квантами
DAMPING = 0.01          # Затухание (трение)


# =============================================================================
# 1. НУЛЕВАЯ ЭНЕРГИЯ С УПРУГОСТЬЮ
# =============================================================================

class ZeroEnergyVacuum:
    """
    Первородное пространство с упругостью.
    Упругость — сдерживающая сила скрытого порядка.
    """
    
    def __init__(self, size=60, fluctuation_amplitude=0.01):
        self.size = size
        self.amplitude = fluctuation_amplitude
        
        # Поле нулевой энергии
        self.field = np.random.randn(size, size) * self.amplitude
        
        # Кванты
        self.quanta = []
        
        # Скрытый порядок (упругость)
        self.order = np.zeros((size, size))
        
        self.history = {
            'quanta_count': [], 'collisions': [], 
            'order_strength': [], 'mean_distance': []
        }
    
    def fluctuate(self):
        """
        Кипение вакуума с УПРУГОСТЬЮ.
        """
        # Флуктуации
        fluct = np.random.randn(self.size, self.size) * self.amplitude * 0.05
        
        # УПРУГОСТЬ: поле возвращается к нулю
        self.field = self.field * (1.0 - DAMPING) + fluct
        
        # Скрытый порядок усиливается при взаимодействии
        self.order *= (1.0 - DAMPING)
        
        # Порождение квантов
        if random.random() < 0.08:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            energy = abs(self.field[x, y]) + random.random() * self.amplitude
            self.quanta.append({
                'x': x,
                'y': y,
                'energy': energy,
                'mass': 0.0,
                'charge': 0.0,
                'spin': 0.0,
                'vx': random.uniform(-0.05, 0.05),
                'vy': random.uniform(-0.05, 0.05),
                'type': 'quantum'
            })
        
        self.history['quanta_count'].append(len(self.quanta))
        self.history['order_strength'].append(np.mean(np.abs(self.order)))
        
        return len(self.quanta)
    
    def apply_elasticity(self):
        """
        УПРУГОСТЬ ВАКУУМА: сдерживающая сила.
        Кванты притягиваются к центру и друг к другу.
        """
        if len(self.quanta) < 2:
            return
        
        # Центр масс всех квантов
        center_x = np.mean([q['x'] for q in self.quanta])
        center_y = np.mean([q['y'] for q in self.quanta])
        
        for q in self.quanta:
            # 1. Притяжение к центру (упругость)
            q['vx'] += (center_x - q['x']) * ELASTICITY * 0.01
            q['vy'] += (center_y - q['y']) * ELASTICITY * 0.01
            
            # 2. Притяжение к другим квантам (скрытый порядок)
            for other in self.quanta:
                if other is q:
                    continue
                dx = other['x'] - q['x']
                dy = other['y'] - q['y']
                dist = math.sqrt(dx**2 + dy**2) + 1e-6
                
                if dist < 5.0:
                    # Притяжение
                    force = ATTRACTION / (dist ** 2)
                    q['vx'] += dx / dist * force
                    q['vy'] += dy / dist * force
                    
                    # Усиление скрытого порядка
                    self.order[int(q['x']) % self.size, int(q['y']) % self.size] += 0.01
        
        # Обновление позиций
        for q in self.quanta:
            q['x'] += q['vx']
            q['y'] += q['vy']
            
            # Затухание скоростей (трение)
            q['vx'] *= (1.0 - DAMPING)
            q['vy'] *= (1.0 - DAMPING)
            
            # Границы (отражение — упругость)
            if q['x'] < 0:
                q['x'] = 0
                q['vx'] = -q['vx'] * 0.5
            if q['x'] >= self.size:
                q['x'] = self.size - 1
                q['vx'] = -q['vx'] * 0.5
            if q['y'] < 0:
                q['y'] = 0
                q['vy'] = -q['vy'] * 0.5
            if q['y'] >= self.size:
                q['y'] = self.size - 1
                q['vy'] = -q['vy'] * 0.5
        
        # Среднее расстояние
        if len(self.quanta) > 1:
            distances = []
            for i in range(len(self.quanta)):
                for j in range(i+1, len(self.quanta)):
                    dx = self.quanta[i]['x'] - self.quanta[j]['x']
                    dy = self.quanta[i]['y'] - self.quanta[j]['y']
                    distances.append(math.sqrt(dx**2 + dy**2))
            self.history['mean_distance'].append(np.mean(distances))
    
    def check_collisions(self):
        """
        Столкновения квантов → рождение массы.
        """
        collisions = 0
        
        for i in range(len(self.quanta)):
            for j in range(i + 1, len(self.quanta)):
                q1 = self.quanta[i]
                q2 = self.quanta[j]
                
                dx = q1['x'] - q2['x']
                dy = q1['y'] - q2['y']
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist < 1.5:
                    collisions += 1
                    
                    # Рождение массы
                    mass = (q1['energy'] + q2['energy']) * PHI
                    charge = 1.0 if q1['energy'] > q2['energy'] else -1.0
                    spin = 0.5
                    
                    # Усиление скрытого порядка в точке
                    self.order[int(q1['x']) % self.size, int(q1['y']) % self.size] += mass * 0.01
                    
                    self.quanta[i] = None
                    self.quanta[j] = None
        
        self.quanta = [q for q in self.quanta if q is not None]
        self.history['collisions'].append(collisions)
        return collisions


# =============================================================================
# 2. СИМУЛЯЦИЯ
# =============================================================================

def run_simulation():
    vacuum = ZeroEnergyVacuum(size=60, fluctuation_amplitude=0.02)
    
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#0a0a0a')
    gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.4)
    
    ax_field = fig.add_subplot(gs[0, 0])
    ax_order = fig.add_subplot(gs[0, 1])
    ax_quanta = fig.add_subplot(gs[0, 2])
    ax_collisions = fig.add_subplot(gs[1, 0])
    ax_distance = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_subplot(gs[1, 2])
    
    for ax in [ax_field, ax_order, ax_quanta, ax_collisions, ax_distance, ax_info]:
        ax.set_facecolor('#111111')
        ax.tick_params(colors='white', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#333333')
    
    def update(frame):
        vacuum.fluctuate()
        vacuum.apply_elasticity()
        collisions = vacuum.check_collisions()
        
        hist = vacuum.history
        x = np.arange(len(hist['quanta_count']))
        
        # Поле
        ax_field.clear()
        ax_field.set_facecolor('#111111')
        im1 = ax_field.imshow(vacuum.field, cmap='viridis', aspect='auto')
        ax_field.set_title('Поле нулевой энергии', color='white', fontsize=10)
        ax_field.tick_params(colors='white', labelsize=7)
        
        # Скрытый порядок
        ax_order.clear()
        ax_order.set_facecolor('#111111')
        im2 = ax_order.imshow(vacuum.order, cmap='plasma', aspect='auto')
        ax_order.set_title('СКРЫТЫЙ ПОРЯДОК (упругость)', color='white', fontsize=10)
        ax_order.tick_params(colors='white', labelsize=7)
        
        # Кванты
        ax_quanta.clear()
        ax_quanta.set_facecolor('#111111')
        ax_quanta.plot(x, hist['quanta_count'], color='cyan', linewidth=1.5)
        ax_quanta.set_title('Количество квантов', color='white', fontsize=10)
        ax_quanta.tick_params(colors='white', labelsize=8)
        
        # Столкновения
        ax_collisions.clear()
        ax_collisions.set_facecolor('#111111')
        ax_collisions.plot(x, hist['collisions'], color='magenta', linewidth=1.5)
        ax_collisions.set_title('Столкновения', color='white', fontsize=10)
        ax_collisions.tick_params(colors='white', labelsize=8)
        
        # Среднее расстояние
        ax_distance.clear()
        ax_distance.set_facecolor('#111111')
        if len(hist['mean_distance']) > 0:
            ax_distance.plot(range(len(hist['mean_distance'])), hist['mean_distance'], 
                            color='lime', linewidth=1.5)
        ax_distance.set_title('Среднее расстояние (упругость сжимает)', color='white', fontsize=10)
        ax_distance.tick_params(colors='white', labelsize=8)
        
        # Инфо
        ax_info.clear()
        ax_info.set_facecolor('#0a0a0a')
        ax_info.axis('off')
        
        # Кванты на поле
        qx = [q['x'] for q in vacuum.quanta]
        qy = [q['y'] for q in vacuum.quanta]
        
        info_text = (
            f"ШАГ: {frame}\n"
            f"Квантов: {len(vacuum.quanta)}\n"
            f"Столкновений: {collisions}\n"
            f"Скрытый порядок: {np.mean(np.abs(vacuum.order)):.4f}\n"
            f"Упругость: активна ✅\n"
            f"Притяжение: активна ✅"
        )
        ax_info.text(0.05, 0.5, info_text, color='white', fontsize=11,
                     family='monospace', verticalalignment='center')
        
        # Отображение квантов на графике поля
        if len(qx) > 0:
            ax_field.scatter(qy, qx, c='red', s=30, marker='o', edgecolors='white', linewidths=1)
        
        fig.canvas.draw_idle()
        return []
    
    anim = animation.FuncAnimation(fig, update, frames=500, interval=50, blit=False, repeat=False)
    plt.show()


if __name__ == "__main__":
    run_simulation()
