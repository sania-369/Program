#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
ETVP 12.5 VACUUM GENESIS — Зарождение протия из нулевой энергии
================================================================================
Модель первородного вакуума и рождения первой материи.

КОНЦЕПЦИЯ:
1. Нулевая энергия — первородное пространство (масса=0, заряд=0, спин=0)
2. Флуктуации вакуума — кипение нулевой энергии
3. Столкновение двух квантов → точка массы (m > 0)
4. Трение → заряд + магнитный момент
5. Заряд + магнитный момент → спин
6. Протон + нулевая энергия → электрон (противоположный спин)
7. Баланс → протий (атом водорода)

КЛЮЧЕВЫЕ УРАВНЕНИЯ:
- Масса рождается из столкновения: m = E₁ + E₂ (в точке контакта)
- Заряд рождается из трения: q = f(масса, спин)
- Спин из баланса: s = 1/2 (для протона и электрона)
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

# Фундаментальные параметры
M_PROTON = 938.272  # МэВ
M_ELECTRON = 0.511  # МэВ
Q_PROTON = 1.0      # Элементарный заряд
Q_ELECTRON = -1.0
SPIN_HALF = 0.5


# =============================================================================
# 1. НУЛЕВАЯ ЭНЕРГИЯ (ВАКУУМ)
# =============================================================================

class ZeroEnergyVacuum:
    """
    Первородное пространство нулевой энергии.
    Состояние: масса = 0, заряд = 0, магнитный момент = 0, спин = 0.
    """
    
    def __init__(self, size=100, fluctuation_amplitude=0.01):
        self.size = size
        self.amplitude = fluctuation_amplitude
        
        # Поле нулевой энергии (флуктуации)
        self.field = np.random.randn(size, size) * self.amplitude
        
        # Порции энергии (кванты)
        self.quanta = []
        
        self.history = {'fluctuations': [], 'collisions': [], 'mass_born': []}
    
    def fluctuate(self):
        """
        Кипение вакуума — флуктуации нулевой энергии.
        """
        # Добавляем случайные флуктуации
        self.field += np.random.randn(self.size, self.size) * self.amplitude * 0.1
        
        # Порождение квантов из флуктуаций
        if random.random() < 0.05:
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
                'type': 'quantum'
            })
        
        self.history['fluctuations'].append(np.mean(np.abs(self.field)))
        
        return len(self.quanta)
    
    def check_collisions(self):
        """
        Проверка столкновений квантов.
        При столкновении → рождение массы.
        """
        collisions = 0
        
        for i in range(len(self.quanta)):
            for j in range(i + 1, len(self.quanta)):
                q1 = self.quanta[i]
                q2 = self.quanta[j]
                
                # Проверка близости
                dx = q1['x'] - q2['x']
                dy = q1['y'] - q2['y']
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist < 2.0:  # Порог столкновения
                    collisions += 1
                    self._create_mass(q1, q2)
                    
                    # Удаляем столкнувшиеся кванты
                    self.quanta[i] = None
                    self.quanta[j] = None
        
        # Очистка
        self.quanta = [q for q in self.quanta if q is not None]
        
        self.history['collisions'].append(collisions)
        return collisions
    
    def _create_mass(self, q1, q2):
        """
        Рождение точки массы из столкновения двух квантов.
        """
        total_energy = q1['energy'] + q2['energy']
        
        # Масса рождается (E = mc² → m = E)
        mass = total_energy * PHI  # Золотое сечение — коэффициент рождения
        
        # Заряд из трения
        charge = 1.0 if q1['energy'] > q2['energy'] else -1.0
        
        # Спин из баланса
        spin = SPIN_HALF
        
        self.history['mass_born'].append(mass)


# =============================================================================
# 2. РОЖДЕНИЕ ПРОТОНА
# =============================================================================

