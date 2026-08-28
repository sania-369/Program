#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP: Рождение протия из кипящего вакуума.
Визуализация процесса, где кванты энергии вылетают из вакуума,
сталкиваются и под давлением вакуума сразу образуют протий.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from matplotlib.collections import LineCollection

# =============================================================================
# 1. ПАРАМЕТРЫ
# =============================================================================

GRID_SIZE = 100
PHI = (1 + np.sqrt(5)) / 2
VACUUM_PRESSURE = 0.9  # Абсолютное давление вакуума

# =============================================================================
# 2. КИПЯЩИЙ ВАКУУМ
# =============================================================================

def boiling_vacuum(frame):
    """
    Генерирует состояние кипящего вакуума:
    - Постоянные флуктуации нулевой энергии.
    - Вылетающие порции энергии (кванты).
    """
    # Базовое поле — случайные флуктуации
    field = np.random.normal(0, 0.1, (GRID_SIZE, GRID_SIZE))
    
    # Кванты — это локализованные порции энергии
    # Они вылетают из вакуума в случайных точках
    num_quanta = 10 + int(5 * np.sin(frame / 20))
    for _ in range(num_quanta):
        x = np.random.randint(5, GRID_SIZE-5)
        y = np.random.randint(5, GRID_SIZE-5)
        size = np.random.uniform(2, 6)
        strength = np.random.uniform(0.2, 0.8)
        direction = np.random.uniform(0, 2 * np.pi)
        
        # Создаём квант как гауссово возмущение
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                dist = np.sqrt((i-x)**2 + (j-y)**2)
                if dist < size:
                    field[i, j] += strength * np.exp(-dist**2 / (2*(size/3)**2))
    
    # Абсолютное давление вакуума сжимает поле
    field = np.tanh(field * VACUUM_PRESSURE)  # Z-принцип
    return field

# =============================================================================
# 3. РОЖДЕНИЕ ПРОТИЯ ИЗ СТОЛКНОВЕНИЯ КВАНТОВ
# =============================================================================

def protyum_birth(field, frame):
    """
    Моделирует столкновение квантов и рождение протия.
    """
    # Копируем поле
    new_field = field.copy()
    
    # Находим локальные максимумы (потенциальные кванты)
    max_points = []
    for i in range(1, GRID_SIZE-1):
        for j in range(1, GRID_SIZE-1):
            if (new_field[i, j] > new_field[i-1, j] and
                new_field[i, j] > new_field[i+1, j] and
                new_field[i, j] > new_field[i, j-1] and
                new_field[i, j] > new_field[i, j+1] and
                new_field[i, j] > 0.3):
                max_points.append((i, j, new_field[i, j]))
    
    # Сортируем по силе
    max_points.sort(key=lambda x: x[2], reverse=True)
    
    # Столкновение двух самых сильных квантов
    if len(max_points) >= 2:
        # Первый квант (протон)
        p1 = max_points[0]
        x1, y1, s1 = p1
        # Второй квант (электрон)
        p2 = max_points[1]
        x2, y2, s2 = p2
        
        # Расчёт точки столкновения
        dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
        if dist < 20:  # Если кванты близко
            # Рождение протия в точке между ними
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            radius = max(3, int(dist / 3))
            
            # Создаём структуру протия: протон + электрон
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    dist_to_center = np.sqrt((i-cx)**2 + (j-cy)**2)
                    if dist_to_center < radius:
                        # Внутренняя область — протон (масса, заряд)
                        proton_strength = (s1 + s2) * 0.5 * np.exp(-dist_to_center**2 / radius)
                        new_field[i, j] += proton_strength * 0.3
                        
                        # Внешняя область — электрон (волна, спин)
                        if dist_to_center > radius * 0.5:
                            wave = np.sin(2 * np.pi * dist_to_center / (radius * 0.5) + frame * 0.1)
                            new_field[i, j] += wave * 0.1 * np.exp(-dist_to_center**2 / (radius*2))
    
    # Применяем абсолютное давление вакуума
    new_field = np.tanh(new_field * VACUUM_PRESSURE)
    return new_field

# =============================================================================
# 4. ВИЗУАЛИЗАЦИЯ
# =============================================================================

