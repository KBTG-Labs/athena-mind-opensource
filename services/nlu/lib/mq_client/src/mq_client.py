import asyncio
from asyncio import AbstractEventLoop
from typing import Any, Dict, Optional
import logging

from db.common import DBConfig, DBProvider
from db.factory import create_db
from mq.common import MQConfig, MQProvider, QueueDTO
from mq.factory import create_mq
from util.id import generate_id

class MQClient:
    def __init__(
        self,
        mq_provider: MQProvider,
        mq_config: MQConfig,
        db_provider: DBProvider,
        db_config: Optional[DBConfig],
        event_loop: AbstractEventLoop = None,
        sdk_group="",
        polling_interval=0.1,
        timeout=30.0,
        service_name="mq_client",
        logger=logging.getLogger("mq.client"),
    ):
        self.event_loop = event_loop
        self.subscription_data: Dict[str, asyncio.Future] = {}
        self.stateful_sdk = db_provider == DBProvider.LOCAL.value
        self.polling_interval = polling_interval
        self.mq_topics = mq_config.consume_topics
        self.timeout = timeout
        # Factory Create MQ
        self.mq_consumer, self.mq_producer = create_mq(
            mq_provider=mq_provider,
            mq_config=mq_config,
            sdk_group=sdk_group,
            require_unique_id=self.stateful_sdk,
            logger=logger,
        )
        # Factory Create DB
        self.repository = create_db(
            db_provider=db_provider,
            db_config=db_config,
        )
        # Start Consumer Side
        self.is_event_loop_require_created = self.event_loop == None
        self.is_event_loop_started = False
        self.__setup_consumer()

        self.service_name = service_name
        self.logger = logger

    """
    Message Queue - Consumer Side:
    - Consume Message from Messaging Queue
    - Update Repository from Messaging Queue
    """

    def __setup_event_loop(self):
        self.is_event_loop_started = True
        if self.is_event_loop_require_created:
            self.event_loop = asyncio.get_event_loop()
        self.event_loop.create_task(coro=self.__start_consumer())

    def __setup_consumer(self):
        # Create Event Loop if Not Provided
        # if self.is_event_loop_require_created:
        #     self.event_loop = asyncio.get_event_loop()
        # Setup Consumer
        self.mq_consumer.subscribe(topics=self.mq_topics)
        self.mq_consumer.register_callback(self.__consume_response)
        # Start Consumer
        # self.event_loop.create_task(coro=self.__start_consumer())

    async def __start_consumer(self):
        try:
            running = True
            while running:
                try:
                    self.__poll_mq()  # Consume message from queue
                    self.__poll_db()  # Poll message from DB
                    # Delay Iteration
                    await asyncio.sleep(self.polling_interval)
                except Exception as e:
                    # Handle Consumer Error
                    self.logger.error({
                        "message": "Failed to handle message",
                        "error": str(e),
                        "service": self.service_name,
                    })
        finally:
            # Close Consumer
            self.mq_consumer.close()
            # Close Event Loop if Created by SDK
            # if self.is_event_loop_require_created:
            #     self.event_loop.stop()

    def __poll_mq(self):
        # Consume Message from Queue
        self.mq_consumer.consume()

    def __poll_db(self):
        # Iterate Subscription Data
        # NOTE: must iterate with list(self.subscription_data.keys()) to prevent subscription_data size unexpectedly changed
        for id in list(self.subscription_data.keys()):
            # Check the response is registered in the repository
            future = self.subscription_data[id]
            message = self.repository.get(id)
            if message is None:
                continue
            # If the response is already registered, set the subscription data
            try:
                future.set_result(message)
            except asyncio.exceptions.InvalidStateError as e:
                self.logger.error({
                    "message": "Invalid state error",
                    "error": str(e),
                    "service": self.service_name,
                })

            # Remove all unused data from the repository and subscription
            self.repository.delete(id)
            del self.subscription_data[id]

    def __consume_response(self, dto: QueueDTO) -> bool:
        # If SDK is stateful (LocalDB) and SDK doesn't own the given ID, the response won't be save in the repository
        if self.stateful_sdk and dto.id not in self.subscription_data.keys():
            return
        # Save the response with the given ID
        response = dto.message
        self.repository.set(dto.id, response)

    """
    Message Queue - Publisher Side:
    - Publish Message with Topic & Payload
    - Wait for the Response 
    """

    async def __send_request(self, topic: str, payload: Any, destination: Optional[str] = '') -> Any:
        # Generate Unique ID for Each Request
        message_id = generate_id()
        future = asyncio.Future()
        self.subscription_data[message_id] = future
        # Send the Request to MQ
        payload = QueueDTO(
            id=message_id,
            source=self.service_name,
            message=payload,
            destination=destination,
        )
        self.mq_producer.publish_message(topic=topic, payload=payload)
        # Wait Response
        result = await self.subscription_data[message_id]
        return result

    async def send_request(self, topic: str, payload: Any, destination: Optional[str] = '') -> Any:
        if not self.is_event_loop_started:
            self.__setup_event_loop()
        # Send the Request and Wait for the Response with Timeout
        task = self.event_loop.create_task(
            self.__send_request(topic=topic, payload=payload, destination=destination))
        response = await asyncio.wait_for(task, timeout=self.timeout)
        return response
