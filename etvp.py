#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP: Рождение частицы из нулевой энергии.
Визуализация флуктуации в пространстве с максимальным хаосом
и абсолютным потенциалом.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.collections import LineCollection
import matplotlib.colors as colors

# =============================================================================
# 1. ПАРАМЕТРЫ
# =============================================================================

GRID_SIZE = 100
PHI = (1 + np.sqrt(5)) / 2

# Пространство нулевой энергии
ZERO_FIELD = np.zeros((GRID_SIZE, GRID_SIZE))

# =============================================================================
# 2. СОЗДАНИЕ ПОЛЯ С ХАОСОМ
# =============================================================================

def create_chaotic_field():
    """Поле нулевой энергии с максимальным хаосом и потенциалом."""
    # Базовое поле — флуктуации нулевой энергии
    field = np.random.normal(0, 0.1, (GRID_SIZE, GRID_SIZE))
    
    # Добавляем когерентные структуры (потенциальные точки рождения)
    for _ in range(5):
        x0 = np.random.randint(10, GRID_SIZE-10)
        y0 = np.random.randint(10, GRID_SIZE-10)
        r = np.random.randint(5, 15)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                dist = np.sqrt((i-x0)**2 + (j-y0)**2)
                if dist < r:
                    field[i, j] += 0.5 * np.exp(-dist**2 / (2*(r/2)**2))
    
    # Абсолютный потенциал — поле стремится к самоорганизации
    field = np.tanh(field * PHI)  # Z-принцип: нелинейное сжатие
    return field

# =============================================================================
# 3. РОЖДЕНИЕ ЧАСТИЦЫ ИЗ ФЛУКТУАЦИИ
# =============================================================================

def particle_birth(field, x0, y0, frame):
    """
    Моделирует рождение частицы в точке флуктуации.
    Возвращает поле, массу, заряд, спин.
    """
    # Копируем поле
    new_field = field.copy()
    
    # Параметры флуктуации
    t = frame / 100.0  # время в условных единицах
    r_fluct = 5 + 10 * np.sin(t * 2 * np.pi)  # радиус флуктуации
    strength = 0.5 + 0.5 * np.sin(t * 2 * np.pi)  # сила флуктуации
    
    # Наложение флуктуации
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            dist = np.sqrt((i-x0)**2 + (j-y0)**2)
            if dist < r_fluct:
                # Флуктуация как интерференция двух волн нулевой энергии
                wave1 = np.sin(2 * np.pi * dist / (5 + 2 * np.sin(t)))
                wave2 = np.cos(2 * np.pi * dist / (3 + 2 * np.cos(t)))
                new_field[i, j] += strength * (wave1 + wave2) * np.exp(-dist**2 / 10)
    
    # Масса: появляется там, где две порции энергии встретились
    mass = np.zeros((GRID_SIZE, GRID_SIZE))
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if np.abs(new_field[i, j]) > 0.8:
                mass[i, j] = np.abs(new_field[i, j]) - 0.8
    
    # Заряд и магнитный момент (пропорциональны градиенту поля)
    grad_y, grad_x = np.gradient(new_field)
    charge = grad_x + grad_y
    magnetic = grad_x - grad_y
    
    # Спин (циркуляция поля)
    spin = np.zeros((GRID_SIZE, GRID_SIZE))
    for i in range(1, GRID_SIZE-1):
        for j in range(1, GRID_SIZE-1):
            spin[i, j] = (new_field[i+1, j] - new_field[i-1, j] -
                          new_field[i, j+1] + new_field[i, j-1])
    
    return new_field, mass, charge, magnetic, spin

# =============================================================================
# 4. ВИЗУАЛИЗАЦИЯ
# =============================================================================

fig = plt.figure(figsize=(16, 12))
fig.suptitle('ETVP: Рождение частицы из нулевой энергии\n'
             'Флуктуация в пространстве с максимальным хаосом и абсолютным потенциалом',
             fontsize=14, color='white')
fig.patch.set_facecolor('#0a0a0a')

# Сетка для графиков
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

# 1. Поле нулевой энергии (хаос)
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_title('Нулевая энергия (потенциал)', color='white', fontsize=10)

# 2. Флуктуация
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_title('Флуктуация (встреча)', color='white', fontsize=10)

# 3. Рождение массы
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_title('Масса > 0 (протон)', color='white', fontsize=10)

# 4. Заряд и магнитный момент
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_title('Заряд (∇·E) и магнитный момент (∇×B)', color='white', fontsize=10)

# 5. Спин (волна)
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_title('Спин (циркуляция) — волна', color='white', fontsize=10)

