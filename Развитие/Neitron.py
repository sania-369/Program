import numpy as np
PHI = (1+np.sqrt(5))/2
PI = np.pi
Z = np.sqrt(3)

m_e = 0.511
alpha_inv = 137.036
E_bind = 0.782

# E/m_e
ratio = E_bind/m_e  # 1.531

# Через α
for n in range(-3, 4):
    val = alpha_inv**n
    print(f"α^{n} = {val:.6e}, E/(m_e·α^{n}) = {ratio/val:.4f}")

# Ищем f = ratio/α^n
print(f"\nПоиск f = ratio/α^n:")
for n in range(-2, 3):
    f = ratio * (1/alpha_inv)**n
    print(f"n={n}: f = {f:.6f}")
    # Ищем f из Φ, π, √3
    for a in range(-10, 11):
        for b in range(-6, 7):
            for c in range(-6, 7):
                val = PHI**a * PI**b * Z**c
                err = abs(val - f) / f * 100
                if err < 0.5:
                    print(f"  Φ^{a}·π^{b}·√3^{c} = {val:.6f}  ошибка {err:.4f}%")
