import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# =============================================================================
# 1. ПАРАМЕТРЫ СРЕДЫ (МАТРИЦА 11D ВАКУУМА)
# =============================================================================
GRID_SIZE = 80
L_FIELD = 40.0
DT = 0.1

# Базовые геометрические аттракторы из вашего трактата
PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI = np.pi
SQRT3 = np.sqrt(3.0)

# Массы из Группы I (в относительных масштабах для симулятора)
M_E = (2**12 - SQRT3**4 * PI**3) / (PHI**20 * 2 * PI**2 + PI**5) * 40.0 # ~0.511
M_P = M_E * 1836.1526  # Протон тяжелее электрона в 1836 раз

# =============================================================================
# 2. ИНИЦИАЛИЗАЦИЯ СКРЫТОГО ПОРЯДКА (МОРЕ ФЕРМИ)
# =============================================================================
x = np.linspace(-L_FIELD, L_FIELD, GRID_SIZE)
y = np.linspace(-L_FIELD, L_FIELD, GRID_SIZE)
X, Y = np.meshgrid(x, y)

# Координаты частиц фонового вакуума
vacuum_x = X.flatten()
vacuum_y = Y.flatten()
vac_pos_init = np.stack([vacuum_x, vacuum_y], axis=1)
vac_pos = vac_pos_init.copy()
vac_vel = np.zeros_like(vac_pos)

# Позиции новорожденных частиц (появятся на кадре 100)
proton_pos = np.array([0.0, 0.0])
electron_pos = np.array([0.0, 0.0])
electron_vel = np.array([0.0, 0.0])

# =============================================================================
# 3. ГРАФИКА НАБЛЮДАТЕЛЯ
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 10), facecolor='#09090b')
ax.set_facecolor('#09090b')

# Отрисовка ткани вакуума
vac_dots = ax.scatter(vac_pos[:, 0], vac_pos[:, 1], c='#1e1b4b', s=10, alpha=0.5, label='Ткань вакуума (Море Ферми)')
vac_tension = ax.scatter([], [], c=[], s=20, cmap='plasma', alpha=0.8, vmin=0, vmax=8)

# Элементы протия (пока скрыты)
proton_dot = ax.scatter([], [], c='#ef4444', s=250, edgecolors='white', zorder=5, label='Протон ($p^+$)')
electron_dot = ax.scatter([], [], c='#06b6d4', s=50, edgecolors='white', zorder=5, label='Электрон ($e^-$)')
electron_trail, = ax.plot([], [], c='#06b6d4', alpha=0.4, linewidth=1.5)

# Индикаторы
title_text = ax.text(0.5, 0.95, '', transform=ax.transAxes, color='white', fontsize=12, ha='center', weight='bold')
metrics_text = ax.text(0.02, 0.02, '', transform=ax.transAxes, color='#94a3b8', fontsize=10, family='monospace')

ax.set_xlim(-L_FIELD, L_FIELD)
ax.set_ylim(-L_FIELD, L_FIELD)
ax.axis('off')
ax.legend(loc='upper left', facecolor='#18181b', edgecolor='#27272a', labelcolor='white')

trail_history = []

