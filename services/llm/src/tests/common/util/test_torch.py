import pytest
import torch

from unittest.mock import patch

from common.util.torch import select_torch_device, select_torch_dtype


@pytest.mark.device_torch_util
def test_select_device_default():
    device = select_torch_device()
    assert device == torch.device("cpu")


@patch("torch.backends.mps.is_available", return_value=True)
@patch("torch.cuda.is_available", return_value=False)
@pytest.mark.device_torch_util
def test_select_device_mps(mock_mps_available, mock_cuda_available):
    device = select_torch_device(0)
    assert device == torch.device("mps:0")


@patch("torch.backends.mps.is_available", return_value=False)
@patch("torch.cuda.is_available", return_value=True)
@pytest.mark.device_torch_util
def test_select_device_cuda(mock_mps_available, mock_cuda_available):
    device = select_torch_device(0)
    assert device == torch.device("cuda:0")


@patch("torch.backends.mps.is_available", return_value=False)
@patch("torch.cuda.is_available", return_value=False)
@pytest.mark.device_torch_util
def test_select_device_no_gpu(mock_mps_available, mock_cuda_available):
    device = select_torch_device(0)
    assert device == torch.device("cpu")


@patch("torch.backends.mps.is_available", return_value=True)
@patch("torch.cuda.is_available", return_value=True)
@pytest.mark.device_torch_util
def test_select_device_prefer_mps(mock_mps_available, mock_cuda_available):
    device = select_torch_device(0)
    assert device == torch.device("mps:0")


@pytest.mark.dtype_torch_util
def test_select_torch_dtype_float16():
    assert select_torch_dtype("float16") == torch.float16


@pytest.mark.dtype_torch_util
def test_select_torch_dtype_float32():
    assert select_torch_dtype("float32") == torch.float32


@pytest.mark.dtype_torch_util
def test_select_torch_dtype_float64():
    assert select_torch_dtype("float64") == torch.float64


@pytest.mark.dtype_torch_util
def test_select_torch_dtype_invalid():
    with pytest.raises(Exception) as excinfo:
        select_torch_dtype("int32")
    assert str(excinfo.value) == "Unsupported dtype: int32"


@pytest.mark.dtype_torch_util
def test_select_torch_dtype_empty():
    with pytest.raises(Exception) as excinfo:
        select_torch_dtype("")
    assert str(excinfo.value) == "Unsupported dtype: "
