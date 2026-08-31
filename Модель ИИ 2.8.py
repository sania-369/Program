import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple, Literal

class ETVP_ComplexLayer(nn.Module):
    """
    ETVP Complex Layer v2.8 — промышленная версия (аудит Гигачат).
    - Дифференцируемый Z-принцип (штраф в лоссе).
    - Устойчивый солвер Heun (вместо Эйлера) для SDE.
    - Автонормализация Лапласиана + адаптивная вязкость.
    """

    EPS: float = 1e-8

    def __init__(self,
                 dim_in: int,
                 dim_out: int,
                 R_max: float = 1.0,
                 eta: float = 0.01,
                 beta: float = 0.1,
                 laplace_mode: Literal['auto', 'spatial', 'features', 'none'] = 'auto',
                 use_cardioid: bool = True,
                 padding_mode: Literal['reflect', 'zero', 'periodic'] = 'reflect',
                 mode: Literal['increment', 'generate'] = 'increment'):
        super().__init__()

        self.dim_in = dim_in
        self.dim_out = dim_out
        self.R_max = R_max
        self.eta = eta
        self.beta = beta
        self.laplace_mode = laplace_mode
        self.use_cardioid = use_cardioid
        self.padding_mode = padding_mode
        self.mode = mode

        # Веса (Xavier)
        bound = (2.0 / dim_in) ** 0.5
        self.W_re = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.W_im = nn.Parameter(torch.randn(dim_in, dim_out) * bound)
        self.b_re = nn.Parameter(0.01 * torch.randn(dim_out))
        self.b_im = nn.Parameter(0.01 * torch.randn(dim_out))

        # Обучаемая вязкость
        self.theta_mu = nn.Parameter(torch.tensor(0.0))

        # Коэффициент штрафа для Z-принципа
        self.lambda_z = 1.0

        self.current_mode = None

    def _get_z_penalty(self) -> torch.Tensor:
        """Дифференцируемый штраф за превышение R_max."""
        W_norm = torch.abs(self.W_re + 1j * self.W_im).norm(dim=0)
        penalty = F.relu(W_norm - self.R_max).pow(2).mean()
        return self.lambda_z * penalty

    # ============================================================
    # ЛАПЛАСИАН (С АВТОНОРМАЛИЗАЦИЕЙ)
    # ============================================================

    def laplacian_spatial(self, z: torch.Tensor) -> torch.Tensor:
        if z.dim() != 4:
            return torch.zeros_like(z)
        _, _, H, W = z.shape
        pad_mode = {'reflect': 'reflect', 'zero': 'constant', 'periodic': 'circular'}.get(self.padding_mode, 'reflect')
        z_padded = F.pad(z, (1, 1, 1, 1), mode=pad_mode)
        lap = (z_padded[:, :, :-2, 1:-1] +
               z_padded[:, :, 2:, 1:-1] +
               z_padded[:, :, 1:-1, :-2] +
               z_padded[:, :, 1:-1, 2:] -
               4 * z)
        # НОРМАЛИЗАЦИЯ по размеру сетки
        return lap / (H * W + self.EPS)

    def laplacian(self, z: torch.Tensor) -> torch.Tensor:
        mode = self.laplace_mode
        if mode == 'auto':
            mode = 'spatial' if z.dim() == 4 else 'none'
        if mode == 'spatial':
            return self.laplacian_spatial(z)
        else:
            return torch.zeros_like(z)

    # ============================================================
    # КОМПЛЕКСНОЕ УМНОЖЕНИЕ + КАРДИОИДА
    # ============================================================

    def complex_mul(self, x_re: torch.Tensor, x_im: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        if x_re.dim() == 2:
            out_re = x_re @ self.W_re - x_im @ self.W_im + self.b_re
            out_im = x_re @ self.W_im + x_im @ self.W_re + self.b_im
        elif x_re.dim() == 4:
            out_re = torch.einsum('bihw,io->bohw', x_re, self.W_re) - torch.einsum('bihw,io->bohw', x_im, self.W_im) + self.b_re.view(1, -1, 1, 1)
            out_im = torch.einsum('bihw,io->bohw', x_re, self.W_im) + torch.einsum('bihw,io->bohw', x_im, self.W_re) + self.b_im.view(1, -1, 1, 1)
        else:
            raise ValueError(f"Unsupported dims: {x_re.dim()}")
        return out_re, out_im

    def cardioid_activation(self, re: torch.Tensor, im: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        angle = torch.atan2(im, re)
        scale = 0.5 * (1.0 + torch.cos(angle))
        return scale * re, scale * im

    # ============================================================
    # УСТОЙЧИВЫЙ СОЛВЕР (HEUN)
    # ============================================================

    def forward(self,
                x_re: torch.Tensor,
                x_im: torch.Tensor,
                dt: float = 0.1,
                return_intermediate: bool = False) -> Tuple[torch.Tensor, torch.Tensor] | Tuple[torch.Tensor, torch.Tensor, dict]:

        # --- Шаг 1: вычисляем производную в текущей точке ---
        f_re, f_im = self.complex_mul(x_re, x_im)
        if self.use_cardioid:
            f_re, f_im = self.cardioid_activation(f_re, f_im)
        else:
            f_re, f_im = torch.tanh(f_re), torch.tanh(f_im)

        mu = F.softplus(self.theta_mu)
        lap_re = self.laplacian(f_re)
        lap_im = self.laplacian(f_im)

        sqrt_dt = math.sqrt(dt)
        # Шум с учётом фазы
        f_abs = torch.sqrt(f_re**2 + f_im**2) + self.EPS
        noise_scale = self.eta * torch.tanh(self.beta * f_abs)
        noise_re = sqrt_dt * noise_scale * torch.randn_like(f_re) * torch.cos(torch.atan2(f_im, f_re))
        noise_im = sqrt_dt * noise_scale * torch.randn_like(f_im) * torch.sin(torch.atan2(f_im, f_re))

        if self.mode == 'increment':
            k1_re = f_re - mu * lap_re + noise_re / dt  # шум отдельно
            k1_im = f_im - mu * lap_im + noise_im / dt
        else:
            k1_re = f_re - mu * lap_re
            k1_im = f_im - mu * lap_im

        # --- Шаг 2: вычисляем производную в предсказанной точке (Heun) ---
        if self.mode == 'increment':
            x_pred_re = x_re + dt * (f_re - mu * lap_re)
            x_pred_im = x_im + dt * (f_im - mu * lap_im)
        else:
            x_pred_re = f_re - dt * mu * lap_re
            x_pred_im = f_im - dt * mu * lap_im

        f_pred_re, f_pred_im = self.complex_mul(x_pred_re, x_pred_im)
        if self.use_cardioid:
            f_pred_re, f_pred_im = self.cardioid_activation(f_pred_re, f_pred_im)
        else:
            f_pred_re, f_pred_im = torch.tanh(f_pred_re), torch.tanh(f_pred_im)

        lap_pred_re = self.laplacian(f_pred_re)
        lap_pred_im = self.laplacian(f_pred_im)

        if self.mode == 'increment':
            k2_re = f_pred_re - mu * lap_pred_re
            k2_im = f_pred_im - mu * lap_pred_im
        else:
            k2_re = f_pred_re - mu * lap_pred_re
            k2_im = f_pred_im - mu * lap_pred_im

        # --- Шаг 3: усреднение (Heun) ---
        if self.mode == 'increment':
            z_re_next = x_re + dt * (k1_re + k2_re) / 2 + noise_re
            z_im_next = x_im + dt * (k1_im + k2_im) / 2 + noise_im
        else:
            z_re_next = (f_re + f_pred_re) / 2 - dt * mu * (lap_re + lap_pred_re) / 2
            z_im_next = (f_im + f_pred_im) / 2 - dt * mu * (lap_im + lap_pred_im) / 2

        if return_intermediate:
            intermediates = {
                'f': (f_re, f_im),
                'lap': (lap_re, lap_im),
                'noise': (noise_re, noise_im),
                'mu': mu,
                'dt': dt
            }
            return z_re_next, z_im_next, intermediates

        return z_re_next, z_im_next
