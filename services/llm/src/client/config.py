from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.log import LogLevel, LogTimezone


class Configs(BaseSettings):
    model_config = SettingsConfigDict()

    service_name: Optional[str] = "llm-app-service"

    # Logging Configuration
    log_level: Optional[LogLevel] = "INFO"
    log_level_mq: Optional[LogLevel] = "ERROR"
    log_timezone: Optional[LogTimezone] = 0

    # Messaging Queue Kafka Configuration
    mq_bootstrap_server: str
    mq_consumer_group_id: Optional[str] = "llm-service-group"
    mq_consumer_min_commit_count: Optional[int] = 1
    mq_consumer_offset_reset: Optional[str] = "earliest"
    mq_consumer_max_batch_size: Optional[int] = 20
    mq_consumer_consume_timeout: Optional[float] = 1
    mq_consumer_topic: Optional[str] = "llm-request"
    mq_producer_topic: Optional[str] = "llm-response"
    mq_error_topic: Optional[str] = "error-queue"

    llm_module: Literal["huggingface", "gemini"]
    llm_batch_required: Optional[bool] = False

    # HuggingFace Configuration
    huggingface_api_key: Optional[str] = None
    huggingface_model_path: Optional[str] = ""
    huggingface_model_do_sample: Optional[bool] = True
    huggingface_model_max_new_tokens: Optional[int] = 2048
    huggingface_model_torch_dtype: Optional[Literal["float16",
                                                    "float32", "float64"]] = "float16"
    huggingface_model_torch_device: Optional[int] = 0

    # Gemini Configuration
    gemini_api_key: Optional[str] = None
    gemini_model_name: Optional[str] = "gemini-pro"
    gemini_max_output_token: Optional[int] = 2048
    gemini_temperature: Optional[float] = 0.9
    gemini_top_p: Optional[float] = 1
    gemini_stream_required: Optional[bool] = True
    gemini_request_workers: Optional[int] = 4
    gemini_transport: Optional[str] = "grpc"

    #opentelemetry
    enable_telemetry: Optional[bool] = False
    telemetry_collector_endpoint: Optional[str] = ""

