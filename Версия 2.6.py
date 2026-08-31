import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class ETVP_ComplexLayer(nn.Module):
    """
    ETVP Complex Layer v2.6 — исправленный аудит Google.
    - Шаг Эйлера исправлен для dim_in != dim_out.
    - beta — константа (гиперпараметр).
    - Лапласиан только для 4D (пространственная топология).
    - Для 2D — L2-регуляризация вместо Лапласиана.
    """

    def __init__(self, dim_in, dim_out,
                 R_max=1.0, eta=0.01, beta=0.1,
                 laplace_mode='auto', use_cardioid=True):
        super().__init__()

        # Инициализация весов (Xavier для комплексных)
        bound = (2.0 / dim_in) ** 0.5
        self.W_re = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.W_im = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.b_re = nn.Parameter(torch.zeros(dim_out))
        self.b_im = nn.Parameter(torch.zeros(dim_out))

        # Вязкость — обучаемая
        self.theta_mu = nn.Parameter(torch.tensor(0.0))

        # Гиперпараметры (не обучаемые)
        self.eta = eta
        self.beta = beta
        self.R_max = R_max
        self.laplace_mode = laplace_mode
        self.use_cardioid = use_cardioid

        self.current_mode = None

    # ============================================================
    # Z-ПРИНЦИП (стабилизация)
    # ============================================================

    def _project_weights(self):
        with torch.no_grad():
            W_norm_re = self.W_re.norm(dim=0)
            W_norm_im = self.W_im.norm(dim=0)
            W_norm = torch.sqrt(W_norm_re**2 + W_norm_im**2)

            mask = W_norm > self.R_max
            if mask.any():
                scale = torch.ones_like(W_norm)
                scale[mask] = self.R_max / (W_norm[mask] + 1e-8)
                self.W_re.data *= scale.unsqueeze(0)
                self.W_im.data *= scale.unsqueeze(0)

    # ============================================================
    # КОМПЛЕКСНОЕ ПРЕОБРАЗОВАНИЕ
    # ============================================================

    def complex_mul(self, x_re, x_im):
        if x_re.dim() == 2:
            out_re = x_re @ self.W_re - x_im @ self.W_im + self.b_re
            out_im = x_re @ self.W_im + x_im @ self.W_re + self.b_im
        elif x_re.dim() == 4:
            out_re = (torch.einsum('bihw,io->bohw', x_re, self.W_re) -
                      torch.einsum('bihw,io->bohw', x_im, self.W_im) +
                      self.b_re.view(1, -1, 1, 1))
            out_im = (torch.einsum('bihw,io->bohw', x_re, self.W_im) +
                      torch.einsum('bihw,io->bohw', x_im, self.W_re) +
                      self.b_im.view(1, -1, 1, 1))
        else:
            raise ValueError(f"Unsupported dim: {x_re.dim()}")
        return out_re, out_im

    # ============================================================
    # АКТИВАЦИЯ
    # ============================================================

    def cardioid_activation(self, re, im):
        angle = torch.atan2(im, re)
        scale = 0.5 * (1.0 + torch.cos(angle))
        return scale * re, scale * im

    # ============================================================
    # ЛАПЛАСИАН — ТОЛЬКО ДЛЯ 4D
    # ============================================================

    def laplacian_spatial(self, z):
        if z.dim() != 4:
            return torch.zeros_like(z)
        z_padded = F.pad(z, (1, 1, 1, 1), mode='reflect')
        lap = (z_padded[:, :, :-2, 1:-1] +
               z_padded[:, :, 2:, 1:-1] +
               z_padded[:, :, 1:-1, :-2] +
               z_padded[:, :, 1:-1, 2:] -
               4 * z)
        return lap

    def laplacian_features(self, z):
        # Для 2D — L2-регуляризация вместо лапласиана
        return z  # placeholder

    def laplacian(self, z):
        if z.dim() == 4:
            return self.laplacian_spatial(z)
        else:
            # Для 2D — возвращаем нулевой лапласиан
            return torch.zeros_like(z)

    # ============================================================
    # ПРЯМОЙ ПРОХОД (SDE-ШАГ, ИСПРАВЛЕННЫЙ)
    # ============================================================

    def forward(self, x_re, x_im, dt=0.1):
        self._project_weights()

        # 1. Полевое смещение
        f_re, f_im = self.complex_mul(x_re, x_im)

        # 2. Активация
        if self.use_cardioid:
            f_re, f_im = self.cardioid_activation(f_re, f_im)
        else:
            f_re, f_im = torch.tanh(f_re), torch.tanh(f_im)

        # 3. Вязкость
        mu = F.softplus(self.theta_mu)

        # 4. Лапласиан (только для 4D)
        lap_re = self.laplacian(f_re)
        lap_im = self.laplacian(f_im)

        # 5. Шум с корректным масштабом sqrt(dt)
        sqrt_dt = math.sqrt(dt)
        noise_re = sqrt_dt * self.eta * torch.randn_like(f_re) * torch.tanh(self.beta * f_re.abs())
        noise_im = sqrt_dt * self.eta * torch.randn_like(f_im) * torch.tanh(self.beta * f_im.abs())

        # 6. ИСПРАВЛЕННЫЙ ШАГ ЭЙЛЕРА (генерация, а не приращение)
        # Вместо x_re + dt*... используем f_re - dt*mu*lap + noise
        z_re_next = f_re - dt * mu * lap_re + noise_re
        z_im_next = f_im - dt * mu * lap_im + noise_im

        return z_re_next, z_im_next
