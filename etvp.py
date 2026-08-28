import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# =============================================================================
# 1. НАСТРОЙКИ МОДЕЛИ
# =============================================================================
NUM_VACUUM = 800       # Количество частиц вакуума (Море Ферми)
L_FIELD = 50.0         # Размер области симуляции
DT = 0.1               # Шаг времени

# Физические параметры упругого вакуума
K_VACUUM = 0.5         # Жесткость возвращающей силы скрытого порядка (к исходным позициям)
VACUUM_DAMPING = 0.92  # Вязкость/затухание среды вакуума

# Параметры Протия
MASS_PROTON = 1836.0
MASS_ELECTRON = 1.0
G_ATTRACTION = 15.0    # Сила внутреннего притяжения p+ и e-
R_BORDER = 12.0        # Радиус упругой ячейки вакуума, удерживающей электрон

# =============================================================================
# 2. ИНИЦИАЛИЗАЦИЯ СРЕДЫ (Скрытый порядок Моря Ферми)
# =============================================================================
# Создаем квазикристаллическую (упорядоченную) сетку для частиц вакуума
n_side = int(np.sqrt(NUM_VACUUM))
x_line = np.linspace(-L_FIELD/2 + 2, L_FIELD/2 - 2, n_side)
y_line = np.linspace(-L_FIELD/2 + 2, L_FIELD/2 - 2, n_side)
X_init, Y_init = np.meshgrid(x_line, y_line)

# Исходные (равновесные) позиции скрытого порядка
vac_pos_init = np.stack([X_init.ravel(), Y_init.ravel()], axis=1)
num_vac_actual = vac_pos_init.shape[0]

# Текущие динамические переменные частиц вакуума
vac_pos = vac_pos_init.copy()
vac_vel = np.zeros_like(vac_pos)

# Инициализация Протия (изначально «скрыты» вне поля или слиты)
proton_pos = np.array([0.0, 0.0])
proton_vel = np.array([0.0, 0.0])

# Электрон вылетает из точки столкновения
electron_pos = np.array([1.0, 1.0])
electron_vel = np.array([-4.0, 5.0]) # Начальный импульс для орбиты

# Переменная стадии: 0 - Скрытый порядок, 1 - Рождение и Удержание
stage = 0
frame_birth = 40 

# =============================================================================
# 3. НАСТРОЙКА ГРАФИКИ
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 10), facecolor='#09090b')
ax.set_facecolor('#09090b')

# Отрисовка элементов
# Фоновое море Ферми (скрытый порядок) отобразим тонкими полупрозрачными точками
vac_dots = ax.scatter([], [], c='#1e1b4b', s=15, alpha=0.6, label='Море Ферми (Вакуум)')
# Деформированная зона (упругое сжатие)
vac_deformed = ax.scatter([], [], c='#6366f1', s=25, alpha=0.0)

# Частицы протия
proton_dot = ax.scatter([], [], c='#ef4444', s=300, edgecolors='white', zorder=5, label='Протон ($p^+$)')
electron_dot = ax.scatter([], [], c='#06b6d4', s=60, edgecolors='white', zorder=5, label='Электрон ($e^-$)')
electron_trail, = ax.plot([], [], c='#06b6d4', alpha=0.4, linewidth=1.5)

# Радиус упругого удержания вакуумом
vacuum_bubble = plt.Circle((0, 0), R_BORDER, color='#4338ca', fill=False, linestyle='--', alpha=0.0, linewidth=2)
ax.add_patch(vacuum_bubble)

# Текстовые индикаторы
title_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, color='white', fontsize=14, ha='center', weight='bold')
status_text = ax.text(0.02, 0.02, '', transform=ax.transAxes, color='#94a3b8', fontsize=10)

ax.set_xlim(-L_FIELD, L_FIELD)
ax.set_ylim(-L_FIELD, L_FIELD)
ax.axis('off')
ax.legend(loc='upper left', facecolor='#18181b', edgecolor='#27272a', labelcolor='white')

e_history = []

