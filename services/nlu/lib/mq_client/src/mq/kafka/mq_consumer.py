import json
import logging
import traceback

from typing import Callable, List
from confluent_kafka import Consumer, KafkaError

from mq.common import IMQConsumer, QueueDTO

class KafkaConsumer(IMQConsumer):
    def __init__(self, group_id: str, bootstrap_server: str, max_batch_size=10, consume_timeout=1, logger=logging.Logger):
        self.callback: Callable[[QueueDTO], bool] = None
        self.max_batch_size = max_batch_size
        self.consume_timeout = consume_timeout
        self.consumer = Consumer(
            {
                "group.id": group_id,
                "bootstrap.servers": bootstrap_server,
                "auto.offset.reset": "earliest",
            },
            logger=logger,
        )

    def subscribe(self, topics: List[str]):
        self.consumer.subscribe(topics)

    def commit(self, asynchronous=True):
        self.consumer.commit(asynchronous=asynchronous)

    def close(self):
        self.consumer.close()

    def register_callback(self, callback: Callable[[QueueDTO], bool]):
        self.callback = callback

    def consume(self):
        messages = self.consumer.consume(
            self.max_batch_size,
            self.consume_timeout,
        )

        if messages is None or not messages:
            return

        try:
            for message in messages:
                if message.error():
                    error_code = message.error().code()
                    if error_code == KafkaError._PARTITION_EOF:
                        error_message = f"{message.topic()} [{message.partition()}] reached end at offset {message.offset()}"
                        message.stderr.write(error_message)

                    print(f"Consumer Error: {message.error()}")
                    continue

                decode_message = message.value().decode("utf-8")
                queue_dto = QueueDTO.model_validate_json(decode_message)

                if self.callback:
                    self.callback(queue_dto)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

        except Exception as e:
            print(f"Failed to handle message: {e}, {traceback.format_exc()}")
            return
