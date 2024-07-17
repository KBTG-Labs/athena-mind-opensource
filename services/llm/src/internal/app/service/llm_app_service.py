from typing import List

from common.constant.domain import APP_LLM as DOMAIN
from common.log import Logger
from common.data_mapper import IDataMapper
from common.dto import ConsumedMessageDTO, PublishedMessageDTO, LLMRequestDTO, LLMResponseDTO
from internal.app.external_service import IProducerService
from internal.domain.entity import LLMRequest, LLMResponse
from internal.domain.service import ILLMService

from .llm_app_service_interface import ILLMApplicationService
#tracewrapper
from common.decorator import trace

class LLMApplicationService(ILLMApplicationService):
    def __init__(
        self,
        llm_service: ILLMService,
        producer_service: IProducerService,
        error_producer_service: IProducerService,
        mq_request_data_mapper: IDataMapper[LLMRequest, ConsumedMessageDTO[LLMRequestDTO]],
        mq_response_data_mapper: IDataMapper[LLMResponse, PublishedMessageDTO[LLMResponseDTO]],
        service_name: str = "llm_app_service",
    ):
        self.logger = Logger.get_logger(DOMAIN)
        self.llm_service = llm_service
        self.producer_service = producer_service
        self.error_producer_service = error_producer_service
        self.mq_request_data_mapper = mq_request_data_mapper
        self.mq_response_data_mapper = mq_response_data_mapper

        self.service_name = service_name

    @trace
    def handle_queue(self, payload: List[ConsumedMessageDTO[LLMRequest]]):
        self.logger.info(f"handle_queue (payload:{payload})")

        llm_requests = list(
            map(self.mq_request_data_mapper.to_domain_entity, payload))
        results = self.llm_service.process_messages(llm_requests)

        for result in results:
            mq_message = self.mq_response_data_mapper.to_dal_entity(result)
            mq_message.source = self.service_name

            if result.error is not None:
                error_mq_message = PublishedMessageDTO[LLMResponseDTO](
                    id=mq_message.id,
                    source=mq_message.source,
                    message=mq_message.message,
                    error=mq_message.error,
                )
                self.error_producer_service.publish_message(
                    payload=error_mq_message)

            self.producer_service.publish_message(payload=mq_message)
