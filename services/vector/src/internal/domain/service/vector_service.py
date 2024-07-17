from typing import Iterator, List

from common.constant.domain import DOMAIN_VECTOR as DOMAIN
from common.decorator import trace
from common.exception.error import Error, ErrorCode
from common.log import Logger
from internal.domain.entity import VectorRequest, VectorResponse
from internal.domain.ml import IVectorModel

from .vector_service_interface import IVectorService


class VectorService(IVectorService):
    def __init__(self, vector_model: IVectorModel):
        self.logger = Logger.get_logger(DOMAIN)
        self.vector_model = vector_model
        self._max_batch_size = 128

    @trace
    def process_message(self, payload: VectorRequest) -> VectorResponse:
        self.logger.info(f"process_message (payload:{payload})")

        response = VectorResponse(
            id=payload.id,
            results=None,
            destination=payload.destination,
        )
        if len(payload.texts) > self._max_batch_size:
            response.error = Error(
                code=ErrorCode.REQUEST_SIZE_EXCEED,
                detail=f"message.texts length must < {self._max_batch_size}"
            )
            return response
        response.results = self.vector_model.process(payload.to_request())
        return response

    @trace
    def process_messages(self, payloads: List[VectorRequest]) -> Iterator[VectorResponse]:
        self.logger.info(f"process_messages (payload:{payloads})")

        batch, metadata = [], []
        batches = []

        for payload in payloads:
            batch_size = len(batch)
            payload_size = len(payload.texts)
            if payload_size > self._max_batch_size:
                yield VectorResponse(
                    id=payload.id,
                    results=None,
                    error=Error(
                        code=ErrorCode.REQUEST_SIZE_EXCEED,
                        detail=f"message.texts length must < {self._max_batch_size}"
                    )
                )
                continue
            if batch_size > 0 and batch_size + payload_size > self._max_batch_size:
                batches.append((batch, metadata))
                batch, metadata = [], []

            batch.extend(payload.to_request())
            metadata.append((payload.id, payload_size, payload.destination))

        if len(batch) > 0:
            batches.append((batch, metadata))

        for batch, metadata in batches:
            results = self.vector_model.process(batch)

            i = 0
            for payload_id, size, destination in metadata:
                result = results[i:i+size]
                yield VectorResponse(
                    id=payload_id,
                    results=result,
                    destination=destination,
                )
                i += size
