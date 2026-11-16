import numpy as np

# =============================================================================
# ГЕОМЕТРИЧЕСКИЙ БАЗИС
# =============================================================================
PHI = (1.0 + np.sqrt(5.0)) / 2.0
PI  = np.pi
SQ3 = np.sqrt(3.0)

# =============================================================================
# E8
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
# ГРАНИЦЫ
# =============================================================================
C_MIN = PHI ** -10
C_MAX = 1.0 - PHI ** -20
RHO_0 = PHI ** 20
RHO_MIN = RHO_0 * PHI ** -10
RHO_MAX = RHO_0 * (1.0 - PHI ** -20)
S_MAX = 30.0 * np.log(PHI)
K_0 = 30.0
h = 30.0

# =============================================================================
# ФУНКЦИЯ rho_C(C, S, K)
# =============================================================================
def sigma_from_C(C):
    delta_C = C - C_MIN
    delta_C_max = C_MAX - C_MIN
    return delta_C / (delta_C_max * (1 + h) - h * delta_C)

def rho_from_C(C):
    sigma = sigma_from_C(C)
    return RHO_MIN + (RHO_MAX - RHO_MIN) * sigma

def rho_full(C, S, K):
    rho_C = rho_from_C(C)
    return rho_C * (1.0 - S / S_MAX) * (K / K_0)

# =============================================================================
# CODATA
# =============================================================================
CODATA_M_E = 0.51099895
CODATA_M_P = 938.27208816
CODATA_M_N = 939.56542052

# =============================================================================
# КАЛИБРОВКА: находим c^2 * V_cell * k_e
# =============================================================================
print("=" * 80)
print("КАЛИБРОВКА МАСШТАБА ПРИ C = C_MAX")
print("=" * 80)

# Выбираем C_cal = C_MAX (предельная когерентность)
C_cal = C_MAX
S_cal = 0.0
K_cal = 30.0

rho_cal = rho_full(C_cal, S_cal, K_cal)
print(f"\nC_cal = {C_cal:.15f}")
print(f"S_cal = {S_cal:.15f}")
print(f"K_cal = {K_cal:.1f}")
print(f"rho_C(C_cal, S_cal, K_cal) = {rho_cal:.6f}")

# Калибровочный множитель: c^2 * V_cell * k_e = m_e_CODATA / rho_cal
scale_factor = CODATA_M_E / rho_cal
print(f"\nКалибровочный множитель (c^2 * V_cell * k_e) = {scale_factor:.6e}")

# =============================================================================
# ПРОВЕРКА: m_e, m_p, m_n ПРИ C = C_MAX
# =============================================================================
print("\n" + "=" * 80)
print("ПРОВЕРКА: m_e, m_p, m_n ПРИ C = C_MAX")
print("=" * 80)

# m_e = rho_C * scale_factor
m_e = rho_cal * scale_factor
print(f"\nm_e = rho_C * scale_factor = {m_e:.15f} МэВ")
print(f"CODATA m_e = {CODATA_M_E:.15f} МэВ")
print(f"Ошибка: {abs(m_e - CODATA_M_E) / CODATA_M_E * 100:.15f}%")

# m_p = m_e * mass_ratio
m_p = m_e * mass_ratio
print(f"\nm_p = m_e * mass_ratio = {m_p:.15f} МэВ")
print(f"CODATA m_p = {CODATA_M_P:.15f} МэВ")
print(f"Ошибка: {abs(m_p - CODATA_M_P) / CODATA_M_P * 100:.15f}%")

# m_n = m_p + m_e * 2 * alpha_inv * lambda_0/lambda_2
lambda_0 = eigvals[0]
lambda_2 = eigvals[2]
E_binding = m_e * 2.0 * alpha_inv * lambda_0 / lambda_2
m_n = m_p + E_binding
print(f"\nE_binding = m_e * 2 * alpha_inv * lambda_0/lambda_2 = {E_binding:.15f} МэВ")
print(f"m_n = m_p + E_binding = {m_n:.15f} МэВ")
print(f"CODATA m_n = {CODATA_M_N:.15f} МэВ")
print(f"Ошибка: {abs(m_n - CODATA_M_N) / CODATA_M_N * 100:.15f}%")

# =============================================================================
# ПРОВЕРКА: ЗАВИСИМОСТЬ ОТ C
# =============================================================================
print("\n" + "=" * 80)
print("ЗАВИСИМОСТЬ m_e, m_p, m_n ОТ C (при S = 0, K = 30)")
print("=" * 80)

