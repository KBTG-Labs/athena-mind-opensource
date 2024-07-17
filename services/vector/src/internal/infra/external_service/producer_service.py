import json
from typing import Optional

from confluent_kafka import Producer

from common.constant.domain import INFRA_PRODUCER as DOMAIN
from common.constant.domain import KAFKA_PRODUCER
from common.decorator import trace
from common.dto import PublishedMessageDTO
from common.log import Logger, LogLevel
from internal.app.external_service import IProducerService


class ProducerService(IProducerService):
    def __init__(
        self,
        mq_topic: str,
        mq_bootstrap_server: str,
        mq_log_level: LogLevel,
        mq_system_consumed_topic: Optional[str] = None,
    ):
        self.logger = Logger.get_logger(DOMAIN)
        self.kafka_logger = Logger.get_logger(KAFKA_PRODUCER, mq_log_level)

        self.mq_topic = mq_topic
        self.mq_system_consumed_topic = mq_system_consumed_topic
        self.producer = Producer(
            {'bootstrap.servers': mq_bootstrap_server},
            logger=self.kafka_logger,
        )

    def __delivery_report(self, err, msg):
        self.logger.info("Delivery Report")

        if err is not None:
            self.logger.error(f"Message Delivery Failed: {err}")
            return

        topic, partition = msg.topic(), msg.partition()
        message = f"Message Delivery to {topic} [Partition:{partition}]"
        self.logger.info(message)

    @trace
    def publish_message(self, payload: PublishedMessageDTO):
        self.logger.info(f"publish_message (payload: {payload})")

        if not payload.destination:
            message = f"No destination topic given. Using the default one ({self.mq_topic})."
            self.logger.info(message)
            payload.destination = self.mq_topic
        elif self.mq_system_consumed_topic and payload.destination == self.mq_system_consumed_topic:
            message = f"The destination topic cannot be the same as the system-consumed topic ({self.mq_system_consumed_topic}). " \
                f"Overwriting the given destination with the default destination ({self.mq_topic})."
            self.logger.warning(message)
            payload.destination = self.mq_topic

        self.producer.poll(0)
        send_data = json.dumps(
            payload.model_dump(),
            ensure_ascii=True, indent=4
        )
        self.producer.produce(
            payload.destination,
            send_data.encode('utf-8'),
            callback=self.__delivery_report,
        )
        self.producer.flush()