# =============================================================================
# 4. ВЫЧИСЛИТЕЛЬНЫЙ ДВИЖОК СИМУЛЯЦИИ
# =============================================================================
def update(frame):
    global vac_pos, vac_vel, proton_pos, proton_vel, electron_pos, electron_vel, stage, e_history
    
    # Смена стадий симуляции
    if frame < frame_birth:
        stage = 0
        title_text.set_text('Стадия 1: Скрытый порядок Моря Ферми (Вакуум покоится)')
        # Легкие квантовые колебания вакуума в покое
        vac_pos = vac_pos_init + np.random.normal(0, 0.15, vac_pos.shape)
    else:
        if stage == 0:
            stage = 1
            # Эффект квантового взрыва/рождения в центре
            vac_vel += np.random.normal(0, 2.0, vac_pos.shape)
        title_text.set_text('Стадия 2: Рождение Протия и Удержание Упругостью Вакуума')

    if stage == 1:
        # 1. Взаимодействие внутри Протия (Кулоновское/Гравитационное притяжение)
        r_vector = electron_pos - proton_pos
        distance = np.linalg.norm(r_vector)
        if distance < 1.0: distance = 1.0 # Защита от деления на ноль
        
        force_dir = r_vector / distance
        f_attraction = G_ATTRACTION / (distance**2)
        
        # Ускорения компонентов атома
        proton_acc = (force_dir * f_attraction) / MASS_PROTON
        electron_acc = (-force_dir * f_attraction) / MASS_ELECTRON
        
        # 2. Упругое давление вакуума (Скрытый порядок пытается вернуть электрон назад)
        # Если электрон пытается вырваться за границы «пузыря» вакуума
        if distance > R_BORDER:
            # Вакуум давит в сторону протона, упруго возвращая электрон
            elastic_k = 0.8
            electron_acc += -force_dir * elastic_k * (distance - R_BORDER)
            vacuum_bubble.set_alpha(0.7) # Подсвечиваем границу натяжения вакуума
            vacuum_bubble.set_edgecolor('#ec4899')
        else:
            vacuum_bubble.set_alpha(0.2)
            vacuum_bubble.set_edgecolor('#4338ca')

        # Обновление скоростей и позиций Протия
        proton_vel += proton_acc * DT
        proton_pos += proton_vel * DT
        
        electron_vel += electron_acc * DT
        electron_pos += electron_vel * DT
        
        e_history.append(electron_pos.copy())
        if len(e_history) > 40: e_history.pop(0)

        # 3. Влияние Протия на Море Ферми (Деформация порядка)
        # Протон притягивает к себе ткань вакуума, а электрон расталкивает
        for i, pos in enumerate([proton_pos, electron_pos]):
            diff = vac_pos - pos
            dist_vac = np.linalg.norm(diff, axis=1, keepdims=True)
            dist_vac = np.maximum(dist_vac, 2.0)
            
            # Протон (заряд +) стягивает вакуум, Электрон (-) — расталкивает кольцом
            charge = -8.0 if i == 0 else 4.0
            vac_vel += (diff / dist_vac) * (charge / (dist_vac**2)) * DT

        # 4. Сила упругости самого вакуума (возврат к скрытому порядку)
        # Каждая точка вакуума привязана упругой пружиной к своей идеальной позиции
        vac_return_force = -(vac_pos - vac_pos_init) * K_VACUUM
        vac_vel += vac_return_force * DT
        
        # Трение/вязкость среды, чтобы колебания были стабильными
        vac_vel *= VACUUM_DAMPING
        vac_pos += vac_vel * DT

    # =============================================================================
    # 5. ОБНОВЛЕНИЕ КАДРА
    # =============================================================================
    vac_dots.set_offsets(vac_pos)
    
    # Цветовая индикация деформации вакуума (сильнее сдвиг — ярче цвет)
    displacements = np.linalg.norm(vac_pos - vac_pos_init, axis=1)
    colors = np.zeros((num_vac_actual, 4))
    colors[:, 0] = 0.4   # R
    colors[:, 1] = 0.7   # G
    colors[:, 2] = 1.0   # B
    colors[:, 3] = np.clip(displacements * 0.4, 0.0, 1.0) # Альфа зависит от натяжения ткани
    vac_deformed.set_offsets(vac_pos)
    vac_deformed.set_color(colors)

    if stage == 1:
        proton_dot.set_offsets(proton_pos)
        electron_dot.set_offsets(electron_pos)
        
        trail_pts = np.array(e_history)
        electron_trail.set_data(trail_pts[:, 0], trail_pts[:, 1])
        
        vacuum_bubble.center = proton_pos
        status_text.set_text(f"Статус: Атом стабилен\nСмещение ткани вакуума: {np.max(displacements):.2f}\nРадиус орбиты e-: {np.linalg.norm(electron_pos-proton_pos):.2f}")
    else:
        status_text.set_text("Статус: Накопление потенциала энергии вакуума...")

    return vac_dots, vac_deformed, proton_dot, electron_dot, electron_trail, vacuum_bubble

# Запуск анимации
ani = FuncAnimation(fig, update, frames=300, interval=30, blit=False)
plt.show()
