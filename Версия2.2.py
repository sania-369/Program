import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class ETVP_ComplexLayer(nn.Module):
    def __init__(self, dim_in, dim_out, R_max=1.0, eta_init=0.01, beta_init=0.1,
                 laplace_mode='features', use_cardioid=True):
        super().__init__()
        # Инициализация комплексных весов (адаптация Xavier для комплексных чисел)
        bound = (2.0 / dim_in) ** 0.5
        self.W_re = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.W_im = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.b_re = nn.Parameter(torch.zeros(dim_out))
        self.b_im = nn.Parameter(torch.zeros(dim_out))
        
        # Обучаемая вязкость вакуума
        self.theta_mu = nn.Parameter(torch.tensor(0.0))
        
        # Параметры стохастической самокоррекции
        self.eta = nn.Parameter(torch.tensor(eta_init))
        self.beta = nn.Parameter(torch.tensor(beta_init))
        self.R_max = R_max
        
        # Режим Лапласиана: 'features' — по признакам, 'spatial' — по пространству (2D), 'none' — отключен
        self.laplace_mode = laplace_mode
        self.use_cardioid = use_cardioid

    def _project_weights(self):
        """Z-принцип: Стабилизация через проекцию на сферу без разрушения градиентов"""
        with torch.no_grad():
            W_norm = torch.sqrt(self.W_re ** 2 + self.W_im ** 2).sum()
            if W_norm > self.R_max:
                scale = self.R_max / (W_norm + 1e-8)
                self.W_re.copy_(self.W_re * scale)
                self.W_im.copy_(self.W_im * scale)

    def complex_mul(self, x_re, x_im):
        """
        Полноценное комплексное линейное преобразование.
        Поддерживает 2D [batch, features] и 4D [batch, channels, H, W].
        """
        if x_re.dim() == 2:
            # 2D случай: [batch, dim_in] @ [dim_in, dim_out]
            out_re = x_re @ self.W_re - x_im @ self.W_im + self.b_re
            out_im = x_re @ self.W_im + x_im @ self.W_re + self.b_im
        elif x_re.dim() == 4:
            # 4D случай: [batch, C_in, H, W] @ [C_in, C_out] -> [batch, C_out, H, W]
            out_re = (torch.einsum('bihw,io->bohw', x_re, self.W_re) - 
                      torch.einsum('bihw,io->bohw', x_im, self.W_im) + 
                      self.b_re.view(1, -1, 1, 1))
            out_im = (torch.einsum('bihw,io->bohw', x_re, self.W_im) + 
                      torch.einsum('bihw,io->bohw', x_im, self.W_re) + 
                      self.b_im.view(1, -1, 1, 1))
        else:
            raise ValueError(f"Unsupported tensor dimension: {x_re.dim()}. Expected 2D or 4D.")
        
        return out_re, out_im

    def cardioid_activation(self, re, im):
        """
        Аналитическая комплексная активация Cardioid.
        f(z) = 0.5 * (1 + cos(angle(z))) * z
        """
        magnitude = torch.sqrt(re ** 2 + im ** 2 + 1e-8)
        cos_angle = re / magnitude
        scale = 0.5 * (1.0 + cos_angle)
        return scale * re, scale * im

    def complex_tanh(self, re, im):
        """Наивная комплексная активация (запасной вариант)"""
        return torch.tanh(re), torch.tanh(im)

    def laplacian_features(self, z):
        """
        Лапласиан по соседним признакам (dim=1).
        Не связывает объекты в батче.
        """
        if z.size(1) <= 2:
            return torch.zeros_like(z)
        
        z_padded = F.pad(z.unsqueeze(1), (1, 1), mode='reflect').squeeze(1)
        lap = z_padded[:, :-2] - 2 * z[:, :] + z_padded[:, 2:]
        
        return lap

    def laplacian_spatial(self, z):
        """
        Лапласиан по пространственным координатам (2D).
        Для входов вида: [batch, channels, height, width].
        """
        if z.dim() != 4:
            # Если вход не 4D, возвращаем нули
            return torch.zeros_like(z)
        
        # Padding по пространственным измерениям
        z_padded = F.pad(z, (1, 1, 1, 1), mode='reflect')
        
        # Дискретный Лапласиан 2D (4 соседа)
        lap = (z_padded[:, :, :-2, 1:-1] + 
               z_padded[:, :, 2:, 1:-1] + 
               z_padded[:, :, 1:-1, :-2] + 
               z_padded[:, :, 1:-1, 2:] - 
               4 * z)
        
        return lap

    def laplacian(self, z):
        """Выбор режима Лапласиана"""
        if self.laplace_mode == 'features':
            return self.laplacian_features(z)
        elif self.laplace_mode == 'spatial':
            return self.laplacian_spatial(z)
        elif self.laplace_mode == 'none':
            return torch.zeros_like(z)
        else:
            raise ValueError(f"Unknown laplace_mode: {self.laplace_mode}")

    def forward(self, x_re, x_im, dt=0.1):
        # 1. Применяем Z-принцип (проекция весов)
        self._project_weights()
        
        # 2. Детерминированная динамика (Полевое смещение + активация)
        f_re, f_im = self.complex_mul(x_re, x_im)
        
        if self.use_cardioid:
            f_re, f_im = self.cardioid_activation(f_re, f_im)
        else:
            f_re, f_im = self.complex_tanh(f_re, f_im)
        
        # 3. Вычисление обучаемой вязкости вакуума
        mu = F.softplus(self.theta_mu)
        
        # Дифференциальный оператор (давление среды) — исправленный Лапласиан
        lap_re = self.laplacian(x_re)
        lap_im = self.laplacian(x_im)
        
        # 4. Стохастическая самокоррекция (шум под упругим давлением градиентного поля)
        noise_re = self.eta * torch.randn_like(x_re) * torch.tanh(self.beta * x_re.abs())
        noise_im = self.eta * torch.randn_like(x_im) * torch.tanh(self.beta * x_im.abs())
        
        # 5. Интегрирование по методу Эйлера-Маруямы (Neural SDE шаг)
        sqrt_dt = math.sqrt(dt)
        
        z_re_next = x_re + dt * (f_re - mu * lap_re) + sqrt_dt * noise_re
        z_im_next = x_im + dt * (f_im - mu * lap_im) + sqrt_dt * noise_im
        
        return z_re_next, z_im_next