fig = plt.figure(figsize=(14, 10))
fig.suptitle('ETVP: Рождение протия из кипящего вакуума\n'
             'Кванты вылетают, сталкиваются и сразу образуют протий под давлением вакуума',
             fontsize=14, color='white')
fig.patch.set_facecolor('#0a0a0a')

# Сетка
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# 1. Кипящий вакуум
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_title('Кипящий вакуум (нулевая энергия)', color='white', fontsize=10)

# 2. Порции энергии (кванты)
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_title('Порции энергии (кванты)', color='white', fontsize=10)

# 3. Столкновение и взаимодействие
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_title('Столкновение и взаимодействие', color='white', fontsize=10)

# 4. Рождение протия
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_title('Рождение протия (p⁺ + e⁻)', color='white', fontsize=10)

# Настройка осей
for ax in [ax1, ax2, ax3, ax4]:
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white', labelsize=6)
    for spine in ax.spines.values():
        spine.set_color('#333333')

# =============================================================================
# 5. АНИМАЦИЯ
# =============================================================================

def update(frame):
    # Состояние вакуума
    vacuum = boiling_vacuum(frame)
    
    # Рождение протия
    protyum = protyum_birth(vacuum, frame)
    
    # 1. Кипящий вакуум
    ax1.clear()
    ax1.set_facecolor('#111111')
    ax1.imshow(vacuum, cmap='gray', origin='lower', vmin=-0.5, vmax=0.5)
    ax1.set_title('Кипящий вакуум (нулевая энергия)', color='white', fontsize=10)
    ax1.tick_params(colors='white', labelsize=6)
    
    # 2. Порции энергии (кванты) — локальные максимумы
    ax2.clear()
    ax2.set_facecolor('#111111')
    # Показываем кванты как яркие пятна
    quanta = np.zeros_like(vacuum)
    quanta[vacuum > 0.3] = vacuum[vacuum > 0.3]
    ax2.imshow(quanta, cmap='hot', origin='lower', vmin=0, vmax=0.5)
    ax2.set_title('Порции энергии (кванты)', color='white', fontsize=10)
    ax2.tick_params(colors='white', labelsize=6)
    
    # 3. Столкновение — взаимодействие двух квантов
    ax3.clear()
    ax3.set_facecolor('#111111')
    # Показываем область столкновения
    collision = np.zeros_like(vacuum)
    # Находим локальные максимумы
    for i in range(1, GRID_SIZE-1):
        for j in range(1, GRID_SIZE-1):
            if (vacuum[i, j] > vacuum[i-1, j] and
                vacuum[i, j] > vacuum[i+1, j] and
                vacuum[i, j] > vacuum[i, j-1] and
                vacuum[i, j] > vacuum[i, j+1] and
                vacuum[i, j] > 0.25):
                # Рисуем круги вокруг максимумов
                for di in range(-5, 6):
                    for dj in range(-5, 6):
                        if 0 <= i+di < GRID_SIZE and 0 <= j+dj < GRID_SIZE:
                            dist = np.sqrt(di**2 + dj**2)
                            if dist < 5:
                                collision[i+di, j+dj] += vacuum[i, j] * (1 - dist/5)
    ax3.imshow(collision, cmap='plasma', origin='lower')
    ax3.set_title('Столкновение и взаимодействие', color='white', fontsize=10)
    ax3.tick_params(colors='white', labelsize=6)
    
    # 4. Рождение протия
    ax4.clear()
    ax4.set_facecolor('#111111')
    ax4.imshow(protyum, cmap='viridis', origin='lower')
    ax4.set_title('Рождение протия (p⁺ + e⁻)', color='white', fontsize=10)
    ax4.tick_params(colors='white', labelsize=6)
    
    # Статус
    status = f'Шаг: {frame}'
    fig.text(0.5, 0.02, status, ha='center', color='cyan', fontsize=10)
    
    return []

# Создание анимации
anim = FuncAnimation(fig, update, frames=200, interval=50, blit=False)

plt.show()

print("\n" + "=" * 70)
print("ETVP: Рождение протия из кипящего вакуума")
print("=" * 70)
print("Процесс:")
print("1. Кипящий вакуум — постоянные флуктуации нулевой энергии.")
print("2. Порции энергии (кванты) — локализованные возмущения.")
print("3. Кванты сталкиваются и взаимодействуют.")
print("4. Абсолютное давление вакуума — немедленно формирует протий.")
print("=" * 70)
