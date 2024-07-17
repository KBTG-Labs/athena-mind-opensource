
import pytest

from unittest.mock import patch, AsyncMock

from internal.infra.ml.gemini import Gemini
from internal.domain.entity import LLMRequest, LLMResponse
from tests.mocks.gemini import MockGeminiResponse
from tests.mocks.helper import mock_async_generator


def create_gemini_module(
        api_key="TEST_API_KEY",
        model_name="gemini-1.0-pro-001",
        model_max_output_token=2048,
        model_temperature=0.9,
        model_top_p=1,
        model_stream_required=False,
        model_batch_required=False,
        model_request_workers=1,
        model_transport="grpc"
) -> Gemini:
    return Gemini(
        api_key=api_key,
        model_name=model_name,
        model_max_output_token=model_max_output_token,
        model_temperature=model_temperature,
        model_top_p=model_top_p,
        model_stream_required=model_stream_required,
        model_batch_required=model_batch_required,
        model_request_workers=model_request_workers,
        model_transport=model_transport,
    )


@pytest.mark.gemini
def test_gemini_gen_ai_with_no_stream(mock_genai_model):
    model = create_gemini_module(model_stream_required=False)
    model.model = mock_genai_model
    message = LLMRequest(
        id="1",
        prompt="Hello, what is your name?",
        destination="dest1",
    )

    mock_genai_model.generate_content.return_value = MockGeminiResponse(
        text="my name is google genai")
    response = model.generate_response(message)

    assert response.id == "1"
    assert response.results == "my name is google genai"
    assert response.error == None


@pytest.mark.gemini
def test_gemini_gen_ai_with_stream(mock_genai_model):
    model = create_gemini_module(model_stream_required=True)
    model.model = mock_genai_model
    message = LLMRequest(
        id="1",
        prompt="Hello, what is your name?",
        destination="dest1",
    )

    mock_genai_model.generate_content.return_value = [
        MockGeminiResponse(text="good morning sir, "),
        MockGeminiResponse(text="my name is google genai"),
    ]
    response = model.generate_response(message)

    assert response.id == "1"
    assert response.results == "good morning sir, my name is google genai"
    assert response.error == None


@patch('nest_asyncio.apply')
@pytest.mark.gemini
def test_gemini_gen_ai_batch_required(mock_apply, mock_genai_model):
    model_request_workers = 5
    model = create_gemini_module(
        model_batch_required=True,
        model_request_workers=model_request_workers,
    )
    model.model = mock_genai_model

    mock_apply.assert_called_once()
    assert model.request_workers == model_request_workers


@patch('google.generativeai.GenerativeModel', side_effect=Exception("Model Initialization Error"))
@pytest.mark.gemini
def test_genai_model_initialization_exception(mock_gen_model):
    with pytest.raises(Exception) as excinfo:
        create_gemini_module()
    assert str(excinfo.value) == "Model Initialization Error"


@pytest.mark.asyncio
@pytest.mark.gemini
async def test_generate_batch_responses():
    mocked_requests = [
        LLMRequest(
            id="1",
            prompt="Hello, what is your name?",
            destination="dest1",
        ),
        LLMRequest(
            id="2",
            prompt="""
                    You are an Expert Customer Support working for Kasikorn Bank.
                    Your customer is asking a question: <question>What's FCD account?</question>
                    Your co-worker have read the question, search for the internal relavant documents and found these documents:
                    <documents>
                    FCD account is Foreign Currency Deposit Account (FCD Account) that is used to reserve fund for future payments in foreign currencies such as payment for goods, services or overseas tuition fees, etc.
                    Reference: www.google.com
                    </documents>
                    Your task is to answer customer's question based on the searched documents and also provide the references (URL).
                    Answer in English only, the translator will do the personalization for you afterwards.
                """,
            destination="dest2",
        ),
    ]
    mocked_responses = [
        LLMResponse(id="1", results="Hello, my name is Gemini!",
                    error=None, destination="dest1"),
        LLMResponse(id="2", results="FCD account is used to reserve fund for future payments in foreign currencies. More information: www.google.com",
                    error=None, destination="dest2"),
    ]

    gemini_instance = create_gemini_module(model_batch_required=True)
    gemini_instance._Gemini__generate_batch_responses_async = AsyncMock(
        return_value=mocked_responses)
    result = gemini_instance.generate_batch_responses(mocked_requests)

    assert result == mocked_responses


