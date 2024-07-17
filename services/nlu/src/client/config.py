from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from common.log import LogLevel, LogTimezone


class Configs(BaseSettings):
    model_config = SettingsConfigDict()

    service_name: Optional[str] = "athenamind-nlu"
    
    chainlit_host: Optional[str] = "0.0.0.0"
    chainlit_port: Optional[int] = 8901

    log_level: Optional[LogLevel] = "INFO"
    log_timezone: Optional[LogTimezone] = 7

    enable_telemetry: Optional[bool] = False
    telemetry_collector_endpoint: Optional[str] = ""

    mq_client_host: str
    mq_client_consumer_group_id: Optional[str] = "nlu-group-service"
    mq_client_llm_topic: Optional[str] = "llm-request"
    mq_client_llm_consume_topic: Optional[str] = "llm-response"
    mq_client_consume_timeout: Optional[float] = 0.1
    
    adapter_config_path: str
    default_adapter_name: str