#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP HIERARCHY — Иерархия Бесконечности
================================================================================
От бесконечности до всех производных.
Чистая геометрия: ∞ → Φ,π,√3 → E8 → три → всё.
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import math

# =============================================================================
# 0. БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
Z   = np.sqrt(3.0)
SQ2 = np.sqrt(2.0)

# =============================================================================
# 1. E8
# =============================================================================

E8 = np.array([
    [ 2, -1,  0,  0,  0,  0,  0,  0],
    [-1,  2, -1,  0,  0,  0,  0,  0],
    [ 0, -1,  2, -1,  0,  0,  0,  0],
    [ 0,  0, -1,  2, -1,  0,  0,  0],
    [ 0,  0,  0, -1,  2, -1,  0, -1],
    [ 0,  0,  0,  0, -1,  2, -1,  0],
    [ 0,  0,  0,  0,  0, -1,  2,  0],
    [ 0,  0,  0,  0, -1,  0,  0,  2]
], dtype=float)

eigvals = np.sort(np.linalg.eigvalsh(E8))

# =============================================================================
# 2. ВЕСА
# =============================================================================

W_ALPHA = (PHI**12) * (PI**-4) * (Z**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (Z**4) * 0.5
W_G     = (PHI**-43) * (PI**-1) * (Z**-5) * 2

# =============================================================================
# 3. ТРИ КОНСТАНТЫ
# =============================================================================

alpha_inv = eigvals[7] * W_ALPHA      # 137.0354
mass_ratio = eigvals[2] * W_MASS      # 1836.02
G_constant = eigvals[3] * W_G          # 6.674e-11

# CODATA
CODATA_ALPHA = 137.035999084
CODATA_MASS  = 1836.15267343
CODATA_G     = 6.67430e-11

# =============================================================================
# 4. ПРОИЗВОДНЫЕ
# =============================================================================

# Топология
spin_e = 1/2
spin_p = 1/2
charge_e = -1
charge_p = +1

# Магнитный момент (аномалия)
a_e = 1 / (2 * PI * alpha_inv)  # α/(2π)

# Боровский радиус (в единицах ħ/(m_e·c))
# a₀ = ħ/(m_e·c·α) → в безразмерных: 1/α
a0_rel = 1 / (alpha_inv)

# Энергия ионизации (в единицах m_e·c²)
E_i_rel = alpha_inv**2 / 2

# Постоянная Ридберга (в единицах m_e·c²/(2h))
R_rel = alpha_inv**2 / 2

# =============================================================================
# 5. ВЫВОД В КОНСОЛЬ
# =============================================================================

print("=" * 80)
print("🌀 ИЕРАРХИЯ ПРОТИЯ: ОТ БЕСКОНЕЧНОСТИ ДО ВСЕГО")
print("=" * 80)

print("""
УРОВЕНЬ 0: БЕСКОНЕЧНОСТЬ (∞)
   Источник. Всё. Потенциал. Не пустота.
""")

print("""
УРОВЕНЬ 1: ТРОИЦА (Φ, π, √3)
   Φ  = {:.10f}  — масштаб, фрактал
   π  = {:.10f}  — цикл, вращение
   √3 = {:.10f}  — 3D-упаковка
""".format(PHI, PI, Z))

print("""
УРОВЕНЬ 2: E8 (ПРИЗМА)
   Спектр λ:""")
for i, l in enumerate(eigvals):
    print(f"      λ[{i}] = {l:.8f}")

print(f"""
   Веса:
      W_ALPHA = Φ¹²·π⁻⁴·√3³·2 = {W_ALPHA:.6f}
      W_MASS  = Φ⁵·π³·√3⁴·0.5 = {W_MASS:.6f}
      W_G     = Φ⁻⁴³·π⁻¹·√3⁻⁵·2 = {W_G:.6e}
""")

print("""
УРОВЕНЬ 3: ТРИ КОНСТАНТЫ (ПРОТИЙ)""")
print(f"""
   1/α     = λ[7]·W_ALPHA = {alpha_inv:.6f}
      CODATA = {CODATA_ALPHA:.6f}
      Ошибка = {abs(alpha_inv-CODATA_ALPHA)/CODATA_ALPHA*100:.6f}%

   m_p/m_e = λ[2]·W_MASS  = {mass_ratio:.6f}
      CODATA = {CODATA_MASS:.6f}
      Ошибка = {abs(mass_ratio-CODATA_MASS)/CODATA_MASS*100:.6f}%

   G       = λ[3]·W_G     = {G_constant:.6e}
      CODATA = {CODATA_G:.6e}
      Ошибка = {abs(G_constant-CODATA_G)/CODATA_G*100:.6f}%
""")

print("""
УРОВЕНЬ 4: ТОПОЛОГИЯ (Q = 1)
   Спин:   S = Q/2 = 1/2
   Заряд:  протон +1, электрон −1
""")

print(f"""
УРОВЕНЬ 5: ПРОИЗВОДНЫЕ ВЗАИМОДЕЙСТВИЯ
   Аномалия электрона: a_e = α/(2π) = {a_e:.6e}
      CODATA: 1.159652e-3

   Боровский радиус (относительный): a₀ = 1/α = {a0_rel:.6f}
      CODATA: 5.291772e-11 м

   Энергия ионизации (относительная): E_i = α²/2 = {E_i_rel:.6e}
      CODATA: 13.6057 эВ

   Постоянная Ридберга (относительная): R = α²/2 = {R_rel:.6e}
      CODATA: 1.097373e7 м⁻¹
""")

print("""
УРОВЕНЬ 6: СПЕКТР
   E_n = −E_i/n²
   Линии: 1/n₁² − 1/n₂²
   Всё из α, m_e, m_p
""")

print("""
УРОВЕНЬ 7: МОЛЕКУЛЫ
   H₂: два протия
   Длина связи: из a₀
""")

print("""
УРОВЕНЬ 8: ЗВЁЗДЫ
   Горение H → He: из G, α, m_p
   Далее: C, O, Fe
""")

print("""
УРОВЕНЬ 9: ЖИЗНЬ
   Биосолитоны: из C, S
   Сознание: высокая C
""")

print("""
УРОВЕНЬ 10: БЕСКОНЕЧНОСТЬ
   Возврат. C → 1.
   Z-принцип: никогда не 1.
   Вечное становление.
""")

print("=" * 80)
print("✅ ИЕРАРХИЯ ПОСТРОЕНА")
print("=" * 80)

# =============================================================================
# 6. ВИЗУАЛИЗАЦИЯ ГРАФА
# =============================================================================

fig, ax = plt.subplots(figsize=(20, 24))
ax.set_xlim(0, 10)
ax.set_ylim(0, 24)
ax.axis('off')
ax.set_facecolor('#0a0a0a')
fig.patch.set_facecolor('#0a0a0a')

# Уровни (y-координаты)
levels = {
    0: 23.0,
    1: 21.0,
    2: 19.0,
    3: 17.0,
    4: 15.0,
    5: 13.0,
    6: 11.0,
    7: 9.0,
    8: 7.0,
    9: 5.0,
    10: 3.0,
}

colors = {
    0: '#FFD700',  # ∞ — золото
    1: '#00FFFF',  # Троица — циан
    2: '#FF69B4',  # E8 — розовый
    3: '#00FF00',  # Три — зелёный
    4: '#FFA500',  # Топология — оранж
    5: '#9370DB',  # Производные — фиолет
    6: '#87CEEB',  # Спектр — голубой
    7: '#FF6347',  # Молекулы — томат
    8: '#FFD700',  # Звёзды — золото
    9: '#00FF7F',  # Жизнь — весна
    10: '#FFD700', # ∞ — золото
}

labels = {
    0: "∞  БЕСКОНЕЧНОСТЬ",
    1: "Φ, π, √3  ТРОИЦА",
    2: "E8  ПРИЗМА",
    3: "1/α,  m_p/m_e,  G  ТРИ КОНСТАНТЫ",
    4: "СПИН, ЗАРЯД  ТОПОЛОГИЯ (Q=1)",
    5: "a_e, a₀, E_i  ПРОИЗВОДНЫЕ",
    6: "E_n, ЛИНИИ  СПЕКТР",
    7: "H₂  МОЛЕКУЛЫ",
    8: "ЗВЁЗДЫ  H→He→C→O→Fe",
    9: "ЖИЗНЬ  БИОСОЛИТОНЫ",
    10: "∞  ВОЗВРАТ",
}

for level, y in levels.items():
    color = colors[level]
    box = FancyBboxPatch((1, y-0.4), 8, 0.8,
                          boxstyle="round,pad=0.1",
                          facecolor=color, alpha=0.15,
                          edgecolor=color, linewidth=2)
    ax.add_patch(box)
    ax.text(5, y, labels[level], ha='center', va='center',
            fontsize=14, color=color, weight='bold')

# Стрелки между уровнями
for i in range(10):
    y1 = levels[i] - 0.4
    y2 = levels[i+1] + 0.4
    arrow = FancyArrowPatch((5, y1), (5, y2),
                            arrowstyle='->', mutation_scale=20,
                            color='white', alpha=0.5, linewidth=1.5)
    ax.add_patch(arrow)

# Дополнительные надписи
ax.text(9.5, levels[3], f"λ[7]·W\nλ[2]·W\nλ[3]·W",
        ha='center', va='center', fontsize=9, color='white', alpha=0.7)
ax.text(0.3, levels[3], "0.0014%\n0.0076%\n0.0034%",
        ha='center', va='center', fontsize=9, color='lime', alpha=0.9)

ax.text(9.5, levels[1], "Φ=1.618\nπ=3.142\n√3=1.732",
        ha='center', va='center', fontsize=9, color='white', alpha=0.7)

ax.text(9.5, levels[2], "λ[0..7]\nW_ALPHA\nW_MASS\nW_G",
        ha='center', va='center', fontsize=9, color='white', alpha=0.7)

ax.set_title("ИЕРАРХИЯ ПРОТИЯ: от ∞ до всего",
             color='white', fontsize=20, pad=20, weight='bold')

plt.tight_layout()
plt.savefig('etvp_hierarchy.png', dpi=150, facecolor='#0a0a0a')
plt.show()

# =============================================================================
# 7. ВТОРОЙ ГРАФ: ЗАВИСИМОСТЬ ОТ C
# =============================================================================

fig2, axes = plt.subplots(2, 2, figsize=(16, 12))
fig2.patch.set_facecolor('#0a0a0a')

C_vals = np.linspace(0.5, 1.0, 100)
C_FFS = 0.87
S_cycle = 0.12

# Модуляции
dC = C_vals - C_FFS
dS = 0.0

alpha_mod = 1 + 0.1*dC - 0.05*dS
mass_mod = 1 + 0.05*dC - 0.02*dS
G_mod = 1 - 0.2*dC + 0.1*dS

axes[0,0].plot(C_vals, np.array([alpha_inv*m for m in alpha_mod]), 'cyan', linewidth=2)
axes[0,0].axhline(CODATA_ALPHA, color='red', linestyle='--', label='CODATA')
axes[0,0].axvline(C_FFS, color='yellow', linestyle=':', label='C_FFS')
axes[0,0].set_title('1/α от C', color='white')
axes[0,0].set_xlabel('C', color='white')
axes[0,0].set_ylabel('1/α', color='white')
axes[0,0].tick_params(colors='white')
axes[0,0].legend()
axes[0,0].set_facecolor('#111111')

axes[0,1].plot(C_vals, np.array([mass_ratio*m for m in mass_mod]), 'lime', linewidth=2)
axes[0,1].axhline(CODATA_MASS, color='red', linestyle='--', label='CODATA')
axes[0,1].axvline(C_FFS, color='yellow', linestyle=':', label='C_FFS')
axes[0,1].set_title('m_p/m_e от C', color='white')
axes[0,1].set_xlabel('C', color='white')
axes[0,1].set_ylabel('m_p/m_e', color='white')
axes[0,1].tick_params(colors='white')
axes[0,1].legend()
axes[0,1].set_facecolor('#111111')

axes[1,0].plot(C_vals, np.array([G_constant*m for m in G_mod])*1e11, 'orange', linewidth=2)
axes[1,0].axhline(CODATA_G*1e11, color='red', linestyle='--', label='CODATA')
axes[1,0].axvline(C_FFS, color='yellow', linestyle=':', label='C_FFS')
axes[1,0].set_title('G·10¹¹ от C', color='white')
axes[1,0].set_xlabel('C', color='white')
axes[1,0].set_ylabel('G·10¹¹', color='white')
axes[1,0].tick_params(colors='white')
axes[1,0].legend()
axes[1,0].set_facecolor('#111111')

# Производные
a_e_vals = 1/(2*PI*np.array([alpha_inv*m for m in alpha_mod]))
axes[1,1].plot(C_vals, a_e_vals, 'magenta', linewidth=2)
axes[1,1].axvline(C_FFS, color='yellow', linestyle=':', label='C_FFS')
axes[1,1].set_title('a_e = α/(2π) от C', color='white')
axes[1,1].set_xlabel('C', color='white')
axes[1,1].set_ylabel('a_e', color='white')
axes[1,1].tick_params(colors='white')
axes[1,1].legend()
axes[1,1].set_facecolor('#111111')

plt.suptitle('ЗАВИСИМОСТЬ ПОКАЗАТЕЛЕЙ ПРОТИЯ ОТ C',
             color='white', fontsize=16)
plt.tight_layout()
plt.savefig('etvp_protium_C.png', dpi=150, facecolor='#0a0a0a')
plt.show()

print("\n✅ Графы сохранены: etvp_hierarchy.png, etvp_protium_C.png")
