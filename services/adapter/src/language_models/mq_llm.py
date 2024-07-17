import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from mq_client import MQClient

from common.constant.domain import DOMAIN_LLM as DOMAIN
from common.decorator import trace
from common.log import Logger

DEFAULT_FALLBACK_MESSAGE = """ขออภัย, ฉันไม่พบข้อมูลที่ต้องการ กรุณาลองให้ข้อมูลเพิ่มเติมหรือถามคำถามใหม่ ฉันยินดีที่จะช่วยเหลือคุณเสมอ"""
class MQLanguageModel(LLM):

    topic: str = "llm-request"
    consume_topic: str = "llm_response"
    mq: MQClient = None
    logger: logging.Logger = Logger.get_logger(DOMAIN)
    fallback_message: str = DEFAULT_FALLBACK_MESSAGE
    service: str = "mq_llm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info({
            "message": "init mq_llm service",
            "service": self.service,
            "topic": self.topic,
            "consume_topic": self.consume_topic,
        })

    @trace
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        self.logger.info({
            "message": "[sync] _call called",
            "service": self.service,
            "prompt": prompt
        })
        payload = {
            "text": prompt
        }
        start_time = time.perf_counter()
        result = asyncio.run_coroutine_threadsafe(self.mq.send_request(self.topic, payload, self.consume_topic), self.mq.event_loop).result()
        result = result["results"]
        self.logger.info({
            "message": "[sync] _call got result",
            "service": self.service,
            "result": result,
            "process_time": f"{time.perf_counter() - start_time:.2f}s",
        })
        
        if result is None:
            return self.fallback_message
        
        return result

    @trace
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        self.logger.info({
            "message": "[async] _acall called",
            "service": self.service,
            "prompt": prompt
        })
        payload = {
            "text": prompt
        }
        start_time = time.perf_counter()
        result = await self.mq.send_request(self.topic, payload, self.consume_topic)
        result = result["results"]
        self.logger.info({
            "message": "[async] _acall got result",
            "service": self.service,
            "result": result,
            "process_time": f"{time.perf_counter() - start_time:.2f}s",
        })

        if result is None:
            return self.fallback_message
        
        return result
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": "MQChatModel",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "mq_llm"