from typing import List

from common.constant.domain import APP_VECTOR as DOMAIN
from common.data_mapper import IDataMapper
from common.decorator import trace
from common.dto import ConsumedMessageDTO, PublishedMessageDTO
from common.log import Logger
from internal.app.external_service import IProducerService
from internal.domain.entity import VectorRequest, VectorResponse
from internal.domain.service import IVectorService

from .vector_app_service_interface import IVectorApplicationService


class VectorApplicationService(IVectorApplicationService):
    def __init__(
        self,
        vector_service: IVectorService,
        producer_service: IProducerService,
        error_producer_service: IProducerService,
        mq_request_data_mapper: IDataMapper[VectorRequest, ConsumedMessageDTO],
        mq_response_data_mapper: IDataMapper[VectorResponse,
                                             PublishedMessageDTO],
        service_name: str = "vector_app_service",
    ):
        self.logger = Logger.get_logger(DOMAIN)
        self.vector_service = vector_service
        self.producer_service = producer_service
        self.error_producer_service = error_producer_service
        self.mq_request_data_mapper = mq_request_data_mapper
        self.mq_response_data_mapper = mq_response_data_mapper

        self.service_name = service_name

    @trace
    def handle_queue(self, payloads: List[ConsumedMessageDTO]):
        self.logger.info(f"handle_queue (payload:{payloads})")

        vector_requests = list(
            map(self.mq_request_data_mapper.to_domain_entity, payloads))
        results = self.vector_service.process_messages(vector_requests)
        for result in results:
            mq_message = self.mq_response_data_mapper.to_dal_entity(result)
            mq_message.source = self.service_name

            if result.error is not None:
                self.error_producer_service.publish_message(mq_message)
            self.producer_service.publish_message(mq_message)
