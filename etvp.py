import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Circle
import matplotlib.gridspec as gridspec

# Настройка стиля
plt.style.use('dark_background')
fig = plt.figure(figsize=(20, 12), facecolor='black')
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)

# Создание осей
ax_main = fig.add_subplot(gs[0, :])  # Главная панель - пространство
ax_spectral = fig.add_subplot(gs[1, 0])  # Спектральная динамика
ax_energy = fig.add_subplot(gs[1, 1])  # Энергетический ландшафт
ax_params = fig.add_subplot(gs[1, 2])  # Параметры

# Золотое сечение
PHI = (1 + np.sqrt(5)) / 2

# Создание неэрмитовой матрицы M (11x11)
def create_matrix_M(C, S, t):
    """Создает неэрмитову матрицу M с параметрами когерентности C и энтропии S"""
    np.random.seed(42)
    
    # Базовая эрмитова часть
    H = np.zeros((11, 11), dtype=complex)
    
    # Заполнение матрицы с золотым сечением
    for i in range(11):
        for j in range(11):
            if i == j:
                H[i, j] = PHI ** (i - 5) * C
            elif abs(i - j) == 1:
                H[i, j] = 0.3 * np.exp(-S * abs(i - j))
            elif abs(i - j) == 2:
                H[i, j] = 0.15 * np.exp(-S * abs(i - j) / PHI)
    
    # Неэрмитова часть (диссипация)
    Gamma = np.zeros((11, 11), dtype=complex)
    for i in range(11):
        for j in range(11):
            if i > j:
                Gamma[i, j] = 0.1j * np.exp(-S * (i - j)) * np.sin(t)
    
    M = H + Gamma
    return M

# Функция для вычисления спектральных характеристик
def compute_spectral_properties(M):
    """Вычисляет все спектральные характеристики матрицы"""
    eigenvalues = np.linalg.eigvals(M)
    eigenvalues_sorted = eigenvalues[np.argsort(np.abs(eigenvalues))[::-1]]
    
    # Эмерджентное время
    dt = np.imag(eigenvalues_sorted[10] / eigenvalues_sorted[0])
    
    # Эффективная метрика (след M†M)
    metric_trace = np.real(np.trace(M.conj().T @ M))
    
    # Кривизна (спектральная дисперсия)
    curvature = np.real(np.trace(M @ M)) - np.real(np.trace(M))**2
    
    # Гравитационная постоянная
    G_eff = np.real(eigenvalues_sorted[0] / (eigenvalues_sorted[9] * eigenvalues_sorted[8])) / (PHI**20 * 1e7)
    
    # Постоянная тонкой структуры
    alpha_inv = np.real(eigenvalues_sorted[0] / eigenvalues_sorted[10]) * PHI**(-2)
    
    return {
        'eigenvalues': eigenvalues_sorted,
        'dt': dt,
        'metric_trace': metric_trace,
        'curvature': curvature,
        'G_eff': G_eff,
        'alpha_inv': alpha_inv
    }