# =============================================================================
# 4. ДИНАМИЧЕСКИЙ ДВИЖОК СЖАТИЯ И РОЖДЕНИЯ
# =============================================================================
def update(frame):
    global vac_pos, vac_vel, proton_pos, electron_pos, electron_vel, trail_history
    
    # Считаем текущую локальную плотность и упругость в центре
    dist_to_center = np.linalg.norm(vac_pos, axis=1)
    
    # -------------------------------------------------------------------------
    # СТАДИЯ 1: Нулевая энергия и скрытые флуктуации (Кадры 0 - 40)
    # -------------------------------------------------------------------------
    if frame < 40:
        title_text.set_text("СТАДИЯ 1: Скрытый порядок вакуума (Флуктуации плазмы, масса = 0)")
        # Легкое квантовое «дыхание» среды без изменения структуры
        vac_pos = vac_pos_init + np.random.normal(0, 0.1, vac_pos.shape)
        current_tension = np.zeros(len(vac_pos))
        
    # -------------------------------------------------------------------------
    # СТАДИЯ 2: Повышение локальной плотности и упругости (Кадры 40 - 100)
    # -------------------------------------------------------------------------
    elif frame >= 40 and frame < 100:
        title_text.set_text("СТАДИЯ 2: Нарастание локальной упругости и плотности вакуума")
        
        # Сила уплотнения вакуума к центру (нарастает со временем)
        compression_factor = (frame - 40) / 60.0 * 2.5
        
        # Направляем импульс частиц вакуума строго к центру, сжимая решетку
        direction_to_center = -vac_pos / np.maximum(dist_to_center[:, None], 1.0)
        # Сжатие по закону Гаусса (сильнее всего в центре)
        force_profile = np.exp(-dist_to_center**2 / (2 * 12.0**2))[:, None]
        
        vac_vel += direction_to_center * force_profile * compression_factor * DT
        
        # Сила упругости самого вакуума, пытающаяся вернуть порядок (Z-принцип удержания)
        vac_return = -(vac_pos - vac_pos_init) * 0.4
        vac_vel += vac_return * DT
        
        # Нелинейный ограничитель демпфирования по вашему трактату (etve_tanh_limit)
        vac_vel = np.tanh(vac_vel * 0.8)
        vac_pos += vac_vel
        
    # -------------------------------------------------------------------------
    # СТАДИЯ 3: Пробой предела упругости и Рождение Протия (Кадры 100+)
    # -------------------------------------------------------------------------
    else:
        title_text.set_text("СТАДИЯ 3: Материализация Протия. Удержание упругостью сжатого пузыря")
        
        # В момент пробоя (кадр 100) инициализируем систему протия
        if frame == 100:
            proton_pos = np.array([0.0, 0.0])
            # Электрон выбрасывается центробежным вихрем (трением) на границу сжатия
            electron_pos = np.array([8.0, 0.0])
            # Начальный импульс электрона для закрутки спина
            electron_vel = np.array([0.0, 4.5])
            
            # Вакуум испытывает обратную «ударную волну» из центра наружу
            shock_dir = vac_pos / np.maximum(dist_to_center[:, None], 1.0)
            shock_force = np.exp(-dist_to_center**2 / (2 * 6.0**2))[:, None]
            vac_vel += shock_dir * shock_force * 8.0
            
        # Взаимодействие Протона и Электрона
        r_vec = electron_pos - proton_pos
        r_dist = np.linalg.norm(r_vec)
        r_dir = r_vec / np.maximum(r_dist, 1.0)
        
        # Внутреннее кулоновское притяжение
        f_internal = 20.0 / (r_dist**2)
        electron_acc = -r_dir * f_internal / (M_E * 0.1) # нормировано на геометрию массы электрона
        
        # Главное: Упругое давление сжатого вакуумного пузыря снаружи!
        # Среда вокруг центра стала плотнее, она не пускает электрон наружу
        if r_dist > 9.0:
            elastic_vacuum_push = (r_dist - 9.0) * 1.5
            electron_acc += -r_dir * elastic_vacuum_push
            
        electron_vel += electron_acc * DT
        electron_pos += electron_vel * DT
        
        trail_history.append(electron_pos.copy())
        if len(trail_history) > 30:
            trail_history.pop(0)
            
        # Влияние родившихся частиц на ткань Моря Ферми
        # Протон удерживает вакуум вокруг себя, электрон — расталкивает
        diff_p = vac_pos - proton_pos
        dist_p = np.linalg.norm(diff_p, axis=1, keepdims=True)
        vac_vel += -(diff_p / np.maximum(dist_p, 1.0)) * (5.0 / (dist_p**2 + 2.0)) * DT
        
        diff_e = vac_pos - electron_pos
        dist_e = np.linalg.norm(diff_e, axis=1, keepdims=True)
        vac_vel += (diff_e / np.maximum(dist_e, 1.0)) * (2.0 / (dist_e**2 + 1.0)) * DT
        
        # Возврат к порядку + демпфирование
        vac_return = -(vac_pos - vac_pos_init) * 0.3
        vac_vel += vac_return * DT
        vac_vel *= 0.93
        vac_pos += vac_vel

    # =============================================================================
    # 5. СБОР МЕТРИК И ОТРИСОВКА КАДРА
    # =============================================================================
    # Рассчитываем текущее локальное смещение (натяжение/плотность) для цвета
    displacements = np.linalg.norm(vac_pos - vac_pos_init, axis=1)
    
    # Обновляем позиции точек вакуума
    vac_dots.set_offsets(vac_pos)
    
    # Подсвечиваем зоны экстремального сжатия и упругости
    vac_tension.set_offsets(vac_pos)
    vac_tension.set_array(displacements)
    
    if frame >= 100:
        proton_dot.set_offsets(proton_pos)
        electron_dot.set_offsets(electron_pos)
        
        pts = np.array(trail_history)
        electron_trail.set_data(pts[:, 0], pts[:, 1])
        
        # Вывод параметров из Группы I в реальном времени
        r_orbit = np.linalg.norm(electron_pos - proton_pos)
        metrics_text.set_text(
            f"МЕТРИКИ ПОЛЯ (ЕТВП 12.5):\n"
            f"─ Базисная масса m_e: {M_E:.5f} MeV\n"
            f"─ Пропорция масс m_p/m_e: {M_P/M_E:.2f}\n"
            f"─ Локальное натяжение вакуума: {np.max(displacements):.2f}\n"
            f"─ Радиус когерентной орбиты: {r_orbit:.2f}"
        )
    else:
        metrics_text.set_text(
            f"МЕТРИКИ ПОЛЯ:\n"
            f"─ Вакуум в режиме плазмы\n"
            f"─ Плотность в центре: {1.0 + np.max(displacements)*0.1:.2f}\n"
            f"─ Заряд и Масса: 0.000"
        )
        
    return vac_dots, vac_tension, proton_dot, electron_dot, electron_trail

# Сборка анимации
ani = FuncAnimation(fig, update, frames=240, interval=40, blit=False)
plt.show()
