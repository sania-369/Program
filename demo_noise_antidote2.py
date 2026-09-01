import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import math

# =============================================================================
# 0. ИНИЦИАЛИЗАЦИЯ И РАСЧЁТ ДАННЫХ ДЛЯ ТЕСТА
# =============================================================================
torch.manual_seed(42)
np.random.seed(42)

steps = 300
x_vals = np.linspace(0, 10 * np.pi, steps)
clean_signal = np.sin(x_vals)
noise = np.random.normal(0, 0.8, steps)  # 80% шума
noisy_signal = clean_signal + noise

# Подготовка тензоров для обучения
noisy_tensor = torch.tensor(noisy_signal, dtype=torch.float32).view(-1, 1)
clean_tensor = torch.tensor(clean_signal, dtype=torch.float32).view(-1, 1)

X_train = noisy_tensor[:-1]
y_train = clean_tensor[1:]

# =============================================================================
# 1. МОДЕЛИ (StandardNet vs ETVP_ComplexLayer)
# =============================================================================
class SimpleNet(nn.Module):
    def __init__(self, hidden_dim=64):
        super().__init__()
        self.fc1 = nn.Linear(1, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)
    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))

class ETVP_ComplexLayer(nn.Module):
    def __init__(self, dim_in, dim_out, R_max=1.0):
        super().__init__()
        self.R_max = R_max
        bound = (2.0 / dim_in) ** 0.5
        self.W_re = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.W_im = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.b_re = nn.Parameter(torch.randn(dim_out) * 0.01)
        self.b_im = nn.Parameter(torch.randn(dim_out) * 0.01)
    def forward(self, x_re, x_im):
        out_re = x_re @ self.W_re - x_im @ self.W_im + self.b_re
        out_im = x_re @ self.W_im + x_im @ self.W_re + self.b_im
        angle = torch.atan2(out_im, out_re)
        scale = 0.5 * (1.0 + torch.cos(angle))  # Кардиоидный фильтр
        return scale * out_re, scale * out_im
    def get_z_penalty(self):
        W_norm = torch.sqrt(self.W_re.norm(dim=0)**2 + self.W_im.norm(dim=0)**2)
        return torch.relu(W_norm - self.R_max).pow(2).mean()

class ETVPNet(nn.Module):
    def __init__(self, hidden_dim=64):
        super().__init__()
        self.layer1 = ETVP_ComplexLayer(1, hidden_dim)
        self.layer2 = ETVP_ComplexLayer(hidden_dim, 1)
    def forward(self, x):
        x_re, x_im = self.layer1(x, torch.zeros_like(x))
        x_re, _ = self.layer2(x_re, x_im)
        return x_re
    def get_penalty(self):
        return self.layer1.get_z_penalty() + self.layer2.get_z_penalty()

# =============================================================================
# 2. ПРОЦЕСС ОБУЧЕНИЯ
# =============================================================================
epochs = 500

standard_model = SimpleNet()
opt_std = torch.optim.Adam(standard_model.parameters(), lr=0.01)
criterion = nn.MSELoss()
std_losses = []

etvp_model = ETVPNet()
opt_etvp = torch.optim.Adam(etvp_model.parameters(), lr=0.01)
etvp_losses = []

for epoch in range(epochs):
    # Обучение StandardNet
    opt_std.zero_grad()
    pred_std = standard_model(X_train)
    loss_std = criterion(pred_std, y_train)
    loss_std.backward()
    opt_std.step()
    std_losses.append(loss_std.item())

    # Обучение ETVPNet
    opt_etvp.zero_grad()
    pred_etvp = etvp_model(X_train)
    loss_etvp = criterion(pred_etvp, y_train) + 0.01 * etvp_model.get_penalty()
    loss_etvp.backward()
    opt_etvp.step()
    etvp_losses.append(loss_etvp.item())

# Получение итоговых предсказаний
with torch.no_grad():
    std_final_pred = standard_model(X_train).numpy().flatten()
    etvp_final_pred = etvp_model(X_train).numpy().flatten()

