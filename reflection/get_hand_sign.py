from typing import List

import torch
import torch.nn as nn
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, 'models/handsign.pt')

SIGNS = {
    "0": "OK",
    "1": "THUMB_UP",
    "2": "TWO",
    "3": "THREE",
    "4": "SPIDERMAN",
    "5": "OPEN_HAND",
    "6": "FIST",
    "7": "PINCH",
    "8": "THUMB_DOWN",
    "9": "INDEX",
    "10": "MIDDLE",
    "11": "LITTLE"
}


def onehot(index: int, size: int = 16) -> List[int]:
    list = [0 for i in range(size)]
    list[index] = 1
    return list


class signclassifier(nn.Module):
    def __init__(self) -> None:
        super(signclassifier, self).__init__()

        self.func = nn.Sequential(
            nn.Linear(21*2, 64),
            nn.ReLU(inplace=True),

            nn.Linear(64, 32),
            nn.ReLU(inplace=True),

            nn.Linear(32, 16),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:

        y = x.view(-1, 21*2)
        z = self.func(y)

        return z


def init(device: str = "cuda"):
    model = signclassifier().to(device).eval()
    try:
        model.load_state_dict(torch.load(model_path))
    except:
        print("No model saved")
        return
    return model

def find_gesture(model, data: List[List]) -> List:
    data = torch.tensor(data).unsqueeze(0).cuda()
    out = model(data)
    return [SIGNS[str(torch.argmax(out.squeeze(0)).item())], torch.max(out.squeeze(0)).item()]
