import numpy as np
from itertools import combinations

# =============================================================================
# ТОПОЛОГИЧЕСКИЕ КОНСТАНТЫ E8
# =============================================================================
h = 30
r = 8
D = 248
m = [1, 7, 11, 13, 17, 19, 23, 29]

# =============================================================================
# БАЗОВЫЕ ЧИСЛА (все, что есть в E8 и Триаде)
# =============================================================================
base = {
    "h": h, "r": r, "D": D,
    "m1": 1, "m2": 7, "m3": 11, "m4": 13,
    "m5": 17, "m6": 19, "m7": 23, "m8": 29,
    "h/2": h/2, "h/3": h/3, "h/5": h/5, "h/6": h/6,
    "h/10": h/10, "h/15": h/15,
    "2h": 2*h, "3h": 3*h,
    "r+2": r+2, "r+4": r+4, "r-2": r-2,
    "D/h": D/h, "D/r": D/r, "D/(r+2)": D/(r+2),
    "h-r": h-r, "h+r": h+r, "h*r": h*r,
    "Φ": (1+np.sqrt(5))/2, "π": np.pi, "√3": np.sqrt(3),
}

# =============================================================================
# ЦЕЛЕВЫЕ ЧИСЛА (степени и множители)
# =============================================================================
targets = {
    "12 (Φ в W_ALPHA)": 12,
    "5 (Φ в W_MASS)": 5,
    "-43 (Φ в W_G)": -43,
    "-4 (π в W_ALPHA)": -4,
    "3 (π в W_MASS)": 3,
    "-1 (π в W_G)": -1,
    "3 (√3 в W_ALPHA)": 3,
    "4 (√3 в W_MASS)": 4,
    "-5 (√3 в W_G)": -5,
    "10 (множитель mod_alpha)": 10,
    "2 (множитель W_ALPHA)": 2,
    "0.5 (множитель W_MASS)": 0.5,
}

# =============================================================================
# ПОИСК БЛИЖАЙШИХ КОМБИНАЦИЙ
# =============================================================================
def closest_combinations(target, top_n=5):
    """Ищет top_n ближайших комбинаций базовых чисел к target."""
    results = []
    names = list(base.keys())
    vals = [base[n] for n in names]
    
    # 1. Одиночные числа
    for i, v in enumerate(vals):
        results.append((abs(v - target), f"{names[i]}", v))
    
    # 2. Суммы и разности двух чисел
    for i, j in combinations(range(len(vals)), 2):
        results.append((abs(vals[i] + vals[j] - target), f"{names[i]} + {names[j]}", vals[i] + vals[j]))
        results.append((abs(vals[i] - vals[j] - target), f"{names[i]} - {names[j]}", vals[i] - vals[j]))
        results.append((abs(vals[j] - vals[i] - target), f"{names[j]} - {names[i]}", vals[j] - vals[i]))
    
    # 3. Произведения и отношения двух чисел
    for i, j in combinations(range(len(vals)), 2):
        results.append((abs(vals[i] * vals[j] - target), f"{names[i]} * {names[j]}", vals[i] * vals[j]))
        if abs(vals[j]) > 1e-9:
            results.append((abs(vals[i] / vals[j] - target), f"{names[i]} / {names[j]}", vals[i] / vals[j]))
        if abs(vals[i]) > 1e-9:
            results.append((abs(vals[j] / vals[i] - target), f"{names[j]} / {names[i]}", vals[j] / vals[i]))
    
    # 4. Три числа: (a+b)*c, (a-b)*c, a*b+c, a*b-c
    for i, j, k in combinations(range(len(vals)), 3):
        for op1, op2, desc in [
            (lambda a,b: a+b, lambda x,c: x*c, f"({names[i]} + {names[j]}) * {names[k]}"),
            (lambda a,b: a-b, lambda x,c: x*c, f"({names[i]} - {names[j]}) * {names[k]}"),
            (lambda a,b: a*b, lambda x,c: x+c, f"{names[i]} * {names[j]} + {names[k]}"),
            (lambda a,b: a*b, lambda x,c: x-c, f"{names[i]} * {names[j]} - {names[k]}"),
        ]:
            try:
                val = op2(op1(vals[i], vals[j]), vals[k])
                results.append((abs(val - target), desc, val))
            except:
                pass
    
    # Сортируем по близости и убираем дубликаты
    results.sort(key=lambda x: x[0])
    seen = set()
    unique = []
    for diff, desc, val in results:
        key = (desc, round(val, 6))
        if key not in seen:
            seen.add(key)
            unique.append((diff, desc, val))
        if len(unique) >= top_n:
            break
    
    return unique

# =============================================================================
# ВЫВОД
# =============================================================================
print("=" * 80)
print("БЛИЖАЙШИЕ КОМБИНАЦИИ ИЗ E8 К ЦЕЛЕВЫМ ЧИСЛАМ")
print("=" * 80)
print(f"h={h}, r={r}, D={D}")
print(f"m={m}")

for target_name, target_val in targets.items():
    print(f"\n--- {target_name} = {target_val} ---")
    combos = closest_combinations(target_val, top_n=5)
    for diff, desc, val in combos:
        rel_err = (diff / abs(target_val) * 100) if target_val != 0 else diff * 100
        marker = "✅" if rel_err < 5 else ("⚠️" if rel_err < 20 else "❌")
        print(f"  {marker} {desc} = {val:.6f}  (отклонение: {diff:.6f}, {rel_err:.2f}%)")