# --- Сквозной тест схемы обучения (Проверка Autograd) ---
if __name__ == "__main__":
    # Тест 1: Лапласиан по признакам (табличные данные)
    layer = ETVP_ComplexLayer(dim_in=16, dim_out=16, laplace_mode='features')
    
    x_re = torch.randn(10, 16, requires_grad=True)
    x_im = torch.randn(10, 16, requires_grad=True)
    
    curr_re, curr_im = x_re, x_im
    for step in range(5):
        curr_re, curr_im = layer(curr_re, curr_im, dt=0.1)
    
    loss = (curr_re**2 + curr_im**2).sum()
    loss.backward()
    
    print("--- Тест 1 (features, 2D) пройден ---")
    print("Градиент W_re:", layer.W_re.grad.abs().mean().item())
    print("Градиент Вязкости (theta_mu):", layer.theta_mu.grad.item())
    
    # Тест 2: Лапласиан по пространству (2D-картинка, 4D-тензор)
    layer2 = ETVP_ComplexLayer(dim_in=4, dim_out=8, laplace_mode='spatial')
    
    # Вход: [batch=2, channels=4, height=8, width=8]
    x_re = torch.randn(2, 4, 8, 8, requires_grad=True)
    x_im = torch.randn(2, 4, 8, 8, requires_grad=True)
    
    # Передаем в слой БЕЗ сплющивания
    curr_re, curr_im = x_re, x_im
    for step in range(3):
        curr_re, curr_im = layer2(curr_re, curr_im, dt=0.1)
    
    # Проверяем, что Лапласиан реально сработал
    lap_test = layer2.laplacian_spatial(x_re)
    print("Норма Лапласиана (spatial):", lap_test.abs().sum().item())
    assert lap_test.abs().sum() > 0, "Лапласиан не сработал!"
    
    loss = (curr_re**2 + curr_im**2).sum()
    loss.backward()
    
    print("--- Тест 2 (spatial, 4D) пройден ---")
    print("Градиент W_re:", layer2.W_re.grad.abs().mean().item())
    print("Градиент Вязкости (theta_mu):", layer2.theta_mu.grad.item())
    print("Форма выхода:", curr_re.shape)
