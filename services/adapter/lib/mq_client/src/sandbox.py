import asyncio
from lib.mq_client.src.mq_client import MQClient, MQProvider, MQConfig, DBProvider


async def main(mq: MQClient):
    payload = {"texts": ["how much protein should a female eat", "南瓜的家常做法"]}

    response1 = await mq.send_request(
        topic="vector-request",
        payload=payload)

    print(f"Final Response1: {response1}\n")

    response2 = await mq.send_request(
        topic="vector-request",
        payload=payload)

    print(f"Final Response2: {response2}\n")

    response3 = await mq.send_request(
        topic="vector-request",
        payload=payload)

    print(f"Final Response3: {response3}\n")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    mq = MQClient(
        mq_provider=MQProvider.KAFKA.value,
        mq_config=MQConfig(host="localhost:9092",
                           consume_topics=["vector-response"]),
        db_provider=DBProvider.LOCAL.value,
        db_config=None,
        sdk_group="test",
        # event_loop=loop,
    )

    loop.run_until_complete(main(mq))
