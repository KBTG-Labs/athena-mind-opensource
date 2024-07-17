import asyncio
import time
from typing import List

from langchain_core.embeddings import Embeddings
from mq_client import MQClient

from common.constant.domain import DOMAIN_VECTOR as DOMAIN
from common.decorator import trace
from common.log import Logger


class MQEmbeddings(Embeddings):
    def __init__(
        self, 
        mq: MQClient,
        topic: str = "vector-request",
        consume_topic: str = "vector-response",
        service: str = "mq_embeddings"
    ):
        self.topic = topic
        self.consume_topic = consume_topic
        self.mq = mq
        self.logger = Logger.get_logger(DOMAIN)
        self.service = service
        
        self.logger.info({
            "message": "init mq_embeddings service",
            "service": self.service,
            "topic": self.topic,
            "consume_topic": self.consume_topic,
        })

    @trace
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        self.logger.info({
            "message": "[sync] embed_documents called", 
            "service": self.service,
        })
        payload = {
            "texts": texts
        }

        start_time = time.perf_counter()
        result = asyncio.run_coroutine_threadsafe(self.mq.send_request(self.topic, payload, self.consume_topic), self.mq.event_loop).result()
        result = result["results"]
        
        self.logger.info({
            "message": "[sync] embed_documents got result",
            "service": self.service,
            "length": len(result),
            "process_time": f"{time.perf_counter() - start_time:.2f}s",
        })
        return result

    @trace
    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]
    
    @trace
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        self.logger.info({
            "message": "[async] aembed_documents called", 
            "service": self.service,
        })
        payload = {
            "texts": texts
        }

        start_time = time.perf_counter()
        result = await self.mq.send_request(self.topic, payload, self.consume_topic)
        result = result["results"]

        self.logger.info({
            "message": "[async] aembed_documents got result",
            "service": self.service,
            "length": len(result),
            "process_time": f"{time.perf_counter() - start_time:.2f}s",
        })
        return result

    @trace
    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous Embed query text."""
        results = await self.aembed_documents([text])
        return results[0]