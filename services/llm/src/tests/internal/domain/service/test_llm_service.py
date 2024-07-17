import pytest

from internal.domain.entity import LLMRequest, LLMResponse
from internal.domain.service import LLMService


@pytest.mark.llm_service
def test_llm_service_process(mock_genai_model_inference):
    llm_service = LLMService(
        llm_model=mock_genai_model_inference,
        llm_batch_required=False,
    )
    prompt = "test"
    requests = [LLMRequest(id="test", prompt=prompt)]
    mock_response = LLMResponse(id="test", results="my name is google genai")
    mock_genai_model_inference.generate_response.return_value = mock_response

    responses = llm_service.process_messages(requests)

    assert isinstance(responses, list)
    assert len(responses) == 1
    assert responses[0].id == "test"
    assert responses[0].results == "my name is google genai"
    assert responses[0].error is None


@pytest.mark.llm_service
def test_llm_service_batch_process(mock_genai_model_inference):
    llm_service = LLMService(
        llm_model=mock_genai_model_inference,
        llm_batch_required=True,
    )
    prompt = "test"
    requests = [LLMRequest(id="test", prompt=prompt)]
    mock_response = [LLMResponse(id="test", results="my name is google genai")]
    mock_genai_model_inference.generate_batch_responses.return_value = mock_response

    responses = llm_service.process_messages(requests)

    assert isinstance(responses, list)
    assert len(responses) == 1
    assert responses[0].id == "test"
    assert responses[0].results == "my name is google genai"
    assert responses[0].error is None
