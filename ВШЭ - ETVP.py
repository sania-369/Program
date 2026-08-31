#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETVP + ВШЭ: Гибридный солвер для подвижности ионов в гелии.
Соединяет быструю аналитику ВШЭ с полевыми поправками ETVP.
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 0. БАЗОВЫЕ КОНСТАНТЫ ETVP
# =============================================================================
PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI = np.pi
SQRT3 = np.sqrt(3.0)

# =============================================================================
# 1. БАЗОВЫЙ МЕТОД ВШЭ (аналитические формулы)
# =============================================================================
def mobility_vshe(E_field, ion='O2'):
    """
    Базовая подвижность иона в гелии по методу ВШЭ.
    E_field: приведённое электрическое поле, Тд (10^-17 В·см²)
    ion: 'O2', 'O4', 'NO'
    Возвращает подвижность K (см²/(В·с)).
    """
    # Аппроксимация из статьи ВШЭ
    if ion == 'O2':
        # O2- в He
        K0 = 2.5  # см²/(В·с) при низких полях
        alpha = 0.02
        beta = 0.15
    elif ion == 'O4':
        K0 = 1.8
        alpha = 0.03
        beta = 0.20
    elif ion == 'NO':
        K0 = 2.2
        alpha = 0.025
        beta = 0.18
    else:
        raise ValueError(f"Unknown ion: {ion}")

    # Модельная зависимость от поля
    # K(E) = K0 / (1 + alpha * E^beta)
    return K0 / (1.0 + alpha * (E_field ** beta))

# =============================================================================
# 2. ПОЛЕВЫЕ ПОПРАВКИ ETVP
# =============================================================================
def coherence_helium(E_field):
    """
    Когерентность (C) гелия как функция поля.
    C ∈ [0, 1].
    """
    # Модель: при низких полях гелий когерентен, при высоких — разогревается
    return 1.0 / (1.0 + 0.01 * E_field ** 0.5)

def entropy_helium(E_field):
    """
    Энтропия (S) гелия как функция поля.
    """
    # Рост энтропии с полем
    return 0.1 * np.tanh(0.01 * E_field) + 0.05

def gradient_coherence(E_field, spatial_pos=0.0):
    """
    Градиент когерентности (∇C) — предполагаем линейное изменение.
    """
    return 0.001 * E_field * spatial_pos

# =============================================================================
# 3. ГИБРИДНЫЙ СОЛВЕР
# =============================================================================
def mobility_hybrid(E_field, ion='O2', spatial_pos=0.0, use_etvp=True):
    """
    Гибридный расчёт подвижности: ВШЭ + поправки ETVP.
    """
    # 1. Базовое значение ВШЭ
    K_base = mobility_vshe(E_field, ion)

    if not use_etvp:
        return K_base

    # 2. Вычисляем параметры ETVP
    C = coherence_helium(E_field)
    S = entropy_helium(E_field)
    gradC = gradient_coherence(E_field, spatial_pos)

    # 3. Поправки
    # Когерентность: чем выше C, тем меньше рассеяние, выше подвижность
    correction_C = 1.0 + 0.2 * (C - 0.5)

    # Энтропия: чем выше S, тем больше хаоса, ниже подвижность
    correction_S = 1.0 - 0.3 * S

    # Градиент: вносит асимметрию
    correction_grad = 1.0 + 0.05 * gradC

    # Резонансная поправка (обертон, близкий к 1 ТГц)
    E_res = 1e3  # Тд, резонансное поле (энергия ~1 ТГц)
    resonance = 1.0 + 0.1 * np.exp(-((E_field - E_res) / 200) ** 2)

    # Итоговая подвижность
    K_etvp = K_base * correction_C * correction_S * correction_grad * resonance

    return K_etvp

# =============================================================================
# 4. ВЕРИФИКАЦИЯ И СРАВНЕНИЕ
# =============================================================================
def run_hybrid_test():
    print("=" * 70)
    print("ГИБРИДНЫЙ СОЛВЕР: ВШЭ + ETVP")
    print("=" * 70)

    # Диапазон полей (Тд)
    E_fields = np.linspace(1, 500, 100)

    # Расчёт подвижности O2-
    K_vshe = [mobility_vshe(E, 'O2') for E in E_fields]
    K_hybrid = [mobility_hybrid(E, 'O2', spatial_pos=0.0) for E in E_fields]
    K_hybrid_grad = [mobility_hybrid(E, 'O2', spatial_pos=1.0) for E in E_fields]

    # График
    plt.figure(figsize=(12, 6))

    plt.plot(E_fields, K_vshe, 'b-', label='ВШЭ (базовый)', linewidth=2)
    plt.plot(E_fields, K_hybrid, 'r--', label='ВШЭ + ETVP (C, S)', linewidth=2)
    plt.plot(E_fields, K_hybrid_grad, 'g:', label='ВШЭ + ETVP (∇C ≠ 0)', linewidth=2)

    plt.xlabel('Приведённое поле E/N (Тд)')
    plt.ylabel('Подвижность K (см²/(В·с))')
    plt.title('Гибридный расчёт подвижности O₂⁻ в гелии')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

    # Вывод
    print("\nЗначения при E = 100 Тд:")
    print(f"  ВШЭ (базовый):        {mobility_vshe(100, 'O2'):.4f}")
    print(f"  ВШЭ + ETVP (C, S):     {mobility_hybrid(100, 'O2'):.4f}")
    print(f"  ВШЭ + ETVP (∇C ≠ 0):   {mobility_hybrid(100, 'O2', spatial_pos=1.0):.4f}")

    print("\nПоправки ETVP:")
    E = 100
    print(f"  C = {coherence_helium(E):.4f}")
    print(f"  S = {entropy_helium(E):.4f}")
    print(f"  ∇C = {gradient_coherence(E, 1.0):.4f}")

if __name__ == "__main__":
    run_hybrid_test()
