import pytest
from pydantic import ValidationError

from client.config import Configs


@pytest.fixture(autouse=True)
def clear_system_env(monkeypatch):
    envs = [
        "MQ_BOOTSTRAP_SERVER",
        "MQ_CONSUMER_GROUP_ID",
        "MQ_CONSUMER_MIN_COMMIT_COUNT",
        "MQ_CONSUMER_OFFSET_RESET",
        "MQ_CONSUMER_MAX_BATCH_SIZE",
        "MQ_CONSUMER_CONSUME_TIMEOUT",
        "MQ_CONSUMER_TOPIC",
        "MQ_PRODUCER_TOPIC",
        "MQ_ERROR_TOPIC",
        "VECTOR_MODEL_PATH",
        "VECTOR_BATCH_SIZE",
        "VECTOR_MAX_CHARACTERS",
    ]
    for env in envs:
        monkeypatch.delenv(env, raising=False)


@pytest.mark.configs
def test_configs_defaults():
    config = Configs(
        vector_model_path="/path/to/model",
        mq_bootstrap_server="localhost:9092",
    )

    assert config.mq_bootstrap_server == "localhost:9092"
    assert config.mq_consumer_group_id == "vector-service-group"
    assert config.mq_consumer_min_commit_count == 1
    assert config.mq_consumer_offset_reset == "earliest"
    assert config.mq_consumer_max_batch_size == 20
    assert config.mq_consumer_consume_timeout == 1
    assert config.mq_consumer_topic == "vector-request"
    assert config.mq_producer_topic == "vector-response"
    assert config.mq_error_topic == "error-queue"
    assert config.vector_model_path == "/path/to/model"
    assert config.vector_batch_size == 32
    assert config.vector_max_characters == 500


@pytest.mark.configs
def test_overwrite_configs_with_env(monkeypatch):
    monkeypatch.setenv("MQ_BOOTSTRAP_SERVER", "new-kafka:9092")
    monkeypatch.setenv("MQ_CONSUMER_GROUP_ID", "test-group")
    monkeypatch.setenv("VECTOR_MODEL_PATH", "/new/path/to/model")

    config = Configs()

    assert config.mq_bootstrap_server == "new-kafka:9092"
    assert config.mq_consumer_group_id == "test-group"
    assert config.vector_model_path == "/new/path/to/model"


@pytest.mark.configs
def test_overwrite_configs_with_fields():
    config = Configs(
        mq_bootstrap_server="new-kafka:9092",
        mq_consumer_group_id="test-group",
        vector_model_path="/new/path/to/model",
    )

    assert config.mq_bootstrap_server == "new-kafka:9092"
    assert config.mq_consumer_group_id == "test-group"
    assert config.vector_model_path == "/new/path/to/model"


@pytest.mark.configs
def test_overwrite_configs_from_env_with_field(monkeypatch):
    monkeypatch.setenv("MQ_BOOTSTRAP_SERVER", "localhost:9092")
    monkeypatch.setenv("VECTOR_MODEL_PATH", "path-from-env")

    config = Configs(
        mq_bootstrap_server="new-kafka:9092",
        vector_model_path="new-path",
    )

    assert config.mq_bootstrap_server == "new-kafka:9092"
    assert config.vector_model_path == "new-path"


@pytest.mark.configs
def test_configs_validation_error(monkeypatch):
    expected_error_validation_message = "1 validation error for Configs"
    expected_error_type_message = "Input should be a valid string"
    monkeypatch.setenv("MQ_BOOTSTRAP_SERVER", "localhost:9092")

    with pytest.raises(ValidationError) as excinfo:
        Configs(vector_model_path=1)

    error_message = str(excinfo.value)
    assert expected_error_validation_message in error_message
    assert expected_error_type_message in error_message
