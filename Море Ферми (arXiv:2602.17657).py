import numpy as np
import matplotlib.pyplot as plt

# Инициализация параметров по данным arXiv:2602.17657 и ядра ETVE v12.4 FFS
GLOBAL_PHI = (1.0 + np.sqrt(5.0)) / 2.0
C_FFS = 0.87          # Порог когерентности для дробного состояния из вашего ядра
GLOBAL_C_TARGET = 1.0 - 1.0 / (GLOBAL_PHI ** 12)
EPSILON_FFS = 0.01

class FractionalFermiSeaSimulation:
    def __init__(self, num_atoms=70000, alpha=2):
        self.num_atoms = num_atoms
        self.alpha = alpha  # Параметр дробной статистики (уровень занятости)
        self.C = GLOBAL_C_TARGET
        self.S = 0.12       # Стартовая энтропия цикла взаимодействий
        
    def simulate_holonomy_cycle(self, steps=200):
        """Моделирует циклическое переключение отталкивания-притяжения."""
        c_history = []
        entropy_history = []
        friedel_amplitudes = []
        
        # Симулируем 4 полных цикла накачки
        for t in range(steps):
            # Внешний поток взаимодействия (периодическое сильное сжатие/растяжение)
            interaction_ramp = np.sin(2 * np.pi * t / 50)
            
            # Эволюция когерентности поля под воздействием знакопеременного потока
            # В фазе сильного отталкивания/притяжения поле стремится к упорядоченности C_FFS
            chaos_operator = 1.0 / (1.0 + abs(interaction_ramp) * (1.0 / GLOBAL_PHI))
            self.C = self.C * chaos_operator + (1.0 - chaos_operator) * C_FFS
            
            # Эффект демпфирования (Z-Принцип из v12.4 предотвращает тепловой коллапс)
            self.C = np.tanh(self.C) * 0.13 + 0.85 
            
            # Изменение энтропии: проседает в моменты квантового упорядочения
            self.S = 0.12 + 0.05 * np.cos(4 * np.pi * t / 50) * (1.0 - self.C)
            
            c_history.append(self.C)
            entropy_history.append(self.S)
            
            # Амплитуда формирования осцилляций Фриделя растет при приближении C к C_FFS
            friedel_amp = np.exp(-abs(self.C - C_FFS) / EPSILON_FFS)
            friedel_amplitudes.append(friedel_amp)
            
        return np.array(c_history), np.array(entropy_history), np.array(friedel_amplitudes)

    def calculate_correlation_function(self, r, current_c):
        """Вычисляет пространственные корреляции первого порядка g1(r)."""
        # Импульс Ферми для 1D трубки
        k_F = np.pi * 0.5 
        
        # Классическое затухание Томонаги-Луттинджера для стабильной жидкости
        tll_decay = 1.0 / (r**0.5 + 1e-12)
        
        # Вклад дробных мод Ферми (возбужденное волновое состояние с частотой, сдвинутой на альфа)
        # Проявляется при когерентности близкой к C_FFS
        ffs_coherence = np.exp(-abs(current_c - C_FFS) / EPSILON_FFS)
        
        # Фриделевские «ряби» (Friedel Ripples) на дробной частоте
        friedel_oscillations = np.cos(2 * k_F * r / self.alpha) * ffs_coherence * 0.4
        
        # Итоговая функция корреляции
        g1_r = tll_decay * (1.0 + friedel_oscillations)
        return g1_r

# --- ЗАПУСК МОДЕЛИРОВАНИЯ ЭКСПЕРИМЕНТА ---
sim = FractionalFermiSeaSimulation(num_atoms=70000, alpha=2)
c_hist, s_hist, f_amp_hist = sim.simulate_holonomy_cycle(steps=200)

# Пространственная сетка для измерения корреляций в нанотрубке
r_space = np.linspace(0.1, 40, 500)
g1_initial = sim.calculate_correlation_function(r_space, current_c=0.98) # Начальное тепловое состояние
g1_ffs_state = sim.calculate_correlation_function(r_space, current_c=c_hist[25]) # Состояние в пике FFS

# --- ВИЗУАЛИЗАЦИЯ И СРАВНЕНИЕ ---
<layout>
import io
import base64

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Левый график: Динамика квантового поля при циклах взаимодействия
ax1.plot(c_hist, label='Когерентность поля $C(t)$', color='purple', linewidth=2)
ax1.plot(s_hist, label='Энтропия среды $S(t)$', color='orange', linestyle='--')
ax1.axhline(C_FFS, color='red', linestyle=':', label='Порог $C_{FFS}$ (0.87)')
ax1.set_title('Динамика калибровки при циклах накачки')
ax1.set_xlabel('Шаги времени ($dt$)')
ax1.set_ylabel('Амплитуда параметров')
ax1.legend(loc='lower left')
ax1.grid(True, alpha=0.3)

# Правый график: Пространственные корреляции и осцилляции Фриделя
ax1_twin = ax1.twinx()
ax1_twin.plot(f_amp_hist, color='green', alpha=0.3, label='Амплитуда супер-мод')

ax2.plot(r_space, g1_initial, label='Равновесное состояние ($TLL$)', color='gray', alpha=0.6)
ax2.plot(r_space, g1_ffs_state, label='Дробное море Ферми ($FFS, \\alpha=2$)', color='blue', linewidth=1.5)
ax2.set_title('Парные корреляции $g_1(r)$ и рябь Фриделя')
ax2.set_xlabel('Пространственное расстояние в 1D трубке ($r$)')
ax2.set_ylabel('Амплитуда корреляции $g_1$')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()

buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight')
buf.seek(0)
base64_str = base64.b64encode(buf.read()).decode('utf-8')
plt.close()
print(f'base64_encoded_image:"data:image/png;base64,{base64_str}"')
</layout>
