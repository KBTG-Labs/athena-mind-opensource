import pytest

from common.dto import ConsumedMessageDTO
from common.exception import Error, ErrorCode
from internal.app.data_mapper import MQRequestDataMapper, MQResponseDataMapper
from internal.app.service import LLMApplicationService
from internal.domain.entity import LLMResponse


@pytest.mark.llm_app_service
def test_llm_application_service(
    mock_llm_service,
    mock_producer_service,
    mock_error_producer_service,
):
    request_data_mapper = MQRequestDataMapper()
    response_data_mapper = MQResponseDataMapper()
    app_service = LLMApplicationService(
        llm_service=mock_llm_service,
        producer_service=mock_producer_service,
        error_producer_service=mock_error_producer_service,
        mq_request_data_mapper=request_data_mapper,
        mq_response_data_mapper=response_data_mapper,
        service_name="test_service",
    )

    payloads = [
        ConsumedMessageDTO(
            id="test_1",
            source="llm-request",
            message={
                "text": "hello what's your name"
            },
        ),
        ConsumedMessageDTO(
            id="test_2",
            source="llm-request",
            message={
                "text": "hello what's your name"
            },
        ),
        ConsumedMessageDTO(
            id="test_3",
            source="llm-request",
            message={
                "text": "hello what's your name"
            },
        )
    ]

    mock_responses = [
        LLMResponse(
            id="test_1",
            results="my name is google genai",
        ),
        LLMResponse(
            id="test_2",
            results="my name is google genai",
        ),
        LLMResponse(
            id="test_3",
            results=None,
            error=Error(
                code=ErrorCode.MAXIMUM_RETRIES_REACH,
                detail="test error"
            )
        ),
    ]

    mock_llm_service.process_messages.return_value = mock_responses
    app_service.handle_queue(payloads)

    mock_llm_service.process_messages.assert_called_once()
    assert mock_producer_service.publish_message.call_count == len(payloads)

    error_response_dto = response_data_mapper.to_dal_entity(mock_responses[2])
    error_response_dto.source = "test_service"
    assert mock_producer_service.publish_message.call_count == len(payloads)
    assert mock_error_producer_service.publish_message.call_count == 1