# Функция для визуализации пространства нулевой энергии
def visualize_zero_energy_space(ax, spectral_props, t, fluctuation_phase):
    """Визуализация пространства через спектральную геометрию"""
    ax.clear()
    
    # Создание координатной сетки
    grid_size = 150
    x = np.linspace(-8, 8, grid_size)
    y = np.linspace(-8, 8, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Использование метрики для создания геометрии
    metric_trace = spectral_props['metric_trace']
    curvature = spectral_props['curvature']
    
    # Создание поля на основе спектральных свойств
    eigenvalues = spectral_props['eigenvalues']
    
    # Базовое поле (нулевая энергия)
    field = np.zeros((grid_size, grid_size))
    
    # Добавление спектральных мод
    for n in range(min(5, len(eigenvalues))):
        kx = n * 0.5 + 0.3
        ky = (n % 3) * 0.7 + 0.2
        amplitude = np.abs(eigenvalues[n]) * 0.1
        phase = np.angle(eigenvalues[n])
        field += amplitude * np.cos(kx * X + ky * Y + phase + t * np.abs(eigenvalues[n]))
    
    # Добавление флуктуации (столкновение квантов)
    fluctuation_center = (0, 0)
    dist = np.sqrt((X - fluctuation_center[0])**2 + (Y - fluctuation_center[1])**2)
    fluctuation = fluctuation_phase * np.exp(-dist**2 / 1.5) * np.cos(t * 3)
    field += fluctuation
    
    # Нормализация
    field = (field - field.min()) / (field.max() - field.min())
    
    # Визуализация
    cmap = LinearSegmentedColormap.from_list('spectral', 
        ['#0a0a2e', '#1a1a4e', '#2a2a6e', '#3a3a8e', '#5a5aae', '#7a7ace', '#9a9aee'], N=256)
    
    im = ax.imshow(field, extent=[-8, 8, -8, 8], cmap=cmap, 
                   interpolation='bilinear', aspect='auto', alpha=0.9)
    
    # Добавление контуров равной энергии
    contours = ax.contour(X, Y, field, levels=8, colors='white', alpha=0.3, linewidths=0.5)
    
    # Визуализация точки массы в центре флуктуации
    if fluctuation_phase > 0.3:
        mass_radius = 0.2 + fluctuation_phase * 0.3
        mass_circle = Circle((0, 0), mass_radius, color='red', alpha=0.8)
        ax.add_patch(mass_circle)
        
        # Заряд
        charge_circle = Circle((0, 0), mass_radius + 0.15, 
                              color='yellow', alpha=0.5, fill=False, linewidth=2)
        ax.add_patch(charge_circle)
    
    # Подписи
    ax.set_title(f'Пространство нулевой энергии\nМетрика: {metric_trace:.3f}, Кривизна: {curvature:.3f}', 
                color='white', fontsize=11, pad=20)
    ax.set_xlabel('X (спектральная координата)', color='white', fontsize=9)
    ax.set_ylabel('Y (спектральная координата)', color='white', fontsize=9)
    ax.set_facecolor('#050520')
    ax.grid(True, alpha=0.2, color='cyan')
    
    return im

# Функция для визуализации спектра
def visualize_spectrum(ax, spectral_props):
    """Визуализация спектра матрицы M"""
    ax.clear()
    
    eigenvalues = spectral_props['eigenvalues']
    
    # Комплексная плоскость
    theta = np.linspace(0, 2*np.pi, 100)
    unit_circle = np.exp(1j * theta)
    ax.plot(unit_circle.real, unit_circle.imag, 'w--', alpha=0.3, linewidth=0.5)
    
    # Собственные значения
    for n, ev in enumerate(eigenvalues):
        color = plt.cm.plasma(n / 11)
        ax.scatter(ev.real, ev.imag, c=[color], s=100, alpha=0.8, 
                  edgecolors='white', linewidth=1)
        ax.annotate(f'λ{n+1}', (ev.real, ev.imag), color='white', 
                   fontsize=8, xytext=(5, 5), textcoords='offset points')
    
    # Выделение особых значений
    ax.scatter(eigenvalues[0].real, eigenvalues[0].imag, c='red', s=150, 
              marker='*', edgecolors='gold', linewidth=2, label='λ1 (максимум)')
    ax.scatter(eigenvalues[10].real, eigenvalues[10].imag, c='cyan', s=150, 
              marker='*', edgecolors='white', linewidth=2, label='λ11 (минимум)')
    
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.set_title('Спектр матрицы M (11×11)\nНеэрмитова динамика', color='white', fontsize=11)
    ax.set_xlabel('Re(λ)', color='white')
    ax.set_ylabel('Im(λ)', color='white')
    ax.legend(loc='upper right', fontsize=8)
    ax.set_facecolor('#050520')
    ax.grid(True, alpha=0.3)
    
# Функция для визуализации энергетического ландшафта
def visualize_energy_landscape(ax, spectral_props, t):
    """Визуализация энергетического ландшафта"""
    ax.clear()
    
    # Энергетические уровни
    energy_levels = np.abs(spectral_props['eigenvalues'])
    
    # Создание потенциальной ямы
    x = np.linspace(-5, 5, 200)
    V = x**2 * 0.5  # гармонический потенциал
    
    # Добавление спектральных уровней
    ax.plot(x, V, 'w-', linewidth=2, alpha=0.7, label='Потенциал')
    ax.fill_between(x, V, alpha=0.2, color='blue')
    
    # Уровни энергии
    for n, E in enumerate(energy_levels[:5]):
        ax.hlines(E, -np.sqrt(2*E), np.sqrt(2*E), 
                 colors=plt.cm.plasma(n/5), linewidth=2, alpha=0.7)
        ax.text(-np.sqrt(2*E), E + 0.1, f'E{n+1}={E:.2f}', 
               color='white', fontsize=8)
    
    # Волновая функция основного состояния
    psi = np.exp(-x**2/2) / np.pi**0.25
    ax.plot(x, psi * 2 + energy_levels[0], 'g-', linewidth=2, 
           alpha=0.6, label='Ψ (осн. сост.)')
    
    ax.set_title('Энергетический ландшафт\nКвантованные уровни из спектра', color='white', fontsize=11)
    ax.set_xlabel('Координата', color='white')
    ax.set_ylabel('Энергия', color='white')
    ax.set_facecolor('#050520')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_ylim(0, np.max(energy_levels) * 1.5)

# Функция для отображения параметров
def visualize_parameters(ax, spectral_props, t, phase):
    """Отображение вычисленных физических параметров"""
    ax.clear()
    ax.axis('off')
    
    # Вычисление параметров
    alpha_inv = spectral_props['alpha_inv']
    G_eff = spectral_props['G_eff']
    dt = spectral_props['dt']
    curvature = spectral_props['curvature']
    
    # Отображение параметров
    params = [
        ('Постоянная тонкой структуры', f'α⁻¹ = {alpha_inv:.3f}'),
        ('Гравитационная постоянная', f'G = {G_eff:.2e}'),
        ('Эмерджентное время', f'dt = {dt:.3f}'),
        ('Кривизна пространства', f'R = {curvature:.3f}'),
        ('Золотое сечение', f'Φ = {PHI:.6f}'),
        ('Фаза флуктуации', f'φ = {phase:.2f}'),
        ('Когерентность', f'C = {0.5 + 0.5*np.sin(t):.3f}'),
        ('Энтропия', f'S = {0.3 + 0.2*np.cos(t*0.7):.3f}'),
    ]
    
    y_pos = 0.95
    ax.text(0.5, y_pos, 'ФИЗИЧЕСКИЕ ПАРАМЕТРЫ', 
           color='gold', ha='center', fontsize=11, weight='bold', transform=ax.transAxes)
    y_pos -= 0.08
    
    for name, value in params:
        ax.text(0.05, y_pos, f'{name}:', color='cyan', fontsize=9, transform=ax.transAxes)
        ax.text(0.95, y_pos, value, color='white', ha='right', fontsize=9, transform=ax.transAxes)
        y_pos -= 0.09
    
    # Визуализация матрицы M
    ax.text(0.5, 0.15, 'Матрица M (неэрмитова):', 
           color='gold', ha='center', fontsize=9, transform=ax.transAxes)
    
    M = create_matrix_M(0.7, 0.3, t)
    M_display = np.abs(M)
    ax.imshow(M_display, extent=[0.1, 0.9, 0.05, 0.12], 
             cmap='plasma', aspect='auto', alpha=0.7)
    
    ax.set_facecolor('#050520')

# Анимация
total_frames = 300

def animate(frame):
    t = frame * 0.1
    
    # Параметры когерентности и энтропии (осциллирующие)
    C = 0.5 + 0.5 * np.sin(t * 0.7)
    S = 0.3 + 0.2 * np.cos(t * 0.5)
    
    # Создание матрицы M
    M = create_matrix_M(C, S, t)
    
    # Вычисление спектральных свойств
    spectral_props = compute_spectral_properties(M)
    
    # Фаза флуктуации (столкновение квантов)
    if frame < 100:
        # Нарастание флуктуации
        fluctuation_phase = frame / 100
    elif frame < 200:
        # Поддержание
        fluctuation_phase = 1.0
    else:
        # Затухание
        fluctuation_phase = 1.0 - (frame - 200) / 100
    
    # Визуализация
    im = visualize_zero_energy_space(ax_main, spectral_props, t, fluctuation_phase)
    visualize_spectrum(ax_spectral, spectral_props)
    visualize_energy_landscape(ax_energy, spectral_props, t)
    visualize_parameters(ax_params, spectral_props, t, fluctuation_phase)
    
    # Добавление аннотаций
    if fluctuation_phase > 0.8:
        ax_main.text(0, -7, '⚡ ФЛУКТУАЦИЯ: Рождение частицы из нулевой энергии', 
                    color='red', ha='center', fontsize=11, weight='bold',
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
    
    return [im]

# Создание анимации
ani = FuncAnimation(fig, animate, frames=total_frames, interval=50, blit=False)

# Сохранение
ani.save('etvp_quantum_visualization.gif', writer=PillowWriter(fps=20), dpi=100)
plt.show()

print("Визуализация ETVP 12.5 создана и сохранена как 'etvp_quantum_visualization.gif'")
print("\nКлючевые аспекты визуализации:")
print("1. Пространство нулевой энергии через спектральную геометрию")
print("2. Неэрмитова матрица M (11×11) как источник всех параметров")
print("3. Флуктуация как столкновение квантов в спектральном пространстве")
print("4. Эмерджентное время из мнимых частей собственных значений")
print("5. Рождение частицы из точки массы в центре флуктуации")
print("6. Квантованные энергетические уровни из спектра")
print("7. Вычисление фундаментальных постоянных из спектральных отношений")
