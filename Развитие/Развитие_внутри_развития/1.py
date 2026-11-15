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
# ВСЕ КОЭФФИЦИЕНТЫ ИЗ E8 (БЕЗ ОКРУГЛЕНИЯ)
# =============================================================================
W_ALPHA = (PHI**12) * (PI**-4) * (SQ3**3) * 2
W_MASS  = (PHI**5)  * (PI**3)  * (SQ3**4) * 0.5
W_G     = (PHI**-43) * (PI**-1) * (SQ3**-5) * 2

alpha_inv = eigvals[7] * W_ALPHA          # 1/α из E8
mass_ratio = eigvals[2] * W_MASS          # m_p/m_e из E8
G_E8 = eigvals[3] * W_G                   # G из E8

GAMMA = 1.0 / (PHI ** 12)                 # γ из E8
ETA   = 1.0 / (PHI ** 10)                 # η из E8
k_e_F = GAMMA / ETA                       # k_e = γ/η = 1/Φ²

# =============================================================================
# АБСОЛЮТНЫЕ МАССЫ (из E8, без CODATA)
# =============================================================================
# Масштаб энергии: E_scale = m_e / k_e, но m_e из E8 пока не выведен.
# Используем соотношение: m_p = m_e * mass_ratio, m_n = m_p + E_binding
# E_binding = m_e * 2 * alpha_inv * λ[0]/λ[2] (из v13.3)
E_binding_E8 = (1.0 / mass_ratio) * 2.0 * alpha_inv * eigvals[0] / eigvals[2]
# (в единицах m_e, т.к. m_e = 1)

# В единицах m_e:
m_e_E8 = 1.0
m_p_E8 = mass_ratio
m_n_E8 = m_p_E8 + E_binding_E8

# =============================================================================
# CODATA (только для сравнения)
# =============================================================================
CODATA_M_E = 0.51099895
CODATA_M_P = 938.27208816
CODATA_M_N = 939.56542052
CODATA_DIFF = CODATA_M_N - CODATA_M_P

print("=" * 80)
print("ВСЕ КОЭФФИЦИЕНТЫ ИЗ E8 (без округления)")
print("=" * 80)
print(f"\n1/α     = {alpha_inv:.15f}")
print(f"m_p/m_e = {mass_ratio:.15f}")
print(f"G       = {G_E8:.15e}")
print(f"γ       = {GAMMA:.15f}")
print(f"η       = {ETA:.15f}")
print(f"k_e     = γ/η = {k_e_F:.15f}")

# =============================================================================
# ПРОВЕРКА m_n - m_p ЧЕРЕЗ k_e = γ/η
# =============================================================================
print("\n" + "=" * 80)
print("ПРОВЕРКА m_n - m_p ЧЕРЕЗ k_e = γ/η (все из E8)")
print("=" * 80)

# E_scale = m_e / k_e (в единицах m_e, т.е. m_e = 1)
E_scale_E8 = m_e_E8 / k_e_F

print(f"\nE_scale (в единицах m_e) = {E_scale_E8:.15f}")

# Гипотезы для m_n - m_p (в единицах m_e)
hypotheses = [
    ("m_e", m_e_E8),
    ("E_scale · (1 - k_e)", E_scale_E8 * (1 - k_e_F)),
    ("E_scale · k_e · Φ", E_scale_E8 * k_e_F * PHI),
    ("E_scale · k_e / Φ", E_scale_E8 * k_e_F / PHI),
    ("E_scale · (1 - k_e) · Φ", E_scale_E8 * (1 - k_e_F) * PHI),
    ("m_e · Φ", m_e_E8 * PHI),
    ("m_e · (1 + k_e)", m_e_E8 * (1 + k_e_F)),
    ("m_e · (1 + k_e) · Φ", m_e_E8 * (1 + k_e_F) * PHI),
]

print(f"\nГипотезы для (m_n - m_p)/m_e:")
for name, val in hypotheses:
    print(f"  {name}: {val:.15f}")

# CODATA для сравнения (в единицах m_e)
CODATA_DIFF_ME = CODATA_DIFF / CODATA_M_E
print(f"\nCODATA (m_n - m_p)/m_e = {CODATA_DIFF_ME:.15f}")

# Ошибки
print(f"\nОшибки:")
for name, val in hypotheses:
    err = abs(val - CODATA_DIFF_ME) / CODATA_DIFF_ME * 100
    print(f"  {name}: {err:.6f}%")

# =============================================================================
# ПРОВЕРКА АБСОЛЮТНЫХ МАСС (в МэВ, через E_scale из E8)
# =============================================================================
print("\n" + "=" * 80)
print("АБСОЛЮТНЫЕ МАССЫ (в МэВ, через E_scale из E8)")
print("=" * 80)

# E_scale в МэВ = m_e_CODATA / k_e_F (потому что m_e_CODATA известна)
# Но это использует CODATA. Вместо этого: E_scale = m_e_E8 * (1 МэВ / ?)
# Пока m_e в МэВ не выведен, используем соотношение:
# m_n - m_p = E_scale * (гипотеза)
# где E_scale = m_e / k_e, а m_e в МэВ — из CODATA (для проверки)

E_scale_MeV = CODATA_M_E / k_e_F

print(f"\nE_scale (МэВ) = m_e_CODATA / k_e = {E_scale_MeV:.15f}")

for name, val in hypotheses:
    # val в единицах m_e, переводим в МэВ: val * m_e_CODATA
    val_MeV = val * CODATA_M_E
    err = abs(val_MeV - CODATA_DIFF) / CODATA_DIFF * 100
    print(f"  {name}: {val_MeV:.15f} МэВ (ошибка {err:.6f}%)")

print(f"\nCODATA (m_n - m_p) = {CODATA_DIFF:.15f} МэВ")

# =============================================================================
# ИТОГ
# =============================================================================
print("\n" + "=" * 80)
print("ИТОГ")
print("=" * 80)

best = min(hypotheses, key=lambda x: abs(x[1] - CODATA_DIFF_ME))
print(f"\nЛучшая гипотеза: m_n - m_p = {best[0]}")
print(f"  В единицах m_e: {best[1]:.15f}")
print(f"  CODATA:         {CODATA_DIFF_ME:.15f}")
print(f"  Ошибка:         {abs(best[1] - CODATA_DIFF_ME) / CODATA_DIFF_ME * 100:.6f}%")

print(f"\nВсе коэффициенты — из E8. CODATA — только для сравнения.")
