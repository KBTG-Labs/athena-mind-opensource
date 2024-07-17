from dataclasses import dataclass

from common.data_mapper import IDataMapper
from common.dto import ConsumedMessageDTO, PublishedMessageDTO
from common.log import Logger
from internal.app.data_mapper import MQRequestDataMapper, MQResponseDataMapper
from internal.app.external_service import IConsumerService, IProducerService
from internal.app.service import ILLMApplicationService, LLMApplicationService
from internal.domain.entity import LLMRequest, LLMResponse
from internal.domain.ml import ILLMModel
from internal.domain.service import ILLMService, LLMService
from internal.infra.external_service import ConsumerService, ProducerService
from internal.infra.ml import Gemini, HuggingFace

from client.config import Configs


@dataclass
class DependencyService:
    producer_service: IProducerService
    consumer_service: IConsumerService
    llm_service: ILLMService
    llm_app_service: ILLMApplicationService


def init_producer_service(
    configs: Configs
) -> IProducerService:
    return ProducerService(
        mq_topic=configs.mq_producer_topic,
        mq_bootstrap_server=configs.mq_bootstrap_server,
        mq_log_level=configs.log_level_mq,
        mq_system_consumed_topic=configs.mq_consumer_topic,
    )


def init_error_producer_service(
    configs: Configs
) -> IProducerService:
    return ProducerService(
        mq_topic=configs.mq_error_topic,
        mq_bootstrap_server=configs.mq_bootstrap_server,
        mq_log_level=configs.log_level_mq,
        mq_system_consumed_topic=configs.mq_consumer_topic,
    )


def init_consumer_service(
    configs: Configs,
    llm_app_service: ILLMApplicationService
) -> IConsumerService:
    return ConsumerService(
        llm_app_service=llm_app_service,
        mq_group_id=configs.mq_consumer_group_id,
        mq_bootstrap_server=configs.mq_bootstrap_server,
        mq_offset_reset=configs.mq_consumer_offset_reset,
        mq_max_batch_size=configs.mq_consumer_max_batch_size,
        mq_consume_timeout=configs.mq_consumer_consume_timeout,
        mq_log_level=configs.log_level_mq,
    )


def init_mq_request_data_mapper() -> IDataMapper[LLMRequest, ConsumedMessageDTO]:
    return MQRequestDataMapper()


def init_mq_response_data_mapper() -> IDataMapper[LLMResponse, PublishedMessageDTO]:
    return MQResponseDataMapper()


def init_llm_app_service(
    llm_service: ILLMService,
    producer_service: IProducerService,
    error_producer_service: IProducerService,
    mq_request_data_mapper: IDataMapper[LLMRequest, ConsumedMessageDTO],
    mq_response_data_mapper: IDataMapper[LLMResponse, PublishedMessageDTO],
    service_name: str,
) -> ILLMApplicationService:
    return LLMApplicationService(
        llm_service=llm_service,
        producer_service=producer_service,
        error_producer_service=error_producer_service,
        mq_request_data_mapper=mq_request_data_mapper,
        mq_response_data_mapper=mq_response_data_mapper,
        service_name=service_name,
    )


def init_llm_service(
    llm_model: ILLMModel,
    llm_batch_required: bool,
) -> ILLMService:
    return LLMService(
        llm_model=llm_model,
        llm_batch_required=llm_batch_required,
    )


def init_llm_model(
    configs: Configs
) -> ILLMModel:
    match configs.llm_module:
        case "huggingface":
            return HuggingFace(
                huggingface_api_key=configs.huggingface_api_key,
                model_path=configs.huggingface_model_path,
                model_do_sample=configs.huggingface_model_do_sample,
                model_max_new_tokens=configs.huggingface_model_max_new_tokens,
                model_torch_dtype=configs.huggingface_model_torch_dtype,
                model_torch_device=configs.huggingface_model_torch_device,
                model_batch_required=configs.llm_batch_required,
            )
        case "gemini":
            return Gemini(
                api_key=configs.gemini_api_key,
                model_name=configs.gemini_model_name,
                model_max_output_token=configs.gemini_max_output_token,
                model_temperature=configs.gemini_temperature,
                model_top_p=configs.gemini_top_p,
                model_stream_required=configs.gemini_stream_required,
                model_request_workers=configs.gemini_request_workers,
                model_batch_required=configs.llm_batch_required,
                model_transport=configs.gemini_transport,
            )
        case _:
            raise ValueError("LLM Module Must Be: huggingface or gemini")


def init_services(configs: Configs) -> DependencyService:
    Logger.change_log_level(configs.log_level)
    Logger.change_log_timezone(configs.log_timezone)

    mq_request_data_mapper = init_mq_request_data_mapper()
    mq_response_data_mapper = init_mq_response_data_mapper()

    producer_service = init_producer_service(configs=configs)
    error_producer_service = init_error_producer_service(configs=configs)

    llm_model = init_llm_model(configs=configs)
    llm_service = init_llm_service(
        llm_model=llm_model,
        llm_batch_required=configs.llm_batch_required,
    )
    llm_app_service = init_llm_app_service(
        llm_service=llm_service,
        producer_service=producer_service,
        error_producer_service=error_producer_service,
        mq_request_data_mapper=mq_request_data_mapper,
        mq_response_data_mapper=mq_response_data_mapper,
        service_name=configs.service_name,
    )
    consumer_service = init_consumer_service(
        configs=configs,
        llm_app_service=llm_app_service,
    )

    return DependencyService(
        producer_service=producer_service,
        consumer_service=consumer_service,
        llm_service=llm_service,
        llm_app_service=llm_app_service,
    )
