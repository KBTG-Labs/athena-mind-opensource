import pytest
from langchain_core.runnables import Runnable
from mq_client import MQClient

from language_models.mq_llm import MQLanguageModel


@pytest.fixture
def mock_mq_client(mocker):
    return mocker.Mock(spec=MQClient)

@pytest.fixture
def mock_mq_llm(mocker):
    return mocker.Mock(spec=MQLanguageModel)

@pytest.fixture
def mock_agent(mocker):
    return mocker.Mock(spec=Runnable)