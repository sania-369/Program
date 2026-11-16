import numpy as np

# =============================================================================
# ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================
PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

# =============================================================================
# МАТРИЦА E8
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

eigvals = np.sort(np.real(np.linalg.eigvals(E8)))

# =============================================================================
# КОНСТАНТЫ ИЗ E8
# =============================================================================
W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4) * 0.5
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * 2

alpha_inv = eigvals[7] * W_ALPHA
mass_ratio = eigvals[2] * W_MASS
G_E8 = eigvals[3] * W_G

# =============================================================================
# ГРАНИЦЫ КОГЕРЕНТНОСТИ (ИЗ E8)
# =============================================================================
r = 8
h = 30
C_MIN = PHI ** -(r + 2)          # Phi^-10
C_MAX = 1.0 - PHI ** -(2*(r + 2)) # 1 - Phi^-20

print("=" * 80)
print("ПРОВЕРКА ГИПОТЕЗЫ: rho_min = rho_0 * Phi^-10, rho_max = rho_0 * (1 - Phi^-20)")
print("=" * 80)
print(f"\nC_MIN = {C_MIN:.15f}")
print(f"C_MAX = {C_MAX:.15f}")
print(f"C_MAX - C_MIN = {C_MAX - C_MIN:.15f}")

# =============================================================================
# ГИПОТЕЗА: rho_min, rho_max
# =============================================================================
rho_0 = 1.0  # нормировка (фоновая плотность)

rho_min = rho_0 * PHI ** -10
rho_max = rho_0 * (1.0 - PHI ** -20)

print(f"\nГипотеза:")
print(f"rho_min = rho_0 * Phi^-10 = {rho_min:.15f}")
print(f"rho_max = rho_0 * (1 - Phi^-20) = {rho_max:.15f}")
print(f"rho_max - rho_min = {rho_max - rho_min:.15f}")

# =============================================================================
# СРАВНЕНИЕ С C_MIN, C_MAX
# =============================================================================
print("\n" + "=" * 80)
print("СРАВНЕНИЕ: C_MIN vs rho_min, C_MAX vs rho_max")
print("=" * 80)

print(f"\nC_MIN = Phi^-10 = {C_MIN:.15f}")
print(f"rho_min / rho_0 = Phi^-10 = {rho_min:.15f}")
print(f"Отношение: rho_min / (rho_0 * C_MIN) = {rho_min / (rho_0 * C_MIN):.15f}")

print(f"\nC_MAX = 1 - Phi^-20 = {C_MAX:.15f}")
print(f"rho_max / rho_0 = 1 - Phi^-20 = {rho_max:.15f}")
print(f"Отношение: rho_max / (rho_0 * C_MAX) = {rho_max / (rho_0 * C_MAX):.15f}")

# =============================================================================
# ПРОВЕРКА: СВЯЗЬ rho_C И C ЧЕРЕЗ ГИПЕРБОЛИЧЕСКУЮ УПРУГОСТЬ
# =============================================================================
print("\n" + "=" * 80)
print("ПРОВЕРКА: СВЯЗЬ rho_C И C ЧЕРЕЗ ГИПЕРБОЛУ")
print("=" * 80)

def sigma_from_C(C, C_min=C_MIN, C_max=C_MAX, h=h):
    """Обратная функция гиперболической упругости."""
    delta_C = C - C_min
    delta_C_max = C_max - C_min
    return delta_C / (delta_C_max * (1 + h) - h * delta_C)

def rho_from_sigma(sigma, rho_min=rho_min, rho_max=rho_max):
    """Плотность из sigma."""
    return rho_min + (rho_max - rho_min) * sigma

def rho_from_C(C, rho_min=rho_min, rho_max=rho_max, C_min=C_MIN, C_max=C_MAX, h=h):
    """Плотность из C (строгая обратная функция)."""
    sigma = sigma_from_C(C, C_min, C_max, h)
    return rho_from_sigma(sigma, rho_min, rho_max)

# Проверка при разных C
print("\nC\t\tsigma(C)\trho_C(C)\trho_C/rho_0")
print("-" * 60)
for C in [C_MIN, C_MIN + 0.01, 0.1, 0.5, 0.9, C_MAX]:
    sigma = sigma_from_C(C)
    rho = rho_from_C(C)
    print(f"{C:.6f}\t{sigma:.6f}\t{rho:.6f}\t{rho/rho_0:.6f}")

# =============================================================================
# ПРОВЕРКА: ГРАНИЧНЫЕ СЛУЧАИ
# =============================================================================
print("\n" + "=" * 80)
print("ПРОВЕРКА: ГРАНИЧНЫЕ СЛУЧАИ")
print("=" * 80)

# 1. C = C_MIN
C = C_MIN
sigma = sigma_from_C(C)
rho = rho_from_C(C)
print(f"\n1. C = C_MIN = {C:.15f}")
print(f"   sigma = {sigma:.15f}")
print(f"   rho_C = {rho:.15f}")
print(f"   Ожидание: rho_C = rho_min = {rho_min:.15f}")
print(f"   Совпадение: {abs(rho - rho_min) < 1e-12}")

