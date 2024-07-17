import pytest

from common.dto import ConsumedMessageDTO
from common.exception import Error, ErrorCode
from internal.app.data_mapper import MQRequestDataMapper, MQResponseDataMapper
from internal.app.service import VectorApplicationService
from internal.domain.entity import VectorResponse


@pytest.mark.vector_app_service
def test_vector_application_service(
    mock_vector_service,
    mock_producer_service,
    mock_error_producer_service,
):
    request_data_mapper = MQRequestDataMapper()
    response_data_mapper = MQResponseDataMapper()
    app_service = VectorApplicationService(
        vector_service=mock_vector_service,
        producer_service=mock_producer_service,
        error_producer_service=mock_error_producer_service,
        mq_request_data_mapper=request_data_mapper,
        mq_response_data_mapper=response_data_mapper,
        service_name = "test_service",
    )

    payloads = [
        ConsumedMessageDTO(
            id="test_1",
            source="vector-request",
            message={
                "texts": [
                    "how much protein should a female eat",
                    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
                ]
            },
        ),
        ConsumedMessageDTO(
            id="test_2",
            source="vector-request",
            message={
                "texts": [
                    "南瓜的家常做法",
                    "清炒南瓜丝 原料:嫩南瓜半个 调料:葱、盐、白糖、鸡精 做法: 1、南瓜用刀薄薄的削去表面一层皮     ,用勺子刮去瓤 2、擦成细丝(没有擦菜板就用刀慢慢切成细丝) 3、锅烧热放油,入葱花煸出香味 4、入南瓜丝快速翻炒一分钟左右,     放盐、一点白糖和鸡精调味出锅 2.香葱炒南瓜 原料:南瓜1只 调料:香葱、蒜末、橄榄油、盐 做法: 1、将南瓜去皮,切成片 2、油     锅8成热后,将蒜末放入爆香 3、爆香后,将南瓜片放入,翻炒 4、在翻炒的同时,可以不时地往锅里加水,但不要太多 5、放入盐,炒匀      6、南瓜差不多软和绵了之后,就可以关火 7、撒入香葱,即可出锅"
                ]
            },
        ),
        ConsumedMessageDTO(
            id="test_3",
            source="vector-request",
            message={
                "texts": [
                    "how much protein should a female eat",
                    "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
                ] * 100
            },
        ),
    ]

    mock_responses = [
        VectorResponse(
            id="test_1",
            results=[[0.1, 0.2, 0.3]],
        ),
        VectorResponse(
            id="test_2",
            results=[[0.1, 0.2, 0.3]],
        ),
        VectorResponse(
            id="test_3",
            results=None,
            error=Error(
                code=ErrorCode.REQUEST_SIZE_EXCEED,
                detail="test error"
            )
        ),
    ]
    mock_vector_service.process_messages.return_value = mock_responses
    app_service.handle_queue(payloads)
    mock_vector_service.process_messages.assert_called_once()
    assert mock_producer_service.publish_message.call_count == len(payloads)
    mock_error_producer_service.publish_message.assert_called_once()

