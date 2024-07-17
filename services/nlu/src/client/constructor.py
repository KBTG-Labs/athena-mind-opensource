import json
from typing import List

from langgraph.graph.graph import CompiledGraph
from langserve import RemoteRunnable
from mq_client import DBProvider, MQClient, MQConfig, MQProvider

from client.config import Configs
from common.constant.domain import INFRA_MQ_CLIENT as MQ_CLIENT
from common.log import Logger
from language_models import MQLanguageModel
from router import create_routing_graph, create_supervisor


def init_mq_client(
    host: str,
    consume_topics: List[str],
    sdk_group: str,
    consume_timeout: float,
) -> MQClient:
    mq_client = MQClient(
        mq_provider=MQProvider.KAFKA.value,
        mq_config=MQConfig(
            host=host,
            consume_topics=consume_topics,
            consume_timeout=consume_timeout
        ),
        db_provider=DBProvider.LOCAL.value,
        db_config=None,
        sdk_group=sdk_group,
        logger=Logger.get_logger(MQ_CLIENT),
    )

    return mq_client


def init_mq_language_model(mq_client, topic: str, consume_topic: str) -> MQLanguageModel:
    return MQLanguageModel(
        mq=mq_client,
        topic=topic,
        consume_topic=consume_topic,
    )

def get_graph(configs: Configs) -> CompiledGraph:
    with open(configs.adapter_config_path) as f:
        members = json.load(f)
    
    mq_client = init_mq_client(
        host=configs.mq_client_host,
        consume_topics=[configs.mq_client_llm_consume_topic],
        sdk_group=configs.mq_client_consumer_group_id,
        consume_timeout=configs.mq_client_consume_timeout,
    )

    llm = init_mq_language_model(
        mq_client=mq_client,
        topic=configs.mq_client_llm_topic,
        consume_topic=configs.mq_client_llm_consume_topic,
    )

    supervisor = create_supervisor(members, llm, configs.default_adapter_name)

    adapters = {}
    for member in members:
        adapters[member['name']] = RemoteRunnable(f"http://{member['host']}/api/v1/chain/{member['adapter']}")
    graph = create_routing_graph(adapters, supervisor)
    return graph