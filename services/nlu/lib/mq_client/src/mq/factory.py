import logging
from typing import Tuple, Optional
from mq.common import IMQConsumer, IMQProducer, MQConfig, MQProvider
from mq.kafka import KafkaConsumer, KafkaProducer
from util.id import generate_group_id


def create_mq(mq_provider: MQProvider, mq_config: MQConfig, sdk_group="", require_unique_id=True, logger=logging.Logger) -> Tuple[IMQConsumer, IMQProducer]:
    match mq_provider.lower():
        case MQProvider.KAFKA.value:
            host = mq_config.host
            group_id = generate_group_id(
                suffix=sdk_group, require_unique_id=require_unique_id)
            consumer = KafkaConsumer(group_id=group_id, bootstrap_server=host, consume_timeout=mq_config.consume_timeout, logger=logger)
            producer = KafkaProducer(bootstrap_server=host, logger=logger)
            return consumer, producer
        case _:
            raise ValueError(f"Unsupported MQ provider: {mq_provider}")
