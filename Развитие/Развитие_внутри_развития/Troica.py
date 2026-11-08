import numpy as np
from itertools import combinations

# ============================================================
# 1. Матрица 11x11 (E8 + 3), как в ETVP_12.4
# ============================================================
def cartan_e8_11x11():
    C = np.zeros((11, 11), dtype=float)
    # E8 в первых 8
    C[0:8, 0:8] = np.array([
        [ 2, -1,  0,  0,  0,  0,  0,  0],
        [-1,  2, -1,  0,  0,  0,  0,  0],
        [ 0, -1,  2, -1,  0,  0,  0,  0],
        [ 0,  0, -1,  2, -1,  0,  0,  0],
        [ 0,  0,  0, -1,  2, -1,  0, -1],
        [ 0,  0,  0,  0, -1,  2, -1,  0],
        [ 0,  0,  0,  0,  0, -1,  2,  0],
        [ 0,  0,  0,  0, -1,  0,  0,  2]
    ], dtype=float)
    # Расширение до 11: диагональ для 9,10,11 (индексы 8,9,10)
    # В ETVP_12.4: для i in range(4, 11): M[i,i] += C*0.1
    # Здесь C — когерентность, но для чистой матрицы добавим 0.1
    for i in range(8, 11):
        C[i, i] = 2.0  # базовая диагональ
    # Связи для расширения (как в ETVP_12.4 — неявно)
    # В ETVP_12.4 нет явных связей для 9-11, только диагональ
    return C

C11 = cartan_e8_11x11()
print("Матрица 11x11:")
print(C11.astype(int))

# ============================================================
# 2. Собственные значения
# ============================================================
eigvals = np.linalg.eigvalsh(C11)
eigvals = np.sort(eigvals)[::-1]
print(f"\nСобственные значения (11):")
print(np.round(eigvals, 6))

# ============================================================
# 3. Отношения собственных значений — ищем Φ, π, √3
# ============================================================
phi = (1 + np.sqrt(5)) / 2
sqrt3 = np.sqrt(3)
pi = np.pi

print(f"\nΦ = {phi:.6f}")
print(f"√3 = {sqrt3:.6f}")
print(f"π = {pi:.6f}")

# Все попарные отношения
print("\n[1] Отношения собственных значений:")
ratios = []
for i in range(len(eigvals)):
    for j in range(i+1, len(eigvals)):
        if abs(eigvals[j]) > 1e-10:
            r = eigvals[i] / eigvals[j]
            ratios.append((i, j, r))

# Ближайшие к Φ, √3, π
for target, name in [(phi, 'Φ'), (sqrt3, '√3'), (pi, 'π')]:
    best = min(ratios, key=lambda x: abs(x[2] - target))
    print(f"  Ближайшее к {name}: λ{best[0]}/λ{best[1]} = {best[2]:.6f} (разница {abs(best[2]-target):.6f})")

# ============================================================
# 4. Отношения между соседними
# ============================================================
print("\n[2] Отношения соседних:")
for i in range(len(eigvals)-1):
    if abs(eigvals[i+1]) > 1e-10:
        r = eigvals[i] / eigvals[i+1]
        print(f"  λ{i}/λ{i+1} = {r:.6f}")

# ============================================================
# 5. Суммы/разности — может, там Φ
# ============================================================
print("\n[3] Суммы/разности:")
for i in range(len(eigvals)):
    for j in range(i+1, len(eigvals)):
        s = eigvals[i] + eigvals[j]
        d = abs(eigvals[i] - eigvals[j])
        if abs(s - phi) < 0.1:
            print(f"  λ{i}+λ{j} = {s:.6f} ≈ Φ")
        if abs(d - phi) < 0.1:
            print(f"  |λ{i}-λ{j}| = {d:.6f} ≈ Φ")

# ============================================================
# 6. 11x11 с комплексной частью (как в ETVP_12.4)
# ============================================================
print("\n[4] Комплексная 11x11 (как в ETVP_12.4):")
# Добавим мнимую часть: M_imag[i,j] = M[i,j] * tan(phi + 0.1*(i-j))
C_val = 0.87  # C_FFS
phi_field = (pi / 2.0) * (1.0 - (C_val - 0.1) / (0.99 - 0.1))
M_imag = np.zeros_like(C11)
for i in range(11):
    for j in range(11):
        M_imag[i, j] = C11[i, j] * np.tan(phi_field + 0.1 * (i - j))
M_imag = (M_imag + M_imag.T) / 2.0
M_complex = C11 + 1j * M_imag

eigvals_complex = np.linalg.eigvals(M_complex)
eigvals_complex = eigvals_complex[np.argsort(np.abs(eigvals_complex))[::-1]]
print(f"  |λ| комплексной 11x11:")
for i, ev in enumerate(eigvals_complex[:11]):
    print(f"    λ{i}: {ev:.6f}, |λ| = {abs(ev):.6f}")

# Отношения |λ|
abs_eig = np.abs(eigvals_complex)
print("\n  Отношения |λi|/|λj|:")
for i in range(len(abs_eig)):
    for j in range(i+1, len(abs_eig)):
        if abs_eig[j] > 1e-10:
            r = abs_eig[i] / abs_eig[j]
            if abs(r - phi) < 0.1:
                print(f"    |λ{i}|/|λ{j}| = {r:.6f} ≈ Φ")
            if abs(r - sqrt3) < 0.1:
                print(f"    |λ{i}|/|λ{j}| = {r:.6f} ≈ √3")

print("\nГотово.")
