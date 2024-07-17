import json
import pytest

from confluent_kafka import KafkaError

from common.dto import ConsumedMessageDTO
from internal.infra.external_service import ConsumerService

consume_max_batch_size = 10
consume_timeout = 1


@pytest.fixture
def consumer_service(
    mock_consumer,
    mock_vector_app_service,
):
    consumer = ConsumerService(
        vector_app_service=mock_vector_app_service,
        mq_group_id="vector-service-group",
        mq_bootstrap_server="localhost:9092",
        mq_offset_reset="earliest",
        mq_log_level="ERROR",
        mq_max_batch_size=consume_max_batch_size,
        mq_consume_timeout=consume_timeout,
    )
    consumer.consumer = mock_consumer
    return consumer


@pytest.mark.consumer_service
def test_consumer_service_consume_null_message(consumer_service):
    consumer_service.consumer.consume.return_value = None
    messages = consumer_service.consume()
    consumer_service.consumer.consume.assert_called_once_with(
        consume_max_batch_size,
        consume_timeout,
    )
    assert not messages


@pytest.mark.consumer_service
def test_consumer_service_consume_empty_messages(consumer_service):
    consumer_service.consumer.consume.return_value = []
    messages = consumer_service.consume()
    consumer_service.consumer.consume.assert_called_once_with(
        consume_max_batch_size,
        consume_timeout,
    )
    assert not messages


@pytest.mark.consumer_service
def test_consumer_service_consume_and_process_kafka_partition_eof(consumer_service, mock_kafka_message):
    mock_kafka_message.error.return_value = KafkaError(
        error=KafkaError._PARTITION_EOF
    )
    consumer_service.consumer.consume.return_value = [mock_kafka_message]
    messages = consumer_service.consume()
    status = consumer_service.process(messages)
    consumer_service.consumer.consume.assert_called_once_with(
        consume_max_batch_size,
        consume_timeout,
    )
    assert not status


@pytest.mark.consumer_service
def test_consumer_service_consume_and_process_kafka_error(consumer_service, mock_kafka_message):
    mock_kafka_message.error.return_value = KafkaError(
        error=KafkaError._FAIL
    )
    consumer_service.consumer.consume.return_value = [mock_kafka_message]
    messages = consumer_service.consume()
    status = consumer_service.process(messages)
    consumer_service.consumer.consume.assert_called_once_with(
        consume_max_batch_size,
        consume_timeout,
    )
    assert not status


@pytest.mark.consumer_service
def test_consumer_service_consume_success(consumer_service, mock_kafka_message):
    message = {
        "id": "test_1",
        "source": "vector-request",
        "message": {
            "texts": [
                "query: how much protein should a female eat",
                "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
            ]
        },
        "error": None
    }
    message_dto = ConsumedMessageDTO(
        id="test_1",
        source="vector-request",
        message={
            "texts": [
                "query: how much protein should a female eat",
                "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
            ]
        },
        error=None
    )

    mock_kafka_message.error.return_value = None
    mock_kafka_message.value.return_value = json.dumps(message).encode('utf-8')
    consumer_service.consumer.consume.return_value = [mock_kafka_message]
    messages = consumer_service.consume()
    status = consumer_service.process(messages)
    consumer_service.consumer.consume.assert_called_once_with(
        consume_max_batch_size,
        consume_timeout,
    )
    consumer_service.vector_app_service.handle_queue.assert_called_once_with([
                                                                             message_dto])
    assert status


@pytest.mark.consumer_service
def test_consumer_service_consume_failed_with_json_validation_error(consumer_service, mock_kafka_message):
    message = "Invalid Payload"
    mock_kafka_message.error.return_value = None
    mock_kafka_message.value.return_value = json.dumps(message).encode('utf-8')
    consumer_service.consumer.consume.return_value = [mock_kafka_message]
    messages = consumer_service.consume()
    status = consumer_service.process(messages)
    consumer_service.consumer.consume.assert_called_once_with(
        consume_max_batch_size,
        consume_timeout,
    )
    assert not status


@pytest.mark.consumer_service
def test_consumer_service_subscribe_to_be_called(consumer_service, mock_consumer):
    consumer_service.subscribe(topics=["topics"])
    mock_consumer.subscribe.assert_called_once_with(["topics"])


@pytest.mark.consumer_service
def test_consumer_service_close_to_be_called(consumer_service, mock_consumer):
    consumer_service.close()
    mock_consumer.close.assert_called_once()


@pytest.mark.consumer_service
def test_consumer_service_commit_to_be_called(consumer_service, mock_consumer):
    for asynchronous in [True, False]:
        consumer_service.commit(asynchronous=asynchronous)
        mock_consumer.commit.assert_called_with(asynchronous=asynchronous)
