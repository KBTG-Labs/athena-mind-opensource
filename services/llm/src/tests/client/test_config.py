import pytest
from pydantic import ValidationError

from client.config import Configs


@pytest.fixture(autouse=True)
def clear_system_env(monkeypatch):
    envs = [
        "SERVICE_NAME",
        "MQ_BOOTSTRAP_SERVER",
        "MQ_CONSUMER_GROUP_ID",
        "MQ_CONSUMER_MIN_COMMIT_COUNT",
        "MQ_CONSUMER_OFFSET_RESET",
        "MQ_CONSUMER_MAX_BATCH_SIZE",
        "MQ_CONSUMER_CONSUME_TIMEOUT",
        "MQ_CONSUMER_TOPIC",
        "MQ_PRODUCER_TOPIC",
        "MQ_ERROR_TOPIC",
        "LLM_MODULE",
        "LLM_BATCH_REQUIRED",
        "HUGGINGFACE_API_KEY",
        "HUGGINGFACE_MODEL_PATH",
        "HUGGINGFACE_MODEL_DO_SAMPLE",
        "HUGGINGFACE_MODEL_MAX_NEW_TOKENS",
        "HUGGINGFACE_MODEL_TORCH_DTYPE",
        "HUGGINGFACE_MODEL_TORCH_DEVICE",
        "GEMINI_API_KEY",
        "GEMINI_MODEL_NAME",
        "GEMINI_MAX_OUTPUT_TOKEN",
        "GEMINI_TEMPERATURE",
        "GEMINI_TOP_P",
        "GEMINI_STREAM_REQUIRED",
        "GEMINI_REQUEST_WORKERS",
        "GEMINI_TRANSPORT"
    ]
    for env in envs:
        monkeypatch.delenv(env, raising=False)


@pytest.mark.configs
def test_configs_defaults():
    config = Configs(mq_bootstrap_server="localhost:9092", llm_module="gemini")

    assert config.mq_bootstrap_server == "localhost:9092"
    assert config.mq_consumer_group_id == "llm-service-group"
    assert config.mq_consumer_min_commit_count == 1
    assert config.mq_consumer_offset_reset == "earliest"
    assert config.mq_consumer_max_batch_size == 20
    assert config.mq_consumer_consume_timeout == 1
    assert config.mq_consumer_topic == "llm-request"
    assert config.mq_producer_topic == "llm-response"
    assert config.mq_error_topic == "error-queue"
    assert config.huggingface_api_key == None
    assert config.gemini_api_key == None


@pytest.mark.configs
def test_overwrite_configs_with_env(monkeypatch):
    monkeypatch.setenv("MQ_BOOTSTRAP_SERVER", "new-kafka:9092")
    monkeypatch.setenv("MQ_CONSUMER_GROUP_ID", "test-group")
    monkeypatch.setenv("HUGGINGFACE_API_KEY", "huggingface-api-key-env")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-api-key-env")
    monkeypatch.setenv("LLM_MODULE", "gemini")

    config = Configs()

    assert config.mq_bootstrap_server == "new-kafka:9092"
    assert config.mq_consumer_group_id == "test-group"
    assert config.huggingface_api_key == "huggingface-api-key-env"
    assert config.gemini_api_key == "gemini-api-key-env"
    assert config.llm_module == "gemini"


@pytest.mark.configs
def test_overwrite_configs_with_fields():
    config = Configs(
        mq_bootstrap_server="new-kafka:9092",
        mq_consumer_group_id="test-group",
        huggingface_api_key="huggingface-api-key-field",
        gemini_api_key="gemini-api-key-field",
        llm_module="gemini"
    )

    assert config.mq_bootstrap_server == "new-kafka:9092"
    assert config.mq_consumer_group_id == "test-group"
    assert config.huggingface_api_key == "huggingface-api-key-field"
    assert config.gemini_api_key == "gemini-api-key-field"
    assert config.llm_module == "gemini"


@pytest.mark.configs
def test_overwrite_configs_from_env_with_field(monkeypatch):
    monkeypatch.setenv("MQ_BOOTSTRAP_SERVER", "localhost:9092")
    monkeypatch.setenv("LLM_MODULE", "huggingface")

    config = Configs(
        mq_bootstrap_server="new-kafka:9092",
        llm_module="gemini"
    )

    assert config.mq_bootstrap_server == "new-kafka:9092"
    assert config.llm_module == "gemini"


@pytest.mark.configs
def test_configs_validation_error(monkeypatch):
    expected_error_validation_message = "2 validation errors for Configs"
    expected_error_type_message_1 = "Input should be a valid string"
    expected_error_type_message_2 = "Input should be 'huggingface' or 'gemini'"
    monkeypatch.setenv("MQ_BOOTSTRAP_SERVER", "localhost:9092")

    with pytest.raises(ValidationError) as excinfo:
        Configs(huggingface_model_path=1, llm_module=1)

    error_message = str(excinfo.value)
    assert expected_error_validation_message in error_message
    assert expected_error_type_message_1 in error_message
    assert expected_error_type_message_2 in error_message
