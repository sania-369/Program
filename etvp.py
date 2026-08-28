#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
ETVP 12.5 VACUUM GENESIS v5 — Одна флуктуация в абсолютном хаосе
================================================================================
Максимальный хаос + абсолютный потенциал = рождение ПРОТИЯ.

КОНЦЕПЦИЯ (по модели ЕТВП):
1. Нулевая энергия — первородное пространство (m=0, q=0, s=0)
2. Максимальный хаос — флуктуации повсюду
3. Абсолютный потенциал — бесконечная энергия
4. Столкновение квантов → точка массы
5. Трение → заряд + магнитный момент
6. Заряд + магнит → спин
7. Протон + нулевая энергия → электрон (противоположный спин)
8. Баланс → ПРОТИЙ

Нейтрон — не отдельная частица (электронный захват, распад, время жизни).
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
MAX_CHAOS = 1.0            # Максимальный хаос
ABSOLUTE_POTENTIAL = 1.0   # Абсолютный потенциал

# Константы частиц
M_PROTON = 938.272
M_ELECTRON = 0.511
Q_PROTON = 1.0
Q_ELECTRON = -1.0
SPIN = 0.5


# =============================================================================
# 1. КВАНТ НУЛЕВОЙ ЭНЕРГИИ
# =============================================================================

class Quantum:
    """
    Порция нулевой энергии.
    m=0, q=0, спин=0, магнитный момент=0.
    """
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = random.uniform(0.1, 1.0) * ABSOLUTE_POTENTIAL
        
        # Всё равно нулю
        self.mass = 0.0
        self.charge = 0.0
        self.spin = 0.0
        self.magnetic_moment = 0.0
        
        self.vx = random.uniform(-0.03, 0.03) * MAX_CHAOS
        self.vy = random.uniform(-0.03, 0.03) * MAX_CHAOS
        
        self.type = 'zero_energy'
        self.alive = True


# =============================================================================
# 2. РОЖДЕНИЕ ПРОТОНА И ПРОТИЯ
# =============================================================================

def create_proton(q1, q2):
    """
    Столкновение двух квантов → ПРОТОН.
    """
    # Точка столкновения
    x = (q1.x + q2.x) / 2
    y = (q1.y + q2.y) / 2
    
    # Масса из энергии (E = mc²)
    mass = (q1.energy + q2.energy) * PHI * 100
    
    # Заряд из трения (асимметрия)
    charge = Q_PROTON
    
    # Магнитный момент из заряда
    magnetic_moment = charge * 0.5
    
    # Спин из баланса
    spin = SPIN
    
    return {
        'x': x,
        'y': y,
        'mass': mass,
        'charge': charge,
        'spin': spin,
        'magnetic_moment': magnetic_moment,
        'type': 'proton',
        'energy': mass
    }


def create_electron(proton):
    """
    Протон + нулевая энергия → ЭЛЕКТРОН.
    Противоположный заряд и спин.
    """
    return {
        'x': proton['x'] + random.uniform(-2, 2),
        'y': proton['y'] + random.uniform(-2, 2),
        'mass': M_ELECTRON,
        'charge': Q_ELECTRON,
        'spin': -SPIN,  # Противоположный спин
        'magnetic_moment': Q_ELECTRON * 0.5,
        'type': 'electron',
        'energy': M_ELECTRON
    }


def create_protium(proton, electron):
    """
    Баланс → ПРОТИЙ (атом водорода).
    """
    return {
        'x': (proton['x'] + electron['x']) / 2,
        'y': (proton['y'] + electron['y']) / 2,
        'mass': proton['mass'] + electron['mass'],
        'charge': proton['charge'] + electron['charge'],  # 0
        'spin': proton['spin'] + electron['spin'],  # 0
        'type': 'protium'
    }


# =============================================================================
# 3. ОДНА ФЛУКТУАЦИЯ
# =============================================================================

