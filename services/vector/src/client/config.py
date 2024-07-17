from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from common.log import LogLevel, LogTimezone


class Configs(BaseSettings):
    model_config = SettingsConfigDict()

    service_name: Optional[str] = "athenamind-vector"
    
    # Logging Configuration
    log_level: Optional[LogLevel] = "INFO"
    log_level_mq: Optional[LogLevel] = "ERROR"
    log_timezone: Optional[LogTimezone] = 0

    enable_telemetry: Optional[bool] = False
    telemetry_collector_endpoint: Optional[str] = ""
    
    # Messaging Queue Kafka Configuration
    mq_bootstrap_server: str
    mq_consumer_group_id: Optional[str] = "vector-service-group"
    mq_consumer_min_commit_count: Optional[int] = 1
    mq_consumer_offset_reset: Optional[str] = "earliest"
    mq_consumer_max_batch_size: Optional[int] = 20
    mq_consumer_consume_timeout: Optional[float] = 1
    mq_consumer_topic: Optional[str] = "vector-request"
    mq_producer_topic: Optional[str] = "vector-response"
    mq_error_topic: Optional[str] = "error-queue"

    # Vector Model Configuration
    vector_model_path: str
    vector_batch_size: Optional[int] = 32
    vector_max_characters: Optional[int] = 500
