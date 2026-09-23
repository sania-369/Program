#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP BIRTH v2 — Рождение частиц из вакуума (нелинейная активация)
================================================================================
ЗАДАЁШЬ:
  - C_FFS  — когерентность/плотность вакуума
  - S_cycle — шум

СМОТРИШЬ:
  - Какие λ_j активны (нелинейная активация)
  - Разности Δλ — сдвиг спектра
  - Резонансы (λ_i + λ_j ≈ λ_k)
  - Что это значит физически
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 0. ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

C_MIN = 1.0 / (PHI ** 10)
C_MAX = 1.0 - 1.0 / (PHI ** 20)

# =============================================================================
# 1. ТОЧКИ УПРАВЛЕНИЯ
# =============================================================================

# >>> ЗАДАЙ УСЛОВИЯ <<<
C_FFS   = 0.87
S_CYCLE = 0.12

# =============================================================================
# 2. E8 И СПЕКТР
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
# 3. НЕЛИНЕЙНАЯ АКТИВАЦИЯ МОД
# =============================================================================

def active_modes(C_FFS, S_cycle, threshold=0.5):
    """
    Нелинейная активация мод.
    При высоком C_FFS — все моды активны.
    При высоком S_cycle — высокие моды подавлены.
    """
    active = []
    for i, lam in enumerate(eigvals):
        # Активация: чем выше C, тем выше активация
        # Чем выше S, тем сильнее подавление
        activation = lam * (C_FFS ** 2) / (1.0 + S_cycle * 10.0)
        if activation > threshold:
            active.append((i, lam, activation))
    return active


# =============================================================================
# 4. СДВИГ СПЕКТРА ОТ C_FFS
# =============================================================================

def shifted_spectrum(C_FFS):
    """
    Сдвиг спектра относительно C_FFS.
    При C_FFS → C_MIN — спектр сжимается.
    При C_FFS → C_MAX — спектр расширяется.
    """
    # Коэффициент сжатия/расширения
    scale = C_FFS / 0.87  # относительно нашего режима
    return eigvals * scale


# =============================================================================
# 5. РАЗНОСТИ Δλ
# =============================================================================

def find_differences(tolerance=0.1):
    """Находит разности Δλ = λ_i - λ_j."""
    diffs = []
    n = len(eigvals)
    for i in range(n):
        for j in range(i+1, n):
            d = eigvals[i] - eigvals[j]
            if abs(d) > tolerance:
                diffs.append((i, j, d))
    return diffs


# =============================================================================
# 6. РЕЗОНАНСЫ
# =============================================================================

def find_resonances(tolerance=0.05):
    resonances = []
    n = len(eigvals)
    for i in range(n):
        for j in range(i, n):
            for k in range(n):
                if k == i or k == j:
                    continue
                s = eigvals[i] + eigvals[j]
                if abs(s - eigvals[k]) / max(eigvals[k], 1e-12) < tolerance:
                    resonances.append((i, j, k, eigvals[i], eigvals[j], eigvals[k], s))
    return resonances


# =============================================================================
# 7. ЧТО РОЖДАЕТСЯ
# =============================================================================

