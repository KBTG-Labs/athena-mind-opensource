import pytest
from mq_client import MQClient

from embeddings.mq_embeddings import MQEmbeddings
from language_models.mq_llm import MQLanguageModel


@pytest.fixture
def mock_mq_client(mocker):
    return mocker.Mock(spec=MQClient)

@pytest.fixture
def mock_mq_embeddings(mocker):
    return mocker.Mock(spec=MQEmbeddings)

@pytest.fixture
def mock_mq_llm(mocker):
    return mocker.Mock(spec=MQLanguageModel)