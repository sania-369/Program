#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
ETVP 12.5 VACUUM GENESIS v4 — Одна область, рождение протия
================================================================================
ОДНА локальная область вакуума.
Высокая плотность + абсолютный потенциал.
36 квантов нулевой энергии СРАЗУ взаимодействуют.

ПРОЦЕСС:
1. Кванты нулевой энергии (m=0, q=0, s=0)
2. Столкновение → точка массы (m > 0)
3. Трение → заряд + магнитный момент
4. Заряд + магнит → спин
5. Протон (m=938, q=+1, s=1/2)
6. Протон + вакуум → электрон (q=-1, s=-1/2)
7. Баланс → ПРОТИЙ
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

# Вакуум
VACUUM_DENSITY = 0.95       # Высокая плотность
VACUUM_POTENTIAL = 1.0      # Абсолютный потенциал

# 36 квантов
NUM_QUANTA = 36

# Силы
ATTRACTION = 0.12           # Притяжение (гравитация массы)
COULOMB = 0.10              # Электромагнитное взаимодействие
DAMPING = 0.005

# Пороги
MASS_THRESHOLD = 0.5        # Порог рождения массы
PROTON_ENERGY = 938.272     # МэВ


# =============================================================================
# 1. КВАНТ НУЛЕВОЙ ЭНЕРГИИ
# =============================================================================

