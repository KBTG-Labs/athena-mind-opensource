from dataclasses import dataclass

from client.config import Configs
from common.data_mapper import IDataMapper
from common.dto import ConsumedMessageDTO, PublishedMessageDTO
from common.log import Logger
from internal.app.data_mapper import MQRequestDataMapper, MQResponseDataMapper
from internal.app.external_service import IConsumerService, IProducerService
from internal.app.service import IVectorApplicationService, VectorApplicationService
from internal.domain.entity import VectorRequest, VectorResponse
from internal.domain.ml import IVectorModel
from internal.domain.service import IVectorService, VectorService
from internal.infra.external_service import ConsumerService, ProducerService
from internal.infra.ml import VectorModel


@dataclass
class DependencyService:
    producer_service: IProducerService
    consumer_service: IConsumerService
    vector_service: IVectorService
    vector_app_service: IVectorApplicationService


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
    vector_app_service: IVectorApplicationService
) -> IConsumerService:
    return ConsumerService(
        vector_app_service=vector_app_service,
        mq_group_id=configs.mq_consumer_group_id,
        mq_bootstrap_server=configs.mq_bootstrap_server,
        mq_offset_reset=configs.mq_consumer_offset_reset,
        mq_max_batch_size=configs.mq_consumer_max_batch_size,
        mq_consume_timeout=configs.mq_consumer_consume_timeout,
        mq_log_level=configs.log_level_mq,
    )


def init_mq_request_data_mapper() -> IDataMapper[VectorRequest, ConsumedMessageDTO]:
    return MQRequestDataMapper()


def init_mq_response_data_mapper() -> IDataMapper[VectorResponse, PublishedMessageDTO]:
    return MQResponseDataMapper()


def init_vector_app_service(
    vector_service: IVectorService,
    producer_service: IProducerService,
    error_producer_service: IProducerService,
    mq_request_data_mapper: IDataMapper[VectorRequest, ConsumedMessageDTO],
    mq_response_data_mapper: IDataMapper[VectorResponse, PublishedMessageDTO],
) -> IVectorApplicationService:

    return VectorApplicationService(
        vector_service=vector_service,
        producer_service=producer_service,
        error_producer_service=error_producer_service,
        mq_request_data_mapper=mq_request_data_mapper,
        mq_response_data_mapper=mq_response_data_mapper,
    )


def init_vector_service(
    vector_model: IVectorModel,
) -> IVectorService:
    return VectorService(
        vector_model=vector_model,
    )


def init_vector_model(model_path: str, batch_size: int, max_characters: int) -> IVectorModel:
    return VectorModel(
        model_path=model_path,
        model_batch_size=batch_size,
        model_max_characters=max_characters,
    )


def init_services(configs: Configs) -> DependencyService:
    Logger.change_log_level(configs.log_level)
    Logger.change_log_timezone(configs.log_timezone)

    mq_request_data_mapper = init_mq_request_data_mapper()
    mq_response_data_mapper = init_mq_response_data_mapper()

    producer_service = init_producer_service(
        configs=configs,
    )
    error_producer_service = init_error_producer_service(
        configs=configs,
    )
    vector_model = init_vector_model(
        model_path=configs.vector_model_path,
        batch_size=configs.vector_batch_size,
        max_characters=configs.vector_max_characters,
    )
    vector_service = init_vector_service(
        vector_model=vector_model,
    )
    vector_app_service = init_vector_app_service(
        vector_service=vector_service,
        producer_service=producer_service,
        error_producer_service=error_producer_service,
        mq_request_data_mapper=mq_request_data_mapper,
        mq_response_data_mapper=mq_response_data_mapper,
    )
    consumer_service = init_consumer_service(
        configs=configs,
        vector_app_service=vector_app_service,
    )

    return DependencyService(
        producer_service=producer_service,
        consumer_service=consumer_service,
        vector_service=vector_service,
        vector_app_service=vector_app_service,
    )
