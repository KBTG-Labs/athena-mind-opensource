import functools
from asyncio.exceptions import TimeoutError as AsyncioTimeoutError

from httpx import ConnectError, ConnectTimeout
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph

from common import AgentState
from common.constant.domain import APP_NLU as NLU
from common.decorator import retry, trace
from common.log import Logger

DEFAULT_FALLBACK_MESSAGE = """ขออภัย ขณะนี้ระบบมีปัญหา ทำให้ฉันไม่สามารถตอบคำถามนี้ได้ ขออภัยในความไม่สะดวก"""

logger = Logger.get_logger(NLU)


@retry(
    max_retries=3,
    delay=1,
    backoff=2,
    logger=logger,
    exceptions=(ConnectError, ConnectTimeout, AsyncioTimeoutError),
    fallback_response={"messages": [HumanMessage(content=DEFAULT_FALLBACK_MESSAGE)]}
)
@trace
def agent_node(state, agent, name):
    logger.info({
        "message": "agent node invoke state",
        "agent_name": name,
        "state": state,
    })
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result, name=name)]}

def create_routing_graph(adapters, supervisor):
    workflow = StateGraph(AgentState)
    conditional_map = {}
    for name in adapters:
        node = functools.partial(agent_node, agent=adapters[name], name=name)
        workflow.add_node(name, node)
        workflow.add_edge(name, "__end__")
        conditional_map[name] = name
    workflow.add_node("supervisor", supervisor)
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
    workflow.set_entry_point("supervisor")
    graph = workflow.compile()
    return graph