# 2. C = C_MAX
C = C_MAX
sigma = sigma_from_C(C)
rho = rho_from_C(C)
print(f"\n2. C = C_MAX = {C:.15f}")
print(f"   sigma = {sigma:.15f}")
print(f"   rho_C = {rho:.15f}")
print(f"   Ожидание: rho_C = rho_max = {rho_max:.15f}")
print(f"   Совпадение: {abs(rho - rho_max) < 1e-12}")

# 3. C = (C_MIN + C_MAX) / 2
C = (C_MIN + C_MAX) / 2
sigma = sigma_from_C(C)
rho = rho_from_C(C)
print(f"\n3. C = (C_MIN + C_MAX)/2 = {C:.15f}")
print(f"   sigma = {sigma:.15f}")
print(f"   rho_C = {rho:.15f}")
print(f"   rho_C / rho_0 = {rho/rho_0:.15f}")

# =============================================================================
# ПРОВЕРКА: ВЛИЯНИЕ S И K
# =============================================================================
print("\n" + "=" * 80)
print("ПРОВЕРКА: ВЛИЯНИЕ S И K")
print("=" * 80)

S_max = np.log(248)  # энтропия максимального беспорядка
K_0 = 30.0

print(f"\nS_max = ln(248) = {S_max:.6f}")
print(f"K_0 = {K_0:.1f}")

# Формула: rho_C(C, S, K) = rho_C(C) * (1 - S/S_max) * (K/K_0)
def rho_full(C, S, K, rho_min=rho_min, rho_max=rho_max, C_min=C_MIN, C_max=C_MAX, h=h, S_max=S_max, K_0=K_0):
    """Полная формула с S и K."""
    rho_C = rho_from_C(C, rho_min, rho_max, C_min, C_max, h)
    return rho_C * (1.0 - S / S_max) * (K / K_0)

# Проверка при разных S, K
print("\nC\t\tS\t\tK\t\trho_C(C,S,K)\trho_C/rho_0")
print("-" * 70)
for C, S, K in [
    (C_MAX, 0.0, 30.0),   # идеал
    (C_MAX, S_max, 30.0), # максимальный шум
    (C_MAX, 0.0, 0.0),    # нет уплотнения
    (C_MIN, 0.0, 30.0),   # минимальная плотность, но уплотнение
    (0.5, 0.5, 15.0),     # середина
]:
    rho = rho_full(C, S, K)
    print(f"{C:.6f}\t{S:.6f}\t{K:.1f}\t{rho:.6f}\t{rho/rho_0:.6f}")

# =============================================================================
# ПРОВЕРКА: УСТОЙЧИВОСТЬ К ИЗМЕНЕНИЮ r
# =============================================================================
print("\n" + "=" * 80)
print("УСТОЙЧИВОСТЬ: ЧТО ЕСЛИ r = 7 ИЛИ r = 9?")
print("=" * 80)

for r_test in [7, 8, 9]:
    C_MIN_test = PHI ** -(r_test + 2)
    C_MAX_test = 1.0 - PHI ** -(2*(r_test + 2))
    rho_min_test = PHI ** -10  # не зависит от r? (гипотеза)
    rho_max_test = 1.0 - PHI ** -20
    print(f"\nr = {r_test}:")
    print(f"  C_MIN = Phi^-{r_test+2} = {C_MIN_test:.15f}")
    print(f"  C_MAX = 1 - Phi^-{2*(r_test+2)} = {C_MAX_test:.15f}")
    print(f"  rho_min = Phi^-10 = {rho_min_test:.15f} (не зависит от r)")
    print(f"  rho_max = 1 - Phi^-20 = {rho_max_test:.15f} (не зависит от r)")

# =============================================================================
# ИТОГ
# =============================================================================
print("\n" + "=" * 80)
print("ИТОГ")
print("=" * 80)
print("""
Гипотеза: rho_min = rho_0 * Phi^-10, rho_max = rho_0 * (1 - Phi^-20).

Проверки:
1. Граничные случаи: C = C_MIN -> rho_C = rho_min (верно)
2. Граничные случаи: C = C_MAX -> rho_C = rho_max (верно)
3. Влияние S: при S = S_max -> rho_C = 0 (верно)
4. Влияние K: при K = 0 -> rho_C = 0 (верно)
5. Устойчивость: rho_min, rho_max не зависят от r (гипотеза)

Что не проверено:
- rho_0 не выведен из E8 (нормировка).
- S_max = ln(248) не выведен из E8 строго (стандартное определение).
- Связь rho_C и C через гиперболу не доказана (гипотеза).

Что это значит:
Гипотеза согласуется с границами C_MIN, C_MAX и даёт правильные
предельные случаи. Но это не доказательство — это проверка
согласованности. Для строгого вывода нужно вывести rho_0 и S_max
из E8.
""")