def what_born(C_FFS, S_cycle):
    active = active_modes(C_FFS, S_cycle)
    resonances = find_resonances()
    diffs = find_differences()
    shifted = shifted_spectrum(C_FFS)

    print("\n" + "=" * 80)
    print(f"🌱 РОЖДЕНИЕ ПРИ C_FFS = {C_FFS}, S_cycle = {S_cycle}")
    print("=" * 80)

    print(f"\n📊 АКТИВНЫЕ МОДЫ ({len(active)} из 8):")
    for i, lam, act in active:
        print(f"   λ[{i}] = {lam:.6f}  (активация: {act:.6f})")

    print(f"\n📊 СДВИГ СПЕКТРА (C_FFS = {C_FFS}, относительно 0.87):")
    scale = C_FFS / 0.87
    print(f"   Коэффициент сдвига: {scale:.6f}")
    for i in range(len(eigvals)):
        print(f"   λ[{i}]: {eigvals[i]:.6f} → {shifted[i]:.6f}  (Δ = {shifted[i]-eigvals[i]:+.6f})")

    print(f"\n📊 РАЗНОСТИ Δλ (первые 10):")
    for i, j, d in diffs[:10]:
        print(f"   λ[{i}] - λ[{j}] = {d:+.6f}")

    print(f"\n📊 РЕЗОНАНСЫ (λ_i + λ_j ≈ λ_k):")
    for r in resonances[:10]:
        i, j, k, li, lj, lk, s = r
        print(f"   λ[{i}] + λ[{j}] = {s:.6f}  ≈  λ[{k}] = {lk:.6f}")

    print(f"\n📊 ЧТО РОЖДАЕТСЯ:")
    if len(active) == 0:
        print("   • Частицы не рождаются. Слишком низкая когерентность.")
    elif len(active) <= 2:
        print("   • Только низшие моды. Экзотические состояния.")
    elif len(active) <= 5:
        print("   • Частичное рождение. Нестабильные частицы.")
    elif len(active) <= 7:
        print("   • Большинство мод активно. Стандартная модель.")
    else:
        print("   • Все моды активны. Полный спектр частиц.")
        print("   • Три поколения (λ[1]+λ[6], λ[2]+λ[5], λ[3]+λ[4]).")


# =============================================================================
# 8. ЗАПУСК
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("🌀 ETVP BIRTH v2 — Рождение частиц из вакуума")
    print("=" * 80)
    print(f"\n🔧 ЗАДАННЫЕ УСЛОВИЯ:")
    print(f"   C_FFS   = {C_FFS}")
    print(f"   S_cycle = {S_CYCLE}")

    print(f"\n📊 СПЕКТР E8:")
    for i, lam in enumerate(eigvals):
        print(f"   λ[{i}] = {lam:.6f}")

    what_born(C_FFS, S_CYCLE)

    # Графики
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Спектр
    axes[0, 0].stem(range(len(eigvals)), eigvals, basefmt=" ")
    axes[0, 0].set_xlabel("Индекс λ")
    axes[0, 0].set_ylabel("Значение λ")
    axes[0, 0].set_title("Спектр E8 (базовый)")
    axes[0, 0].grid(alpha=0.3)

    # Сдвиг спектра
    shifted = shifted_spectrum(C_FFS)
    axes[0, 1].plot(range(len(eigvals)), eigvals, 'o-', label='базовый')
    axes[0, 1].plot(range(len(eigvals)), shifted, 's--', label=f'сдвинутый (C={C_FFS})')
    axes[0, 1].set_xlabel("Индекс λ")
    axes[0, 1].set_ylabel("Значение λ")
    axes[0, 1].set_title("Сдвиг спектра")
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    # Активные моды
    active = active_modes(C_FFS, S_CYCLE)
    active_idx = [a[0] for a in active]
    active_acts = [a[2] for a in active]
    axes[1, 0].bar(active_idx, active_acts, color='green', alpha=0.7)
    axes[1, 0].axhline(0.5, color='red', linestyle='--', label='порог')
    axes[1, 0].set_xlabel("Индекс λ")
    axes[1, 0].set_ylabel("Активация")
    axes[1, 0].set_title(f"Активные моды (C={C_FFS}, S={S_CYCLE})")
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)

    # Резонансы
    res_sums = [r[6] for r in find_resonances()]
    axes[1, 1].hist(res_sums, bins=20, color='purple', alpha=0.7)
    axes[1, 1].axvline(4.0, color='red', linestyle='--', label='λ[7] порог')
    axes[1, 1].set_xlabel("Сумма λ_i + λ_j")
    axes[1, 1].set_ylabel("Частота")
    axes[1, 1].set_title("Распределение резонансов")
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'etvp_birth_v2_{C_FFS}.png', dpi=150)
    plt.show()

    print("\n✅ Готово.")
