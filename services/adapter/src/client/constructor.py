import importlib
import json
import os
from typing import Any, Dict, List
from urllib.parse import quote_plus

from langchain.chains.base import Chain
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLanguageModel
from mq_client import DBProvider, MQClient, MQConfig, MQProvider

from client.config import Configs
from common.constant.domain import APP_ADAPTER as ADAPTER
from common.constant.domain import INFRA_MQ_CLIENT as MQ_CLIENT
from common.log import Logger
from embeddings import MQEmbeddings
from language_models import MQLanguageModel
from rag import init_rag_chain, init_retriever

logger = Logger.get_logger(ADAPTER)

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

def init_mq_embeddings(mq_client, topic: str, consume_topic: str) -> MQEmbeddings:
    return MQEmbeddings(
        mq=mq_client,
        topic=topic,
        consume_topic=consume_topic,
    )

def init_adapter(
        adapter_name: str,
        adapter_type: str,
        adapter_config: Dict[str, Any],
        opensearch_url: str,
        mongo_url: str,
        llm: BaseLanguageModel,
        embeddings: str | Embeddings,
    ) -> Chain:
    match adapter_type:
        case "rag":
            prompt_dir = adapter_config["prompt"]["dir"]
            query_generate_prompt = os.path.join(prompt_dir, adapter_config["prompt"]["query_generate_prompt"])
            qa_prompt = os.path.join(prompt_dir, adapter_config["prompt"]["qa_prompt"])
            response_control_prompt = os.path.join(prompt_dir, adapter_config["prompt"]["response_control_prompt"])
                
            retriever = init_retriever(
                embedding_model=embeddings,
                opensearch_url=opensearch_url,
                opensearch_index=adapter_config["opensearch_index"],
                mongo_url=mongo_url,
                mongo_db_name=adapter_config["mongo_db_name"],
                mongo_collection_name=adapter_config["mongo_collection_name"],
            )
            chain = init_rag_chain(
                retriever=retriever, 
                llm=llm,
                qg_prompt_path=query_generate_prompt,
                qa_prompt_path=qa_prompt,
                rc_prompt_path=response_control_prompt,
            )
            
            logger.info({
                "message": "init adapter",
                "adapter_name": adapter_name,
                "adapter_type": adapter_type,
                "opensearch_index": adapter_config["opensearch_index"],
                "mongo_db": adapter_config["mongo_db_name"],
                "mongo_collection": adapter_config["mongo_collection_name"],
            })

            return chain
        case "custom":
            chain = importlib.import_module(f'custom_chain.{adapter_name}').get_chain(llm)
            logger.info({
                "message": "init adapter",
                "adapter_name": adapter_name,
                "adapter_type": adapter_type,
            })
            return chain
        case _:
            raise ValueError("Adapter type must be either 'rag' or 'custom'.")

def get_adapters(configs: Configs) -> Dict[str, Chain]:
    with open(configs.adapter_config_path) as f:
            members = json.load(f)
    
    mq_client = init_mq_client(
        host=configs.mq_client_host,
        consume_topics=[configs.mq_client_llm_consume_topic, configs.mq_client_vector_consume_topic],
        sdk_group=configs.mq_client_consumer_group_id,
        consume_timeout=configs.mq_client_consume_timeout,
    )

    llm = init_mq_language_model(
        mq_client=mq_client,
        topic=configs.mq_client_llm_topic,
        consume_topic=configs.mq_client_llm_consume_topic,
    )

    embeddings = init_mq_embeddings(
        mq_client=mq_client,
        topic=configs.mq_client_vector_topic,
        consume_topic=configs.mq_client_vector_consume_topic,
    )

    adapters = {}
    for member in members:
        adapters[member['adapter']] = init_adapter(
            adapter_name=member['adapter'],
            adapter_type=member['type'],
            adapter_config=member.get('config', {}),
            opensearch_url=configs.opensearch_host,
            mongo_url=f"mongodb://{quote_plus(configs.mongo_username)}:{quote_plus(configs.mongo_password)}@{configs.mongo_host}",
            llm=llm,
            embeddings=embeddings,
        )
    return adapters