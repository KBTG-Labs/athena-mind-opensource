from typing import List, Optional

from common.constant.domain import DOMAIN_LLM as DOMAIN
from common.decorator import trace
from common.log import Logger
from internal.domain.entity import LLMRequest, LLMResponse
from internal.domain.ml import ILLMModel

from .llm_service_interface import ILLMService


class LLMService(ILLMService):
    def __init__(self, llm_model: ILLMModel, llm_batch_required: Optional[bool] = False):
        self.logger = Logger.get_logger(DOMAIN)
        self.llm_model = llm_model
        self.llm_batch_required = llm_batch_required

    @trace
    def process_messages(self, payloads: List[LLMRequest]) -> List[LLMResponse]:
        self.logger.info(f"process_messages (payload:{payloads})")
        responses = []

        if self.llm_batch_required:
            responses = self.llm_model.generate_batch_responses(payloads)
        else:
            for payload in payloads:
                response = self.llm_model.generate_response(payload)
                responses.append(response)

        return responses
