import uuid

import chainlit as cl
from langchain.schema import AIMessage, HumanMessage
from langchain.schema.runnable.config import RunnableConfig

from client.config import Configs
from client.constructor import get_graph
from common.constant.domain import APP_NLU as NLU
from common.decorator import trace
from common.log import Logger, configure_logging, correlation_id
from common.telemetry import configure_tracing

configs = Configs()
configure_logging(log_level=configs.log_level, log_timezone=configs.log_timezone)
configure_tracing(
    name=configs.service_name,
    enable_telemetry=configs.enable_telemetry,
    collector_endpoint=configs.telemetry_collector_endpoint,
)


logger = Logger.get_logger(NLU)

graph = get_graph(configs)

@cl.on_chat_start
@trace
async def on_chat_start():
    runnable = graph
    cl.user_session.set("runnable", runnable)
    cl.user_session.set("history", [])

    new_id = str(uuid.uuid4())
    cl.user_session.set("correlation_id", new_id)

@cl.on_message
@trace
async def run_convo(message: cl.Message):
    inputs = {"messages": [HumanMessage(content=message.content)]}

@cl.on_message
@trace
async def on_message(message: cl.Message):
    correlation_id.set(cl.user_session.get("correlation_id"))
    logger.info({
        "message": "user enter a message",
        "input": message.content,
    })
    runnable = cl.user_session.get("runnable")  # type: Runnable
    history = cl.user_session.get("history")  # type: list
    context = [
        HumanMessage(content=h['content']) if h['role'] == 'user' else AIMessage(content=h['content'])
        for h in history
    ]
    context.append(HumanMessage(content=message.content))
    res = await runnable.ainvoke({'messages': context}, config=RunnableConfig(callbacks=[
        cl.LangchainCallbackHandler(
            to_ignore=["ChannelRead", "RunnableLambda", "ChannelWrite", "__start__", "_execute"]
            # can add more into the to_ignore: "agent:edges", "call_model"
            # to_keep=
    )]))
    logger.info({
        "message": "assistant respond with a message",
        "output": res["messages"][-1].content,
    })
    history.append({"role": "user", "content": message.content})
    history.append({"role": "assistant", "content": res["messages"][-1].content})
    await cl.Message(content=res["messages"][-1].content).send()