@pytest.mark.asyncio
@pytest.mark.gemini
async def test__generate_batch_responses_async(monkeypatch):
    mocked_requests = [
        LLMRequest(
            id="1",
            prompt="Hello, what is your name?",
            destination="dest1",
        ),
        LLMRequest(
            id="2",
            prompt="""
                    You are an Expert Customer Support working for Kasikorn Bank.
                    Your customer is asking a question: <question>What's FCD account?</question>
                    Your co-worker have read the question, search for the internal relavant documents and found these documents:
                    <documents>
                    FCD account is Foreign Currency Deposit Account (FCD Account) that is used to reserve fund for future payments in foreign currencies such as payment for goods, services or overseas tuition fees, etc.
                    Reference: www.google.com
                    </documents>
                    Your task is to answer customer's question based on the searched documents and also provide the references (URL).
                    Answer in English only, the translator will do the personalization for you afterwards.
                """,
            destination="dest2",
        ),
    ]
    mocked_responses = [
        LLMResponse(id="1", results="Hello, my name is Gemini!",
                    error=None, destination="dest1"),
        LLMResponse(id="2", results="FCD account is used to reserve fund for future payments in foreign currencies. More information: www.google.com",
                    error=None, destination="dest2"),
    ]

    async def mock_process_async_call(requests):
        for response in mocked_responses:
            yield response

    gemini_instance = create_gemini_module(model_batch_required=True)
    monkeypatch.setattr(
        gemini_instance,
        '_Gemini__process_async_call',
        mock_process_async_call,
    )
    result = await gemini_instance._Gemini__generate_batch_responses_async(mocked_requests)

    assert result == mocked_responses


@pytest.mark.asyncio
@pytest.mark.gemini
async def test__process_async_call(monkeypatch):
    mocked_requests = [
        LLMRequest(
            id="1",
            prompt="Hello, what is your name?",
            destination="dest1",
        ),
        LLMRequest(
            id="2",
            prompt="""
                    You are an Expert Customer Support working for Kasikorn Bank.
                    Your customer is asking a question: <question>What's FCD account?</question>
                    Your co-worker have read the question, search for the internal relavant documents and found these documents:
                    <documents>
                    FCD account is Foreign Currency Deposit Account (FCD Account) that is used to reserve fund for future payments in foreign currencies such as payment for goods, services or overseas tuition fees, etc.
                    Reference: www.google.com
                    </documents>
                    Your task is to answer customer's question based on the searched documents and also provide the references (URL).
                    Answer in English only, the translator will do the personalization for you afterwards.
                """,
            destination="dest2",
        ),
    ]
    mocked_responses = [
        LLMResponse(id="1", results="Hello, my name is Gemini!",
                    error=None, destination="dest1"),
        LLMResponse(id="2", results="FCD account is used to reserve fund for future payments in foreign currencies. More information: www.google.com",
                    error=None, destination="dest2"),
    ]

    async def mock_process_async_call(requests):
        for response in mocked_responses:
            yield response

    gemini_instance = create_gemini_module(model_batch_required=True)
    monkeypatch.setattr(
        gemini_instance,
        '_Gemini__process_async_call',
        mock_process_async_call,
    )
    result = await gemini_instance._Gemini__generate_batch_responses_async(mocked_requests)

    assert result == mocked_responses


@pytest.mark.asyncio
@pytest.mark.gemini
async def test__process_async_call(mock_genai_model):
    model = create_gemini_module(model_batch_required=True)
    model.model = mock_genai_model
    messages = [
        LLMRequest(
            id="1",
            prompt="Hello, what is your name?",
            destination="dest1",
        ),
    ]

    mock_genai_model.generate_content_async.return_value =\
        MockGeminiResponse(text="good morning sir, my name is google genai")

    response_generator = model._Gemini__process_async_call(messages)
    responses = [response async for response in response_generator]

    assert len(responses) == 1
    assert responses[0].results == "good morning sir, my name is google genai"
    assert responses[0].id == "1"
    assert responses[0].destination == "dest1"
    assert responses[0].error == None


@pytest.mark.asyncio
@pytest.mark.gemini
async def test__call_model_async_with_no_stream(mock_genai_model):
    model = create_gemini_module(
        model_batch_required=True,
        model_stream_required=False,
    )
    model.model = mock_genai_model
    prompt = "hello what's your name?"

    mock_genai_model.generate_content_async.return_value = \
        MockGeminiResponse(text="good morning sir, my name is google genai")
    response = await model._Gemini__call_model_async(prompt)

    assert response.results == "good morning sir, my name is google genai"
    assert response.error == None
    mock_genai_model.generate_content_async.assert_called_once_with(
        contents=prompt,
        stream=False
    )


@pytest.mark.asyncio
@pytest.mark.gemini
async def test__call_model_async_with_stream(mock_genai_model):
    model = create_gemini_module(
        model_batch_required=True,
        model_stream_required=True,
    )
    model.model = mock_genai_model
    prompt = "hello what's your name?"

    mock_genai_model.generate_content_async.return_value = mock_async_generator([
        MockGeminiResponse(text="good morning sir, "),
        MockGeminiResponse(text="my name is google genai"),
    ])
    response = await model._Gemini__call_model_async(prompt)

    assert response.results == "good morning sir, my name is google genai"
    assert response.error == None
    mock_genai_model.generate_content_async.assert_called_once_with(
        contents=prompt,
        stream=True
    )
