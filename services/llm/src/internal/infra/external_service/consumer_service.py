import traceback
import pydantic_core

from typing import List, Any, Optional
from confluent_kafka import Consumer, KafkaError

from common.constant.domain import KAFKA_CONSUMER, INFRA_CONSUMER as DOMAIN
from common.log import Logger, LogLevel
from common.dto import ConsumedMessageDTO
from internal.app.external_service import IConsumerService
from internal.app.service import ILLMApplicationService

from common.decorator import trace

class ConsumerService(IConsumerService):
    def __init__(
        self,
        llm_app_service: ILLMApplicationService,
        mq_group_id: str,
        mq_bootstrap_server: str,
        mq_offset_reset: str,
        mq_consume_timeout: int,
        mq_max_batch_size: int,
        mq_log_level: LogLevel,
    ):
        self.logger = Logger.get_logger(DOMAIN)
        self.kafka_logger = Logger.get_logger(KAFKA_CONSUMER, mq_log_level)

        self.llm_app_service = llm_app_service
        self.mq_max_batch_size = mq_max_batch_size
        self.mq_consume_timeout = mq_consume_timeout
        self.consumer = Consumer(
            {
                'group.id': mq_group_id,
                'bootstrap.servers': mq_bootstrap_server,
                'auto.offset.reset': mq_offset_reset,
            },
            logger=self.kafka_logger,
        )

    def subscribe(self, topics: List[str]):
        self.consumer.subscribe(topics)

    def close(self):
        self.consumer.close()

    def commit(self, asynchronous=True):
        self.consumer.commit(asynchronous=asynchronous)

    def consume(self) -> List[Any] | None:
        return self.consumer.consume(
            self.mq_max_batch_size,
            self.mq_consume_timeout,
        )

    @Logger.register_correlation_id_mq
    @trace
    def process(self, messages: List[Any]) -> bool:
        try:
            payloads: List[ConsumedMessageDTO] = []
            for message in messages:
                if message.error():
                    if message.error().code() == KafkaError._PARTITION_EOF:
                        message.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                             (message.topic(), message.partition(), message.offset()))
                    elif message.error():
                        error = message.error()
                        self.logger.error(f"Consumer Error: {error}")
                    return False

                decoded = message.value().decode('utf-8')
                consumed = ConsumedMessageDTO.model_validate_json(decoded)
                payloads.append(consumed)

            self.llm_app_service.handle_queue(payloads)

        except pydantic_core.ValidationError as e:
            self.logger.error(f"Error Decoding JSON: {e}")
            return False

        except Exception as e:
            trace = traceback.format_exc()
            self.logger.error(f"Failed to Handle Message: {e}, {trace}")
            return False

        return True
