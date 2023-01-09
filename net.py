import torch
import torch.nn as nn


class ResidualLayer(nn.Module):
    def __init__(self, in_c, out_c) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv1d(in_c, out_c, kernel_size=3, padding=1, bias=True),
            nn.BatchNorm1d(out_c),
            nn.ReLU(),
            nn.Conv1d(out_c, out_c, kernel_size=3, padding=1, bias=True),
            nn.BatchNorm1d(out_c)
        )
        
    def forward(self, x):
        x = nn.functional.relu(self.block(x) + x)
        return x

class ConvolutionalLayer(nn.Module):
    def __init__(self, in_c, out_c, k_size=3, padding=1) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv1d(in_c, out_c, kernel_size=k_size, padding=1, bias=True),
            nn.BatchNorm1d(out_c),
            nn.ReLU()
        )
        
    def forward(self, x):
        x = self.block(x)
        return x

class YanivDQN(nn.Module):
    def __init__(self, n_players, n_actions, residual_layers) -> None:
        input_length = (6 * (n_players - 1)) + 6

        layers = [ConvolutionalLayer(input_length, 32)]

        for _ in range(residual_layers):
            layers.append(ResidualLayer(32, 32))
        layers.append(ConvolutionalLayer(32, 32))

        # value head
        value_head_layers = [ConvolutionalLayer(32, 32), nn.Flatten(), nn.Linear(32 * 6, 32), nn.ReLU(), nn.Linear(32, 1)]

        # policy head
        policy_head_layers = [nn.Conv1d(32, 32, kernel_size=1, padding=0, bias=True), nn.Conv1d(32, 32, kernel_size=1, padding=0, bias=True), \
                              nn.BatchNorm1d(32), nn.ReLU(), nn.Flatten(), nn.Linear(32 * 6, n_actions)]


        self.layers = nn.Sequential(*layers)
        self.value_head = nn.Sequential(*value_head_layers)
        self.policy_head = nn.Sequential(*policy_head_layers)

        self.loss_fn = nn.SmoothL1Loss()

    def forward(self, x):
        x = self.layers(x)
        value = self.value_head(x)
        policy = self.policy_head(x)
        return value, policy
