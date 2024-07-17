import pytest

from common.exception import Error, ErrorCode
from internal.domain.entity import VectorRequest, VectorResponse
from internal.domain.service import VectorService


@pytest.mark.vector_service
def test_vector_serivce_process_one_request_success(mock_vector_model_inference):  
    vector_service = VectorService(vector_model=mock_vector_model_inference)
    request = VectorRequest(
        id="test_1",
        texts= [
            "how much protein should a female eat",
            "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
        ]
    )

    mock_vector_model_inference.process.return_value = [[0.1, 0.2, 0.3]]
    response = vector_service.process_message(request)
    mock_vector_model_inference.process.assert_called_once_with(request.to_request())
    assert isinstance(response, VectorResponse)
    assert response.id == "test_1"
    assert response.results == [[0.1, 0.2, 0.3]]
    assert response.error is None

@pytest.mark.vector_service
def test_vector_serivce_process_one_request_error_request_size_exceed(mock_vector_model_inference):  
    vector_service = VectorService(vector_model=mock_vector_model_inference)
    request = VectorRequest(
        id="test_1",
        texts= [
            "how much protein should a female eat",
            "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
        ] * 100
    )

    response = vector_service.process_message(request)
    assert not mock_vector_model_inference.process.called 
    assert isinstance(response, VectorResponse)
    assert response.id == "test_1"
    assert response.results is None
    assert response.error.code == ErrorCode.REQUEST_SIZE_EXCEED

@pytest.mark.vector_service
def test_vector_serivce_process_multiple_requests(mock_vector_model_inference):  
    vector_service = VectorService(vector_model=mock_vector_model_inference)
    requests = [
        VectorRequest(
            id="test_1",
            texts= [
                "how much protein should a female eat",
                "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
            ] * 100
        ),
        VectorRequest(
            id="test_2",
            texts= [
                "how much protein should a female eat",
                "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
            ] * 50
        ),
        VectorRequest(
            id="test_3",
            texts= [
                "how much protein should a female eat",
                "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
            ] * 14
        ),
        VectorRequest(
            id="test_4",
            texts= [
                "how much protein should a female eat",
                "As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
            ] * 50
        )
    ]

    mock_vector_model_inference.process.side_effect = [[[0.1, 0.2, 0.3]] * 128, [[0.1, 0.2, 0.3]] * 100]
    responses = vector_service.process_messages(requests)
    # convert generator to list for testing
    responses = list(responses)
    assert mock_vector_model_inference.process.call_count == 2
    assert isinstance(responses, list)
    assert len(responses) == len(requests)

    assert responses[0].results is None
    assert responses[0].error.code == ErrorCode.REQUEST_SIZE_EXCEED
    assert len(responses[1].results) == len(requests[1].texts)
    assert len(responses[2].results) == len(requests[2].texts)
    assert len(responses[3].results) == len(requests[3].texts)