import torch

from typing import Optional


def select_torch_dtype(dtype: str) -> torch.dtype:
    if dtype == "float16":
        return torch.float16
    elif dtype == "float32":
        return torch.float32
    elif dtype == "float64":
        return torch.float64
    else:
        raise Exception(f"Unsupported dtype: {dtype}")


def select_torch_device(device: Optional[int] = -1) -> torch.device:
    torch_device = torch.device("cpu")
    if torch.backends.mps.is_available() and device >= 0:
        torch_device = torch.device(f"mps:{device}")
    elif torch.cuda.is_available() and device >= 0:
        torch_device = torch.device(f"cuda:{device}")
    return torch_device
