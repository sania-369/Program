#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌀 ETVP BIRTH — Рождение частиц из вакуума при заданных C_FFS и S_cycle
================================================================================
ЗАДАЁШЬ:
  - C_FFS  — когерентность/плотность вакуума
  - S_cycle — шум

СМОТРИШЬ:
  - Какие λ_j активны
  - Какие резонансы возникают (λ_i + λ_j ≈ λ_k)
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
# 3. КАКИЕ λ_j АКТИВНЫ ПРИ ДАННЫХ УСЛОВИЯХ
# =============================================================================

def active_modes(C_FFS, S_cycle):
    """Определяет, какие λ_j активны при данных C_FFS и S_cycle."""
    # Порог активации зависит от C_FFS и S_cycle
    threshold = C_FFS - S_cycle * 0.5

    active = []
    for i, lam in enumerate(eigvals):
        # Мода активна, если её вклад > порога
        weight = lam * C_FFS - lam * S_cycle * 0.1
        if weight > threshold * lam * 0.5:
            active.append((i, lam, weight))

    return active


# =============================================================================
# 4. РЕЗОНАНСЫ (λ_i + λ_j ≈ λ_k)
# =============================================================================

def find_resonances(tolerance=0.05):
    """Находит тройки λ_i + λ_j ≈ λ_k."""
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
# 5. ЧТО РОЖДАЕТСЯ
# =============================================================================

def what_born(C_FFS, S_cycle):
    """Определяет, что рождается при данных условиях."""
    active = active_modes(C_FFS, S_cycle)
    resonances = find_resonances()

    print("\n" + "=" * 80)
    print(f"🌱 РОЖДЕНИЕ ПРИ C_FFS = {C_FFS}, S_cycle = {S_cycle}")
    print("=" * 80)

    print(f"\n📊 АКТИВНЫЕ МОДЫ:")
    for i, lam, w in active:
        print(f"   λ[{i}] = {lam:.6f}  (вклад: {w:.6f})")

    print(f"\n📊 РЕЗОНАНСЫ (λ_i + λ_j ≈ λ_k):")
    for r in resonances:
        i, j, k, li, lj, lk, s = r
        print(f"   λ[{i}] + λ[{j}] = {s:.6f}  ≈  λ[{k}] = {lk:.6f}")

    print(f"\n📊 ЧТО РОЖДАЕТСЯ:")

    # Интерпретация по C_FFS
    if C_FFS <= 0.05:
        print("   • Сингулярность. Частицы не рождаются.")
    elif C_FFS <= 0.3:
        print("   • Экзотические состояния. Частицы нестабильны.")
    elif C_FFS <= 0.5:
        print("   • Плазма. Возможны термоядерные реакции.")
        print("   • LENR: трансмутации в решётке.")
    elif C_FFS <= 0.8:
        print("   • Холодная материя. Стандартные частицы.")
        print("   • Протон, электрон, нейтрон.")
    elif C_FFS <= 0.95:
        print("   • Наш режим. Стандартная модель.")
        print("   • Все известные частицы.")
    elif C_FFS <= 0.99:
        print("   • Высококогерентный режим.")
        print("   • Возможны новые резонансы.")
        print("   • Стерильные нейтрино, аксионы?")
    else:
        print("   • Почти абсолютный вакуум.")
        print("   • Частицы не рождаются.")
        print("   • Только поле.")

    # Что дают резонансы
    print(f"\n📊 ФИЗИЧЕСКИЙ СМЫСЛ РЕЗОНАНСОВ:")
    if len(resonances) > 0:
        print(f"   Найдено {len(resonances)} резонансов.")
        print("   Каждый — возможный канал рождения частиц.")
        print("   Например:")
        r0 = resonances[0]
        i, j, k, li, lj, lk, s = r0
        print(f"   λ[{i}] + λ[{j}] ≈ λ[{k}]")
        print(f"   → частица с массой ~{lk:.4f} (в единицах спектра)")
    else:
        print("   Резонансов нет. Частицы не рождаются.")


# =============================================================================
# 6. ЗАПУСК
# =============================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("🌀 ETVP BIRTH — Рождение частиц из вакуума")
    print("=" * 80)
    print(f"\n🔧 ЗАДАННЫЕ УСЛОВИЯ:")
    print(f"   C_FFS   = {C_FFS}")
    print(f"   S_cycle = {S_CYCLE}")

    print(f"\n📊 СПЕКТР E8:")
    for i, lam in enumerate(eigvals):
        print(f"   λ[{i}] = {lam:.6f}")

    # Что рождается
    what_born(C_FFS, S_CYCLE)

    # Графики
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Спектр
    axes[0].stem(range(len(eigvals)), eigvals, basefmt=" ")
    axes[0].set_xlabel("Индекс λ")
    axes[0].set_ylabel("Значение λ")
    axes[0].set_title("Спектр E8")
    axes[0].grid(alpha=0.3)

    # Активные моды
    active = active_modes(C_FFS, S_CYCLE)
    active_idx = [a[0] for a in active]
    active_vals = [a[1] for a in active]
    axes[1].bar(active_idx, active_vals, color='green', alpha=0.7)
    axes[1].set_xlabel("Индекс λ")
    axes[1].set_ylabel("Значение λ")
    axes[1].set_title(f"Активные моды (C_FFS = {C_FFS})")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'etvp_birth_{C_FFS}.png', dpi=150)
    plt.show()

    print("\n✅ Готово.")