# =============================================================================
# 3. ПОСТРОЕНИЕ ГРАФИКА С ИДЕАЛЬНОЙ ЖЁСТКОЙ КОМПОНОВКОЙ
# =============================================================================
# Явно задаём размер полотна и цвет фона
fig = plt.figure(figsize=(15, 10), facecolor='#0B0F19')
plt.rcParams['text.color'] = '#E2E8F0'
plt.rcParams['axes.labelcolor'] = '#94A3B8'
plt.rcParams['xtick.color'] = '#64748B'
plt.rcParams['ytick.color'] = '#64748B'

# Задаём жесткую сетку 2х2 с фиксированными зазорами, исключая перекрытия
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25, left=0.08, right=0.95, top=0.90, bottom=0.08)

# Стилизация графиков
ax_data  = fig.add_subplot(gs[0, 0], facecolor='#111827')
ax_loss  = fig.add_subplot(gs[0, 1], facecolor='#111827')
ax_std   = fig.add_subplot(gs[1, 0], facecolor='#111827')
ax_etvp  = fig.add_subplot(gs[1, 1], facecolor='#111827')

# Общий заголовок
fig.suptitle('🌀 ETVP Complex Layer v3.0 — МЕТРОЛОГИЧЕСКИЙ СТРЕСС-ТЕСТ (80% ШУМА)', 
             fontsize=16, fontweight='bold', color='#38BDF8', y=0.96)

# --- 1. Окно: Исходные данные ---
ax_data.plot(x_vals, clean_signal, color='#38BDF8', linewidth=2, label='Чистый сигнал (Цель)')
ax_data.scatter(x_vals, noisy_signal, color='#EF4444', s=4, alpha=0.3, label='Наведенный шум (80%)')
ax_data.set_title('Входной деформированный поток', fontsize=12, fontweight='bold', pad=10)
ax_data.grid(True, color='#1F2937', linestyle='--')
ax_data.legend(facecolor='#1F2937', edgecolor='none', loc='upper right')

# --- 2. Окно: Сходимость обучения (Логарифмическая шкала) ---
ax_loss.plot(std_losses, color='#EF4444', linewidth=2, label='StandardNet (Linear + ReLU)')
ax_loss.plot(etvp_losses, color='#10B981', linewidth=2, label='ETVPNet (Complex + Cardioid)')
ax_loss.set_yscale('log')
ax_loss.set_title('Скорость фильтрации среды (Loss MSE)', fontsize=12, fontweight='bold', pad=10)
ax_loss.grid(True, color='#1F2937', linestyle='--')
ax_loss.legend(facecolor='#1F2937', edgecolor='none', loc='upper right')

# --- 3. Окно: Результат StandardNet ---
ax_std.plot(x_vals[1:], clean_signal[1:], color='#38BDF8', linewidth=1.5, linestyle=':', label='Цель')
ax_std.plot(x_vals[1:], std_final_pred, color='#F59E0B', linewidth=2, label='Предсказание ReLU')
ax_std.set_title(f'Аппроксимация StandardNet (Финальная ошибка: {std_losses[-1]:.5f})', 
                 fontsize=11, fontweight='bold', color='#EF4444', pad=10)
ax_std.grid(True, color='#1F2937', linestyle='--')
ax_std.legend(facecolor='#1F2937', edgecolor='none', loc='upper right')

# --- 4. Окно: Результат ETVPNet ---
ax_etvp.plot(x_vals[1:], clean_signal[1:], color='#38BDF8', linewidth=1.5, linestyle=':', label='Цель')
ax_etvp.plot(x_vals[1:], etvp_final_pred, color='#10B981', linewidth=2, label='Восстановленное поле')
ax_etvp.set_title(f'Синтез ETVPNet (Финальная ошибка: {etvp_losses[-1]:.5f})', 
                  fontsize=11, fontweight='bold', color='#10B981', pad=10)
ax_etvp.grid(True, color='#1F2937', linestyle='--')
ax_etvp.legend(facecolor='#1F2937', edgecolor='none', loc='upper right')

# Фиксация и сохранение
plt.savefig('etvp_benchmark_perfect.png', dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
print("✅ Идеальный график успешно сгенерирован и сохранен как 'etvp_benchmark_perfect.png'")
plt.show()