class SingleFluctuation:
    """
    Одна флуктуация в одной области.
    """
    
    def __init__(self, size=40, num_quanta=36):
        self.size = size
        self.num_quanta = num_quanta
        self.step_counter = 0
        
        # Кванты нулевой энергии (равномерно в хаосе)
        self.quanta = []
        for _ in range(num_quanta):
            self.quanta.append(Quantum(
                random.uniform(5, size - 5),
                random.uniform(5, size - 5)
            ))
        
        self.proton = None
        self.electron = None
        self.protium = None
        
        # Поле хаоса (фон)
        self.chaos_field = np.random.rand(size, size) * MAX_CHAOS
        
        # История
        self.history = {
            'quanta': [], 'chaos': [], 'proton': [], 'electron': [], 'protium': []
        }
    
    def _update_chaos(self):
        """Максимальный хаос — флуктуации повсюду."""
        self.chaos_field = np.random.rand(self.size, self.size) * MAX_CHAOS
    
    def step(self):
        """Один шаг флуктуации."""
        self.step_counter += 1
        
        # Хаос флуктуирует
        self._update_chaos()
        
        # Движение и взаимодействие квантов
        for i in range(len(self.quanta)):
            q1 = self.quanta[i]
            if not q1.alive:
                continue
            
            for j in range(i + 1, len(self.quanta)):
                q2 = self.quanta[j]
                if not q2.alive:
                    continue
                
                dist = math.sqrt((q1.x - q2.x)**2 + (q1.y - q2.y)**2)
                
                if dist < 1.0 and self.proton is None:
                    # СТОЛКНОВЕНИЕ → ПРОТОН
                    self.proton = create_proton(q1, q2)
                    q1.alive = False
                    q2.alive = False
                    
                elif dist < 3.0:
                    # Притяжение (абсолютный потенциал)
                    force = 0.1 / (dist ** 2) * ABSOLUTE_POTENTIAL
                    dx = (q2.x - q1.x) / dist
                    dy = (q2.y - q1.y) / dist
                    q1.vx += dx * force
                    q1.vy += dy * force
                    q2.vx -= dx * force
                    q2.vy -= dy * force
        
        # Движение квантов
        for q in self.quanta:
            if q.alive:
                q.x += q.vx
                q.y += q.vy
                q.vx *= 0.99
                q.vy *= 0.99
                
                # Границы
                if q.x < 0: q.x = 0; q.vx *= -0.5
                if q.x >= self.size: q.x = self.size - 1; q.vx *= -0.5
                if q.y < 0: q.y = 0; q.vy *= -0.5
                if q.y >= self.size: q.y = self.size - 1; q.vy *= -0.5
        
        # Рождение электрона
        if self.proton is not None and self.electron is None:
            self.electron = create_electron(self.proton)
        
        # Образование протия
        if (self.proton is not None and self.electron is not None 
            and self.protium is None):
            self.protium = create_protium(self.proton, self.electron)
        
        # История
        alive_quanta = sum(1 for q in self.quanta if q.alive)
        self.history['quanta'].append(alive_quanta)
        self.history['chaos'].append(np.mean(self.chaos_field))
        self.history['proton'].append(1 if self.proton else 0)
        self.history['electron'].append(1 if self.electron else 0)
        self.history['protium'].append(1 if self.protium else 0)
        
        return alive_quanta


# =============================================================================
# 4. ВИЗУАЛИЗАЦИЯ
# =============================================================================

