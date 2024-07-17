import json
import logging
from confluent_kafka import Producer

from mq.common import IMQProducer, QueueDTO


class KafkaProducer(IMQProducer):
    def __init__(self, bootstrap_server: str, logger=logging.Logger):
        self.producer = Producer(
            {'bootstrap.servers': bootstrap_server},
            logger=logger,
        )

    def publish_message(self, topic: str, payload: QueueDTO):
        self.producer.poll(0)
        send_data = json.dumps(payload.to_dict(), ensure_ascii=True, indent=4)

        self.producer.produce(topic, send_data.encode('utf-8'))
        self.producer.flush()
