import numpy as np

PHI = (1 + np.sqrt(5)) / 2
PI = np.pi
SQRT3 = np.sqrt(3)

LAM = [2 - 2*np.cos(np.pi * m / 30) for m in [1, 7, 11, 13, 17, 19, 23, 29]]

# Протон
m_p_exp = 938.27208816  # МэВ
m_e = 0.51099895        # МэВ
mu_p_exp = 2.79284734   # μ_N
g_p_exp = 5.5856946893

# --- Масса ---
ratio = LAM[2] * PHI**5 * PI**3 * SQRT3**4 * 0.5
m_p_model = ratio * m_e
err_m = abs(m_p_model - m_p_exp) / m_p_exp * 100

print("=" * 60)
print("ПРОТОН")
print("=" * 60)
print(f"m_p/m_e модель: {ratio:.6f}")
print(f"m_p/m_e CODATA: 1836.152673")
print(f"m_p модель: {m_p_model:.4f} МэВ")
print(f"m_p CODATA: {m_p_exp:.4f} МэВ")
print(f"Ошибка массы: {err_m:.6f}%")
print()

# --- Заряд ---
# Гипотеза: Q = (N_open - N_closed) / 2
# Для протона: N_open = 3 (uud), N_closed = 2
Q_model = (3 - 2) / 2  # = 0.5
print(f"Заряд модель: {Q_model}")
print(f"Заряд CODATA: +1")
print(f"Ошибка: {abs(Q_model - 1)*100:.1f}%")
print()

# --- Магнитный момент ---
# Гипотеза: mu_p = (N_open/N_closed) * (1 + alpha/2pi)
alpha = 1/137.035999084
mu_model = (3/2) * (1 + alpha/(2*PI))
print(f"μ_p модель: {mu_model:.6f} μ_N")
print(f"μ_p CODATA: {mu_p_exp:.6f} μ_N")
print(f"Ошибка: {abs(mu_model - mu_p_exp)/mu_p_exp*100:.4f}%")
print()

# --- g-фактор ---
g_model = 2 * mu_model
print(f"g_p модель: {g_model:.6f}")
print(f"g_p CODATA: {g_p_exp:.6f}")
print(f"Ошибка: {abs(g_model - g_p_exp)/g_p_exp*100:.4f}%")