class ProtonBirth:
    """
    Рождение протона из вакуумных флуктуаций.
    """
    
    def __init__(self, target_mass=M_PROTON):
        self.target_mass = target_mass
        self.energy_accumulated = 0.0
        self.proton_born = False
        
        self.history = {'energy': [], 'progress': []}
    
    def accumulate_energy(self, vacuum):
        """
        Накопление энергии до порога рождения протона.
        """
        # Собираем энергию из квантов
        for q in vacuum.quanta:
            self.energy_accumulated += q['energy']
        
        # Прогресс рождения
        progress = min(self.energy_accumulated / self.target_mass, 1.0)
        
        self.history['energy'].append(self.energy_accumulated)
        self.history['progress'].append(progress)
        
        if progress >= 1.0:
            self.proton_born = True
        
        return progress
    
    def create_proton(self):
        """
        Создание протона при достижении порога.
        """
        if self.proton_born:
            return {
                'mass': M_PROTON,
                'charge': Q_PROTON,
                'spin': SPIN_HALF,
                'type': 'proton',
                'energy_source': self.energy_accumulated
            }
        return None


# =============================================================================
# 3. РОЖДЕНИЕ ЭЛЕКТРОНА И ПРОТИЯ
# =============================================================================

def create_electron_from_proton(proton):
    """
    Протон + нулевая энергия → электрон (противоположный спин).
    """
    return {
        'mass': M_ELECTRON,
        'charge': Q_ELECTRON,
        'spin': -SPIN_HALF,  # Противоположный спин
        'type': 'electron'
    }


def create_protium(proton, electron):
    """
    Баланс протона и электрона → протий (атом водорода).
    """
    return {
        'mass': proton['mass'] + electron['mass'],
        'charge': proton['charge'] + electron['charge'],  # 0 — нейтральный
        'spin': proton['spin'] + electron['spin'],  # 0 — баланс
        'type': 'protium',
        'components': [proton, electron]
    }


# =============================================================================
# 4. ПОЛНАЯ СИМУЛЯЦИЯ
# =============================================================================

class VacuumGenesisSimulation:
    """
    Полная симуляция зарождения материи.
    """
    
    def __init__(self):
        self.vacuum = ZeroEnergyVacuum(size=50, fluctuation_amplitude=0.05)
        self.proton_birth = ProtonBirth()
        self.proton = None
        self.electron = None
        self.protium = None
        self.step_counter = 0
        
        self.history = {
            'quanta_count': [], 'collisions': [], 
            'energy_accumulated': [], 'progress': [],
            'fluctuation_mean': []
        }
    
    def step(self):
        """Один шаг симуляции зарождения."""
        self.step_counter += 1
        
        # 1. Флуктуации вакуума
        quanta_count = self.vacuum.fluctuate()
        
        # 2. Столкновения
        collisions = self.vacuum.check_collisions()
        
        # 3. Накопление энергии для протона
        progress = self.proton_birth.accumulate_energy(self.vacuum)
        
        # 4. Рождение протона
        if self.proton is None:
            self.proton = self.proton_birth.create_proton()
            if self.proton:
                print(f"  ✅ Протон родился на шаге {self.step_counter}!")
        
        # 5. Рождение электрона
        if self.proton is not None and self.electron is None:
            self.electron = create_electron_from_proton(self.proton)
            print(f"  ✅ Электрон родился на шаге {self.step_counter}!")
        
        # 6. Образование протия
        if self.proton is not None and self.electron is not None and self.protium is None:
            self.protium = create_protium(self.proton, self.electron)
            print(f"  ✅ ПРОТИЙ ОБРАЗОВАН на шаге {self.step_counter}!")
        
        # История
        self.history['quanta_count'].append(quanta_count)
        self.history['collisions'].append(collisions)
        self.history['energy_accumulated'].append(self.proton_birth.energy_accumulated)
        self.history['progress'].append(progress)
        self.history['fluctuation_mean'].append(np.mean(np.abs(self.vacuum.field)))
        
        return {
            'quanta': quanta_count,
            'collisions': collisions,
            'progress': progress,
            'proton_born': self.proton is not None,
            'electron_born': self.electron is not None,
            'protium_born': self.protium is not None
        }


# =============================================================================
# 5. ВИЗУАЛИЗАЦИЯ
# =============================================================================