def run():
    fluct = SingleFluctuation(size=40, num_quanta=36)
    
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#0a0a0a')
    gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.4)
    
    ax_main = fig.add_subplot(gs[0, :2])
    ax_chaos = fig.add_subplot(gs[0, 2])
    ax_quanta = fig.add_subplot(gs[1, 0])
    ax_birth = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_subplot(gs[1, 2])
    
    for ax in [ax_main, ax_chaos, ax_quanta, ax_birth, ax_info]:
        ax.set_facecolor('#111111')
        ax.tick_params(colors='white', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#333333')
    
    def update(frame):
        alive = fluct.step()
        
        hist = fluct.history
        x = np.arange(len(hist['quanta']))
        
        # ГЛАВНАЯ ОБЛАСТЬ
        ax_main.clear()
        ax_main.set_facecolor('#0a0a0a')
        ax_main.set_xlim(0, fluct.size)
        ax_main.set_ylim(0, fluct.size)
        
        # Фон — хаос
        ax_main.imshow(fluct.chaos_field, cmap='gray', alpha=0.3, 
                      extent=[0, fluct.size, 0, fluct.size])
        
        # Кванты нулевой энергии
        alive_q = [q for q in fluct.quanta if q.alive]
        qx = [q.x for q in alive_q]
        qy = [q.y for q in alive_q]
        ax_main.scatter(qx, qy, c='white', s=20, alpha=0.6, 
                       edgecolors='gray', linewidths=0.5, label='Нулевая энергия')
        
        # Протон
        if fluct.proton:
            ax_main.scatter([fluct.proton['x']], [fluct.proton['y']], 
                          c='red', s=300, marker='*', edgecolors='white',
                          linewidths=2.5, label='ПРОТОН (m>0, q=+1, s=1/2)')
        
        # Электрон
        if fluct.electron:
            ax_main.scatter([fluct.electron['x']], [fluct.electron['y']],
                          c='blue', s=120, marker='o', edgecolors='white',
                          linewidths=2, label='ЭЛЕКТРОН (q=−1, s=−1/2)')
        
        # Протий
        if fluct.protium:
            ax_main.scatter([fluct.protium['x']], [fluct.protium['y']],
                          c='lime', s=500, marker='o', alpha=0.25,
                          edgecolors='lime', linewidths=4, label='ПРОТИЙ (баланс)')
        
        ax_main.set_title('ОДНА ФЛУКТУАЦИЯ — Рождение протия из нулевой энергии',
                         color='white', fontsize=12)
        ax_main.legend(facecolor='#111111', edgecolor='none', fontsize=8,
                      loc='upper right')
        ax_main.tick_params(colors='white', labelsize=8)
        
        # Хаос
        ax_chaos.clear()
        ax_chaos.set_facecolor('#111111')
        ax_chaos.plot(x, hist['chaos'], color='gray', linewidth=1.5)
        ax_chaos.axhline(MAX_CHAOS, color='red', linestyle='--', linewidth=0.8,
                        label='Макс. хаос')
        ax_chaos.set_ylim(0, 1.2)
        ax_chaos.set_title('Уровень хаоса', color='white', fontsize=10)
        ax_chaos.tick_params(colors='white', labelsize=8)
        ax_chaos.legend(facecolor='#111111', edgecolor='none', fontsize=7)
        
        # Кванты
        ax_quanta.clear()
        ax_quanta.set_facecolor('#111111')
        ax_quanta.plot(x, hist['quanta'], color='white', linewidth=1.5)
        ax_quanta.set_title('Кванты нулевой энергии', color='white', fontsize=10)
        ax_quanta.tick_params(colors='white', labelsize=8)
        
        # Рождение
        ax_birth.clear()
        ax_birth.set_facecolor('#111111')
        ax_birth.plot(x, hist['proton'], color='red', linewidth=1.5, label='Протон')
        ax_birth.plot(x, hist['electron'], color='blue', linewidth=1.5, label='Электрон')
        ax_birth.plot(x, hist['protium'], color='lime', linewidth=2, label='ПРОТИЙ')
        ax_birth.set_ylim(0, 1.2)
        ax_birth.set_title('Рождение частиц', color='white', fontsize=10)
        ax_birth.tick_params(colors='white', labelsize=8)
        ax_birth.legend(facecolor='#111111', edgecolor='none', fontsize=7)
        
        # Инфо
        ax_info.clear()
        ax_info.set_facecolor('#0a0a0a')
        ax_info.axis('off')
        info_text = (
            f"ШАГ: {frame}\n"
            f"Квантов: {alive}\n"
            f"Хаос: макс ✅\n"
            f"Потенциал: абсолютный ✅\n"
            f"ПРОТОН: {'✅ РОДИЛСЯ' if fluct.proton else '❌'}\n"
            f"  m={fluct.proton['mass']:.1f}, q={fluct.proton['charge']}, s={fluct.proton['spin']}\n" if fluct.proton else
            f"Электрон: {'✅' if fluct.electron else '❌'}\n"
            f"ПРОТИЙ: {'✅ ОБРАЗОВАН' if fluct.protium else '⏳'}\n" +
            (f"  Баланс: q=0, s=0" if fluct.protium else "")
        )
        ax_info.text(0.05, 0.5, info_text, color='white', fontsize=10,
                     family='monospace', verticalalignment='center')
        
        fig.canvas.draw_idle()
        return []
    
    anim = animation.FuncAnimation(fig, update, frames=300, interval=50, 
                                  blit=False, repeat=False)
    plt.show()


if __name__ == "__main__":
    run()