class Quantum:
    """Квант нулевой энергии."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = random.uniform(0.1, 1.0) * VACUUM_POTENTIAL
        
        # Изначально: масса=0, заряд=0, спин=0
        self.mass = 0.0
        self.charge = 0.0
        self.spin = 0.0
        self.magnetic_moment = 0.0
        
        self.vx = random.uniform(-0.02, 0.02)
        self.vy = random.uniform(-0.02, 0.02)
        
        self.type = 'zero_energy'
        self.interactions = 0
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


# =============================================================================
# 2. РОЖДЕНИЕ МАТЕРИИ
# =============================================================================

def create_mass(q1, q2):
    """
    Столкновение двух квантов → рождение массы.
    """
    # Энергия столкновения
    total_energy = q1.energy + q2.energy
    
    # Масса рождается
    mass = total_energy * PHI
    
    # Заряд из трения (асимметрия энергий)
    if q1.energy > q2.energy:
        charge = 1.0
    else:
        charge = -1.0
    
    # Магнитный момент (из заряда)
    magnetic_moment = charge * 0.5
    
    # Спин (из баланса)
    spin = 0.5 if charge > 0 else -0.5
    
    return {
        'x': (q1.x + q2.x) / 2,
        'y': (q1.y + q2.y) / 2,
        'mass': mass,
        'charge': charge,
        'spin': spin,
        'magnetic_moment': magnetic_moment,
        'energy': total_energy,
        'type': 'particle',
        'interactions': 0
    }


def create_proton(particle):
    """Превращение частицы в протон при достаточной энергии."""
    if particle['mass'] >= PROTON_ENERGY * 0.01:
        return {
            'x': particle['x'],
            'y': particle['y'],
            'mass': PROTON_ENERGY,
            'charge': 1.0,
            'spin': 0.5,
            'magnetic_moment': 0.5,
            'energy': PROTON_ENERGY,
            'type': 'proton',
            'interactions': 0
        }
    return particle


def create_electron(proton):
    """Протон + нулевая энергия → электрон (противоположный спин)."""
    return {
        'x': proton['x'] + random.uniform(-1, 1),
        'y': proton['y'] + random.uniform(-1, 1),
        'mass': 0.511,
        'charge': -1.0,
        'spin': -0.5,
        'magnetic_moment': -0.5,
        'energy': 0.511,
        'type': 'electron',
        'interactions': 0
    }


# =============================================================================
# 3. ОДНА ЛОКАЛЬНАЯ ОБЛАСТЬ
# =============================================================================

class VacuumRegion:
    """
    Одна локальная область с высокой плотностью.
    """
    
    def __init__(self, size=30):
        self.size = size
        
        # 36 квантов нулевой энергии
        self.quanta = []
        for _ in range(NUM_QUANTA):
            self.quanta.append(Quantum(
                random.uniform(5, size - 5),
                random.uniform(5, size - 5)
            ))
        
        # Частицы (рождённые из столкновений)
        self.particles = []
        self.proton = None
        self.electron = None
        self.protium = None
        
        # История
        self.history = {
            'quanta': [], 'particles': [], 'proton': [],
            'electron': [], 'protium': [], 'interactions': []
        }
    
    def step(self):
        """Один шаг эволюции области."""
        interactions = 0
        
        # 1. ДВИЖЕНИЕ И ВЗАИМОДЕЙСТВИЕ КВАНТОВ
        for i in range(len(self.quanta)):
            for j in range(i+1, len(self.quanta)):
                q1 = self.quanta[i]
                q2 = self.quanta[j]
                
                dist = q1.distance_to(q2)
                
                if dist < 1.0:
                    # СТОЛКНОВЕНИЕ → рождение массы
                    particle = create_mass(q1, q2)
                    self.particles.append(particle)
                    interactions += 1
                    
                    self.quanta[i] = None
                    self.quanta[j] = None
                    
                elif dist < 3.0:
                    # ПРИТЯЖЕНИЕ (высокая плотность)
                    force = ATTRACTION / (dist ** 2) * VACUUM_DENSITY
                    dx = (q2.x - q1.x) / dist
                    dy = (q2.y - q1.y) / dist
                    
                    q1.vx += dx * force
                    q1.vy += dy * force
                    q2.vx -= dx * force
                    q2.vy -= dy * force
                    
                    q1.interactions += 1
                    q2.interactions += 1
                    interactions += 1
        
        # Очистка
        self.quanta = [q for q in self.quanta if q is not None]
        
        # 2. ДВИЖЕНИЕ ЧАСТИЦ
        for p in self.particles:
            # Притяжение частиц (гравитация + кулон)
            for other in self.particles:
                if other is p:
                    continue
                dist = math.sqrt((p['x']-other['x'])**2 + (p['y']-other['y'])**2) + 1e-6
                
                if dist < 5.0:
                    # Кулоновское взаимодействие
                    if p['charge'] * other['charge'] < 0:
                        force = COULOMB / (dist ** 2)  # Притяжение
                    else:
                        force = -COULOMB / (dist ** 2)  # Отталкивание
                    
                    p['x'] += (other['x'] - p['x']) / dist * force
                    p['y'] += (other['y'] - p['y']) / dist * force
        
        # 3. РОЖДЕНИЕ ПРОТОНА
        if self.proton is None:
            for p in self.particles:
                if p['type'] == 'particle' and p['charge'] > 0 and p['mass'] > MASS_THRESHOLD:
                    self.proton = create_proton(p)
                    self.particles.remove(p)
                    break
        
        # 4. РОЖДЕНИЕ ЭЛЕКТРОНА
        if self.proton is not None and self.electron is None:
            self.electron = create_electron(self.proton)
        
        # 5. ОБРАЗОВАНИЕ ПРОТИЯ
        if self.proton is not None and self.electron is not None and self.protium is None:
            # Проверяем баланс зарядов
            if self.proton['charge'] + self.electron['charge'] == 0:
                self.protium = {
                    'x': (self.proton['x'] + self.electron['x']) / 2,
                    'y': (self.proton['y'] + self.electron['y']) / 2,
                    'mass': self.proton['mass'] + self.electron['mass'],
                    'charge': 0,
                    'spin': 0,
                    'type': 'protium'
                }
        
        # История
        self.history['quanta'].append(len(self.quanta))
        self.history['particles'].append(len(self.particles))
        self.history['proton'].append(1 if self.proton else 0)
        self.history['electron'].append(1 if self.electron else 0)
        self.history['protium'].append(1 if self.protium else 0)
        self.history['interactions'].append(interactions)
        
        return interactions


# =============================================================================
# 4. ВИЗУАЛИЗАЦИЯ
# =============================================================================

def run():
    region = VacuumRegion(size=30)
    
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#0a0a0a')
    gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.4)
    
    ax_region = fig.add_subplot(gs[0, :2])
    ax_quanta = fig.add_subplot(gs[0, 2])
    ax_particles = fig.add_subplot(gs[1, 0])
    ax_interactions = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_subplot(gs[1, 2])
    
    for ax in [ax_region, ax_quanta, ax_particles, ax_interactions, ax_info]:
        ax.set_facecolor('#111111')
        ax.tick_params(colors='white', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#333333')
    
    def update(frame):
        interactions = region.step()
        
        hist = region.history
        x = np.arange(len(hist['quanta']))
        
        # ГЛАВНАЯ ОБЛАСТЬ
        ax_region.clear()
        ax_region.set_facecolor('#0a0a0a')
        ax_region.set_xlim(0, region.size)
        ax_region.set_ylim(0, region.size)
        
        # Кванты нулевой энергии (серые)
        qx = [q.x for q in region.quanta]
        qy = [q.y for q in region.quanta]
        ax_region.scatter(qx, qy, c='gray', s=15, alpha=0.5, label='Нулевая энергия')
        
        # Частицы (жёлтые — масса рождена)
        px = [p['x'] for p in region.particles]
        py = [p['y'] for p in region.particles]
        ax_region.scatter(px, py, c='yellow', s=50, marker='o', 
                         edgecolors='white', linewidths=1, label='Масса')
        
        # Протон (красный)
        if region.proton:
            ax_region.scatter([region.proton['x']], [region.proton['y']], 
                            c='red', s=200, marker='*', edgecolors='white', 
                            linewidths=2, label='ПРОТОН')
        
        # Электрон (синий)
        if region.electron:
            ax_region.scatter([region.electron['x']], [region.electron['y']], 
                            c='blue', s=100, marker='o', edgecolors='white', 
                            linewidths=1.5, label='Электрон')
        
        # Протий (зелёное свечение)
        if region.protium:
            ax_region.scatter([region.protium['x']], [region.protium['y']], 
                            c='lime', s=300, marker='o', alpha=0.3, 
                            edgecolors='lime', linewidths=3, label='ПРОТИЙ')
        
        ax_region.set_title('Локальная область вакуума (высокая плотность)', 
                           color='white', fontsize=11)
        ax_region.legend(facecolor='#111111', edgecolor='none', fontsize=7, loc='upper right')
        ax_region.tick_params(colors='white', labelsize=8)
        
        # Кванты
        ax_quanta.clear()
        ax_quanta.set_facecolor('#111111')
        ax_quanta.plot(x, hist['quanta'], color='gray', linewidth=1.5)
        ax_quanta.set_title('Кванты нулевой энергии', color='white', fontsize=10)
        ax_quanta.tick_params(colors='white', labelsize=8)
        
        # Частицы
        ax_particles.clear()
        ax_particles.set_facecolor('#111111')
        ax_particles.plot(x, hist['particles'], color='yellow', linewidth=1.5)
        ax_particles.set_title('Рождённые частицы', color='white', fontsize=10)
        ax_particles.tick_params(colors='white', labelsize=8)
        
        # Взаимодействия
        ax_interactions.clear()
        ax_interactions.set_facecolor('#111111')
        ax_interactions.plot(x, hist['interactions'], color='magenta', linewidth=1.5)
        ax_interactions.set_title('Взаимодействия', color='white', fontsize=10)
        ax_interactions.tick_params(colors='white', labelsize=8)
        
        # Инфо
        ax_info.clear()
        ax_info.set_facecolor('#0a0a0a')
        ax_info.axis('off')
        info_text = (
            f"ШАГ: {frame}\n"
            f"Квантов: {len(region.quanta)}\n"
            f"Частиц: {len(region.particles)}\n"
            f"ПРОТОН: {'✅' if region.proton else '❌'}\n"
            f"Электрон: {'✅' if region.electron else '❌'}\n"
            f"ПРОТИЙ: {'✅ ОБРАЗОВАН' if region.protium else '⏳'}\n"
            f"Взаимодействий: {interactions}"
        )
        ax_info.text(0.05, 0.5, info_text, color='white', fontsize=11,
                     family='monospace', verticalalignment='center')
        
        fig.canvas.draw_idle()
        return []
    
    anim = animation.FuncAnimation(fig, update, frames=300, interval=50, blit=False, repeat=False)
    plt.show()


if __name__ == "__main__":
    run()
