import pytest

from common.exception import Error, ErrorCode
from unittest.mock import patch

from internal.infra.ml import HuggingFace
from internal.domain.entity import LLMRequest, LLMResponse


def create_huggingface_module(
        model_path="test",
        model_do_sample=True,
        model_max_new_tokens=2048,
        model_torch_dtype="float16",
        model_batch_required=False,
        model_torch_device=0,
        huggingface_api_key=None,
) -> HuggingFace:
    return HuggingFace(
        model_path=model_path,
        model_do_sample=model_do_sample,
        model_max_new_tokens=model_max_new_tokens,
        model_torch_dtype=model_torch_dtype,
        model_batch_required=model_batch_required,
        model_torch_device=model_torch_device,
        huggingface_api_key=huggingface_api_key,
    )


@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
@patch('torch.ones_like')
@pytest.mark.huggingface
def test_huggingface_model_generate_response(mock_huggingface_model, mock_tokenizer, mock_torch_ones_like):
    model = create_huggingface_module()
    model.model = mock_huggingface_model
    model.tokenizer = mock_tokenizer
    message = LLMRequest(id="test", prompt="prompt-test")
    expected_response = LLMResponse(
        id=message.id,
        results="Hello, I don't have name.",
        destination=message.destination,
    )

    mock_huggingface_model.generate.return_value = [[0.1, 0.2, 0.3]]
    mock_tokenizer.batch_decode.return_value = \
        ["What's your name?[/INST]Hello, I don't have name."]
    response = model.generate_response(message)

    assert response == expected_response
    mock_huggingface_model.generate.assert_called_once()
    mock_tokenizer.batch_decode.assert_called_once_with(
        [[0.1, 0.2, 0.3]],
        skip_special_tokens=True,
    )


@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
@patch('torch.nn.functional.pad')
@patch('torch.cat')
@patch('torch.ones_like')
@pytest.mark.huggingface
def test_huggingface_model_generate_batch_responses(
    mock_huggingface_model,
    mock_tokenizer,
    mock_torch_pad,
    mock_torch_cat,
    mock_torch_ones_like,
):
    model = create_huggingface_module()
    model.model = mock_huggingface_model
    model.tokenizer = mock_tokenizer
    messages = [LLMRequest(id="test", prompt="prompt-test")]

    expected_response = [
        LLMResponse(
            id=messages[0].id,
            results="Hello, I don't have name.",
            destination=messages[0].destination,
        ),
    ]

    mock_huggingface_model.generate.return_value = [[0.1, 0.2, 0.3]]
    mock_tokenizer.batch_decode.return_value = \
        ["What's your name?[/INST]Hello, I don't have name."]
    response = model.generate_batch_responses(messages)

    assert response == expected_response
    mock_huggingface_model.generate.assert_called_once()
    mock_tokenizer.batch_decode.assert_called_once_with(
        [[0.1, 0.2, 0.3]],
        skip_special_tokens=True,
    )


@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
@patch('torch.nn.functional.pad')
@patch('torch.cat')
@patch('torch.ones_like')
@pytest.mark.huggingface
def test_huggingface_model_generate_batch_responses_with_error(
    mock_huggingface_model,
    mock_tokenizer,
    mock_torch_cat,
    mock_torch_pad,
    mock_torch_ones_like,
):
    model = create_huggingface_module()
    model.model = mock_huggingface_model
    model.tokenizer = mock_tokenizer
    messages = [LLMRequest(id="test", prompt="prompt-test")]

    expected_error_retries = 1
    expected_error_response = [
        LLMResponse(
            id=messages[0].id,
            results=None,
            error=Error(
                code=ErrorCode.MAXIMUM_RETRIES_REACH,
                detail="Test Exception",
            ),
            destination=messages[0].destination,
        ),
    ]

    mock_huggingface_model.generate.side_effect = Exception("Test Exception")
    response = model.generate_batch_responses(messages)

    assert response == expected_error_response
    assert mock_huggingface_model.generate.call_count == expected_error_retries


@patch('transformers.AutoModelForCausalLM.from_pretrained')
@patch('transformers.AutoTokenizer.from_pretrained')
@patch('internal.infra.ml.huggingface.login')
@pytest.mark.huggingface
def test_huggingface_login_call(mock_huggingface_hub, mock_huggingface_model, mock_tokenizer):
    create_huggingface_module(huggingface_api_key="user-api-key")
    mock_huggingface_hub.assert_called_once_with(token="user-api-key")


@patch('transformers.AutoModelForCausalLM.from_pretrained')
@pytest.mark.huggingface
def test_huggingface_init_exception(mock_huggingface_model, mock_tokenizer):
    with pytest.raises(Exception) as excinfo:
        create_huggingface_module(model_path=None)

    assert str(excinfo.value) == "HUGGINGFACE_MODEL_PATH must be defined"