def run_simulation():
    sim = VacuumGenesisSimulation()
    
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#0a0a0a')
    gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.4)
    
    ax_vacuum = fig.add_subplot(gs[0, 0])
    ax_quanta = fig.add_subplot(gs[0, 1])
    ax_energy = fig.add_subplot(gs[0, 2])
    ax_collisions = fig.add_subplot(gs[1, 0])
    ax_progress = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_subplot(gs[1, 2])
    
    for ax in [ax_vacuum, ax_quanta, ax_energy, ax_collisions, ax_progress, ax_info]:
        ax.set_facecolor('#111111')
        ax.tick_params(colors='white', labelsize=8)
        for spine in ax.spines.values():
            spine.set_color('#333333')
    
    def update(frame):
        result = sim.step()
        
        hist = sim.history
        x = np.arange(len(hist['quanta_count']))
        
        # Поле вакуума
        ax_vacuum.clear()
        ax_vacuum.set_facecolor('#111111')
        im = ax_vacuum.imshow(sim.vacuum.field, cmap='viridis', aspect='auto')
        ax_vacuum.set_title('Поле нулевой энергии', color='white', fontsize=10)
        ax_vacuum.tick_params(colors='white', labelsize=7)
        
        # Кванты
        ax_quanta.clear()
        ax_quanta.set_facecolor('#111111')
        ax_quanta.plot(x, hist['quanta_count'], color='cyan', linewidth=1.5)
        ax_quanta.set_title('Количество квантов', color='white', fontsize=10)
        ax_quanta.tick_params(colors='white', labelsize=8)
        
        # Энергия
        ax_energy.clear()
        ax_energy.set_facecolor('#111111')
        ax_energy.plot(x, hist['energy_accumulated'], color='yellow', linewidth=1.5)
        ax_energy.axhline(M_PROTON, color='red', linestyle='--', linewidth=0.8, label='Порог протона')
        ax_energy.set_title('Накопленная энергия', color='white', fontsize=10)
        ax_energy.tick_params(colors='white', labelsize=8)
        ax_energy.legend(facecolor='#111111', edgecolor='none', fontsize=7)
        
        # Столкновения
        ax_collisions.clear()
        ax_collisions.set_facecolor('#111111')
        ax_collisions.plot(x, hist['collisions'], color='magenta', linewidth=1.5)
        ax_collisions.set_title('Столкновения квантов', color='white', fontsize=10)
        ax_collisions.tick_params(colors='white', labelsize=8)
        
        # Прогресс
        ax_progress.clear()
        ax_progress.set_facecolor('#111111')
        ax_progress.plot(x, hist['progress'], color='lime', linewidth=1.5)
        ax_progress.axhline(1.0, color='yellow', linestyle='--', linewidth=0.8)
        ax_progress.set_ylim(0, 1.1)
        ax_progress.set_title('Прогресс рождения протона', color='white', fontsize=10)
        ax_progress.tick_params(colors='white', labelsize=8)
        
        # Инфо
        ax_info.clear()
        ax_info.set_facecolor('#0a0a0a')
        ax_info.axis('off')
        info_text = (
            f"ШАГ: {sim.step_counter}\n"
            f"Квантов: {result['quanta']}\n"
            f"Столкновений: {result['collisions']}\n"
            f"Энергия: {sim.proton_birth.energy_accumulated:.1f} / {M_PROTON}\n"
            f"Прогресс: {result['progress']*100:.2f}%\n"
            f"Протон: {'✅ ДА' if result['proton_born'] else '❌ НЕТ'}\n"
            f"Электрон: {'✅ ДА' if result['electron_born'] else '❌ НЕТ'}\n"
            f"ПРОТИЙ: {'✅ ОБРАЗОВАН' if result['protium_born'] else '⏳ Ждём'}"
        )
        ax_info.text(0.05, 0.5, info_text, color='white', fontsize=11,
                     family='monospace', verticalalignment='center')
        
        fig.canvas.draw_idle()
        return []
    
    anim = animation.FuncAnimation(fig, update, frames=500, interval=50, blit=False, repeat=False)
    plt.show()
    
    print("═" * 60)
    print("  ФИНАЛЬНЫЙ ОТЧЁТ:")
    print("═" * 60)
    print(f"  Шагов: {sim.step_counter}")
    print(f"  Протон: {'родился' if sim.proton else 'НЕ родился'}")
    print(f"  Электрон: {'родился' if sim.electron else 'НЕ родился'}")
    print(f"  Протий: {'ОБРАЗОВАН' if sim.protium else 'НЕ образован'}")
    if sim.protium:
        print(f"  Масса протия: {sim.protium['mass']:.1f} МэВ")
        print(f"  Заряд: {sim.protium['charge']}")
        print(f"  Спин: {sim.protium['spin']}")
    print("═" * 60)


if __name__ == "__main__":
    run_simulation()
