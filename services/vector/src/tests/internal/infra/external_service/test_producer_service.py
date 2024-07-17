import pytest
import unittest

from common.dto import PublishedMessageDTO
from internal.infra.external_service import ProducerService

mq_bootstrap_server = "localhost:9092"
mq_topic = "test"
mq_log_level = 7
mq_system_consumed_topic = "mq-system-consumed-topic"


@pytest.mark.producer_service
def test_producer_service(mock_producer, mock_kafka_message):
    producer = ProducerService(
        mq_topic=mq_topic,
        mq_bootstrap_server=mq_bootstrap_server,
        mq_log_level=mq_log_level,
        mq_system_consumed_topic=mq_system_consumed_topic,
    )
    producer.producer = mock_producer

    id = "message-id"
    message = {"texts": ["message"]}
    destination = "destination-test"
    message_dto = PublishedMessageDTO(
        id=id,
        message=message,
        destination=destination,
    )

    producer.publish_message(message_dto)

    mock_producer.poll.assert_called_once()
    mock_producer.produce.assert_called_once()
    mock_producer.flush.assert_called_once()

    mock_kafka_message.topic.return_value = "test-topic"
    mock_kafka_message.partition.return_value = 0
    producer._ProducerService__delivery_report(None, mock_kafka_message)
    producer._ProducerService__delivery_report(
        Exception('test call delivery report'), mock_kafka_message)


@pytest.mark.producer_service
def test_producer_service_with_destination(mock_producer):
    producer = ProducerService(
        mq_topic=mq_topic,
        mq_bootstrap_server=mq_bootstrap_server,
        mq_log_level=mq_log_level,
        mq_system_consumed_topic=mq_system_consumed_topic,
    )
    producer.producer = mock_producer

    id = "message-id"
    message = {"texts": ["message"]}
    destination = "test-destination"
    mocked = unittest.mock.ANY
    message_dto = PublishedMessageDTO(
        id=id,
        message=message,
        destination=destination,
    )

    producer.publish_message(message_dto)

    mock_producer.produce.assert_called_once_with(
        destination,
        mocked,
        callback=mocked,
    )


@pytest.mark.producer_service
def test_producer_service_without_destination(mock_producer):
    producer = ProducerService(
        mq_topic=mq_topic,
        mq_bootstrap_server=mq_bootstrap_server,
        mq_log_level=mq_log_level,
        mq_system_consumed_topic=mq_system_consumed_topic,
    )
    producer.producer = mock_producer

    id = "message-id"
    message = {"texts": ["message"]}
    destination = None
    mocked = unittest.mock.ANY
    message_dto = PublishedMessageDTO(
        id=id,
        message=message,
        destination=destination,
    )

    producer.publish_message(message_dto)

    mock_producer.produce.assert_called_once_with(
        mq_topic,
        mocked,
        callback=mocked,
    )


@pytest.mark.producer_service
def test_producer_service_with_same_system_consumed_destination(mock_producer):
    producer = ProducerService(
        mq_topic=mq_topic,
        mq_bootstrap_server=mq_bootstrap_server,
        mq_log_level=mq_log_level,
        mq_system_consumed_topic=mq_system_consumed_topic,
    )
    producer.producer = mock_producer

    id = "message-id"
    message = {"texts": ["message"]}
    destination = mq_system_consumed_topic
    mocked = unittest.mock.ANY
    message_dto = PublishedMessageDTO(
        id=id,
        message=message,
        destination=destination,
    )

    producer.publish_message(message_dto)

    mock_producer.produce.assert_called_once_with(
        mq_topic,
        mocked,
        callback=mocked,
    )
