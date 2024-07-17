import pytest
from pydantic import ValidationError

from client.config import Configs


@pytest.fixture(autouse=True)
def clear_system_env(monkeypatch):
    envs = [
        "MQ_CLIENT_HOST",
        "MQ_CLIENT_CONSUMER_GROUP_ID",
        "MQ_CLIENT_LLM_TOPIC",
        "MQ_CLIENT_LLM_CONSUME_TOPIC",
        "ADAPTER_CONFIG_PATH",
        "DEFAULT_ADAPTER_NAME",
    ]
    for env in envs:
        monkeypatch.delenv(env, raising=False)


@pytest.mark.configs
def test_configs_defaults():
    config = Configs(
        mq_client_host="localhost:9092",
        adapter_config_path="/path/to/config",
        default_adapter_name="General Handler",
    )

    assert config.mq_client_host == "localhost:9092"
    assert config.mq_client_consumer_group_id == "nlu-group-service"
    assert config.mq_client_llm_topic == "llm-request"
    assert config.mq_client_llm_consume_topic == "llm-response"
    assert config.adapter_config_path == "/path/to/config"
    assert config.default_adapter_name == "General Handler"


@pytest.mark.configs
def test_overwrite_configs_with_env(monkeypatch):
    monkeypatch.setenv("MQ_CLIENT_HOST", "localhost:9092")
    monkeypatch.setenv("ADAPTER_CONFIG_PATH", "/path/to/config")
    monkeypatch.setenv("DEFAULT_ADAPTER_NAME", "General Handler")

    config = Configs()

    assert config.mq_client_host == "localhost:9092"
    assert config.adapter_config_path == "/path/to/config"
    assert config.default_adapter_name == "General Handler"


@pytest.mark.configs
def test_overwrite_configs_with_fields():
    config = Configs(
        mq_client_host="localhost:9092",
        mq_client_llm_topic="llm-request-2",
        adapter_config_path="/path/to/config",
        default_adapter_name="General Handler",
    )

    assert config.mq_client_host == "localhost:9092"
    assert config.mq_client_llm_topic == "llm-request-2"
    assert config.adapter_config_path == "/path/to/config"
    assert config.default_adapter_name == "General Handler"

@pytest.mark.configs
def test_overwrite_configs_from_env_with_field(monkeypatch):
    monkeypatch.setenv("MQ_CLIENT_HOST", "localhost:9092")
    monkeypatch.setenv("ADAPTER_CONFIG_PATH", "/path/to/config")
    monkeypatch.setenv("DEFAULT_ADAPTER_NAME", "General Handler")

    config = Configs(
        mq_client_host="localhost:9999",
        adapter_config_path="/path/to/other_config",
        default_adapter_name="Account Expert",
    )

    assert config.mq_client_host == "localhost:9999"
    assert config.adapter_config_path == "/path/to/other_config"
    assert config.default_adapter_name == "Account Expert"

@pytest.mark.configs
def test_configs_validation_error(monkeypatch):
    expected_error_validation_message = "1 validation error for Configs"
    expected_error_type_message = "Input should be a valid string"
    
    monkeypatch.setenv("ADAPTER_CONFIG_PATH", "/path/to/config")
    monkeypatch.setenv("DEFAULT_ADAPTER_NAME", "General Handler")

    with pytest.raises(ValidationError) as excinfo:
        Configs(mq_client_host=1)

    error_message = str(excinfo.value)
    assert expected_error_validation_message in error_message
    assert expected_error_type_message in error_message
