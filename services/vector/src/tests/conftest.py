import pytest
from confluent_kafka import Consumer, Message, Producer
from sentence_transformers import SentenceTransformer

from internal.app.service import VectorApplicationService
from internal.domain.service import VectorService
from internal.infra.external_service import ConsumerService, ProducerService
from internal.infra.ml.vector_model import VectorModel


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
def mock_vector_model(mocker):
    return mocker.Mock(spec=SentenceTransformer)

@pytest.fixture
def mock_vector_model_inference(mocker):
    return mocker.Mock(spec=VectorModel)

@pytest.fixture
def mock_vector_service(mocker):
    return mocker.Mock(spec=VectorService)

@pytest.fixture
def mock_vector_app_service(mocker):
    return mocker.Mock(spec=VectorApplicationService)