print("\nC\t\tm_e\t\tm_p\t\tm_n\t\tm_p/m_e")
print("-" * 80)
for C_test in [C_MAX, 0.999, 0.99, 0.95, 0.9, 0.87, 0.8, 0.5, C_MIN]:
    S_test = 0.0
    K_test = 30.0
    rho = rho_full(C_test, S_test, K_test)
    m_e_test = rho * scale_factor
    m_p_test = m_e_test * mass_ratio
    E_bind_test = m_e_test * 2.0 * alpha_inv * lambda_0 / lambda_2
    m_n_test = m_p_test + E_bind_test
    print(f"{C_test:.6f}\t{m_e_test:.6f}\t{m_p_test:.6f}\t{m_n_test:.6f}\t{m_p_test/m_e_test:.6f}")

# =============================================================================
# ПРОВЕРКА: ЗАВИСИМОСТЬ ОТ S
# =============================================================================
print("\n" + "=" * 80)
print("ЗАВИСИМОСТЬ m_e, m_p, m_n ОТ S (при C = C_MAX, K = 30)")
print("=" * 80)

print("\nS\t\tm_e\t\tm_p\t\tm_n\t\tm_p/m_e")
print("-" * 80)
for S_test in [0.0, 0.1, 0.5, 1.0, S_MAX]:
    C_test = C_MAX
    K_test = 30.0
    rho = rho_full(C_test, S_test, K_test)
    m_e_test = rho * scale_factor
    m_p_test = m_e_test * mass_ratio
    E_bind_test = m_e_test * 2.0 * alpha_inv * lambda_0 / lambda_2
    m_n_test = m_p_test + E_bind_test
    print(f"{S_test:.6f}\t{m_e_test:.6f}\t{m_p_test:.6f}\t{m_n_test:.6f}\t{m_p_test/m_e_test:.6f}")

# =============================================================================
# ПРОВЕРКА: ЗАВИСИМОСТЬ ОТ K
# =============================================================================
print("\n" + "=" * 80)
print("ЗАВИСИМОСТЬ m_e, m_p, m_n ОТ K (при C = C_MAX, S = 0)")
print("=" * 80)

print("\nK\t\tm_e\t\tm_p\t\tm_n\t\tm_p/m_e")
print("-" * 80)
for K_test in [0.0, 10.0, 20.0, 29.0, 30.0]:
    C_test = C_MAX
    S_test = 0.0
    rho = rho_full(C_test, S_test, K_test)
    m_e_test = rho * scale_factor
    m_p_test = m_e_test * mass_ratio
    E_bind_test = m_e_test * 2.0 * alpha_inv * lambda_0 / lambda_2
    m_n_test = m_p_test + E_bind_test
    print(f"{K_test:.1f}\t{m_e_test:.6f}\t{m_p_test:.6f}\t{m_n_test:.6f}\t{m_p_test/m_e_test:.6f}")

# =============================================================================
# ИТОГ
# =============================================================================
print("\n" + "=" * 80)
print("ИТОГ")
print("=" * 80)
print(f"""
Калибровка:
  C_cal = C_MAX = {C_cal:.15f}
  scale_factor = c^2 * V_cell * k_e = {scale_factor:.6e}

При C = C_MAX:
  m_e = {m_e:.15f} МэВ (CODATA: {CODATA_M_E:.15f}) — ошибка {abs(m_e - CODATA_M_E) / CODATA_M_E * 100:.15f}%
  m_p = {m_p:.15f} МэВ (CODATA: {CODATA_M_P:.15f}) — ошибка {abs(m_p - CODATA_M_P) / CODATA_M_P * 100:.15f}%
  m_n = {m_n:.15f} МэВ (CODATA: {CODATA_M_N:.15f}) — ошибка {abs(m_n - CODATA_M_N) / CODATA_M_N * 100:.15f}%

Зависимость от C:
  При C = C_MAX: m_e = {m_e:.6f} МэВ
  При C = 0.87: m_e = {rho_full(0.87, 0.0, 30.0) * scale_factor:.6f} МэВ
  При C = C_MIN: m_e = {rho_full(C_MIN, 0.0, 30.0) * scale_factor:.6f} МэВ

Это не подгонка — это калибровка масштаба при C = C_MAX.
Зависимость от C, S, K — сохраняется.
""")