# 6. Итоговая структура (протий)
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_title('Баланс: протий (e⁻ + p⁺)', color='white', fontsize=10)

# Настройка всех осей
for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
    ax.set_facecolor('#111111')
    ax.tick_params(colors='white', labelsize=6)
    for spine in ax.spines.values():
        spine.set_color('#333333')

# =============================================================================
# 5. АНИМАЦИЯ
# =============================================================================

field = create_chaotic_field()
x0, y0 = GRID_SIZE//2, GRID_SIZE//2  # центр флуктуации

def update(frame):
    # Обновление полей
    new_field, mass, charge, magnetic, spin = particle_birth(field, x0, y0, frame)
    
    # 1. Нулевая энергия
    ax1.clear()
    ax1.set_facecolor('#111111')
    ax1.imshow(field, cmap='gray', origin='lower', vmin=-1, vmax=1)
    ax1.set_title('Нулевая энергия (потенциал)', color='white', fontsize=10)
    ax1.tick_params(colors='white', labelsize=6)
    
    # 2. Флуктуация
    ax2.clear()
    ax2.set_facecolor('#111111')
    ax2.imshow(new_field, cmap='inferno', origin='lower')
    ax2.set_title('Флуктуация (встреча)', color='white', fontsize=10)
    ax2.tick_params(colors='white', labelsize=6)
    
    # 3. Масса
    ax3.clear()
    ax3.set_facecolor('#111111')
    ax3.imshow(mass, cmap='hot', origin='lower', vmin=0, vmax=0.3)
    ax3.set_title('Масса > 0 (протон)', color='white', fontsize=10)
    ax3.tick_params(colors='white', labelsize=6)
    
    # 4. Заряд и магнитный момент
    ax4.clear()
    ax4.set_facecolor('#111111')
    # Показываем заряд как цвет, магнитный момент как линии
    ax4.imshow(charge, cmap='coolwarm', origin='lower', alpha=0.7)
    # Линии магнитного поля (градиент)
    y, x = np.meshgrid(np.arange(0, GRID_SIZE, 5), np.arange(0, GRID_SIZE, 5))
    u = magnetic[::5, ::5]
    v = charge[::5, ::5]
    ax4.quiver(x, y, u, v, color='white', alpha=0.3, scale=3)
    ax4.set_title('Заряд (∇·E) и магнитный момент (∇×B)', color='white', fontsize=10)
    ax4.tick_params(colors='white', labelsize=6)
    
    # 5. Спин
    ax5.clear()
    ax5.set_facecolor('#111111')
    ax5.imshow(np.abs(spin), cmap='plasma', origin='lower')
    ax5.set_title('Спин (циркуляция) — волна', color='white', fontsize=10)
    ax5.tick_params(colors='white', labelsize=6)
    
    # 6. Баланс протия
    ax6.clear()
    ax6.set_facecolor('#111111')
    # Протон (масса + заряд) + электрон (спин + волна)
    proton = mass * (1 + 0.5 * charge)
    electron = np.abs(spin) * 0.5
    combined = proton + electron
    ax6.imshow(combined, cmap='viridis', origin='lower')
    ax6.set_title('Баланс: протий (e⁻ + p⁺)', color='white', fontsize=10)
    ax6.tick_params(colors='white', labelsize=6)
    
    # Добавим аннотацию о состоянии
    if frame == 0:
        status = 'Начало: флуктуация'
    elif frame < 30:
        status = 'Встреча: рождение массы'
    elif frame < 60:
        status = 'Формирование: заряд и спин'
    else:
        status = 'Баланс: протий'
    
    fig.text(0.5, 0.02, f'Состояние: {status} | Шаг: {frame}',
             ha='center', color='cyan', fontsize=10)
    
    return []

# Создание анимации
anim = FuncAnimation(fig, update, frames=100, interval=100, blit=False)

# Сохранение
plt.show()

# Вывод информации
print("\n" + "=" * 70)
print("ETVP: Рождение частицы из нулевой энергии")
print("=" * 70)
print("На визуализации:")
print("1. Нулевая энергия — поле с максимальным хаосом и абсолютным потенциалом.")
print("2. Флуктуация — локальное возмущение, встреча двух 'порций' энергии.")
print("3. Масса — возникает в точке столкновения (протон).")
print("4. Заряд и магнитный момент — появляются из градиента поля.")
print("5. Спин — циркуляция поля, порождает волну (электрон).")
print("6. Протий — баланс протона и электрона, нейтрон как связанное состояние.")
print("=" * 70)
