import google.generativeai as genai
import pytest
import huggingface_hub

from confluent_kafka import Consumer, Message, Producer
from transformers import AutoModelForCausalLM, AutoTokenizer

from internal.app.service import LLMApplicationService
from internal.domain.service import LLMService
from internal.infra.external_service import ConsumerService, ProducerService
from internal.infra.ml.gemini import Gemini
from internal.infra.ml.huggingface import login


@pytest.fixture
def mock_producer(mocker):
    return mocker.Mock(spec=Producer)


@pytest.fixture
def mock_producer_service(mocker):
    return mocker.Mock(spec=ProducerService)


@pytest.fixture
def mock_error_producer_service(mocker):
    return mocker.Mock(spec=ProducerService)


@pytest.fixture
def mock_consumer(mocker):
    return mocker.Mock(spec=Consumer)


@pytest.fixture
def mock_consumer_service(mocker):
    return mocker.Mock(spec=ConsumerService)


@pytest.fixture
def mock_kafka_message(mocker):
    return mocker.Mock(spec=Message)


@pytest.fixture
def mock_genai_model(mocker):
    return mocker.Mock(spec=genai.GenerativeModel)


@pytest.fixture
def mock_huggingface_model(mocker):
    return mocker.Mock(spec=AutoModelForCausalLM)


@pytest.fixture
def mock_tokenizer(mocker):
    return mocker.Mock(spec=AutoTokenizer)


@pytest.fixture
def mock_huggingface_hub(mocker):
    return mocker.Mock(spec=login)


@pytest.fixture
def mock_genai_model_inference(mocker):
    return mocker.Mock(spec=Gemini)


@pytest.fixture
def mock_llm_service(mocker):
    return mocker.Mock(spec=LLMService)


@pytest.fixture
def mock_llm_app_service(mocker):
    return mocker.Mock(spec=LLMApplicationService)
