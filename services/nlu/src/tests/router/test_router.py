import pytest
from langchain_core.messages import AIMessage, HumanMessage

from common.agent_state import AgentState
from router.adapter_selecter import get_agent
from router.graph import agent_node


@pytest.mark.router
def test_agent():
    default_agent = "General Handler"
    # case 1: normal
    json_text = """{\"next\": \"Account Expert\"}"""
    result = get_agent(json_text, default_agent)
    assert result == {"next": "Account Expert"}

    # case 2: startwith ```json
    json_text = """```json{\"next\": {\"worker\": \"Account Expert\"}}```"""
    result = get_agent(json_text, default_agent)
    assert result == {"next": "Account Expert"}

    # case 3: unexpected result from llm
    json_text = """{\"next\": {\"worker\": \"Account Expert\"}}"""
    result = get_agent(json_text, default_agent)
    assert result == {"next": "Account Expert"}

    json_text = """{\"next\": {\"role\": \"Account Expert\"}}"""
    result = get_agent(json_text, default_agent)
    assert result == {"next": "Account Expert"}

    json_text = """{\"next\": {\"unexpected\": \"Account Expert\"}}"""
    result = get_agent(json_text, default_agent)
    assert result == {"next": "Account Expert"}

    json_text = """{\"next\": {\"unexpected_1\": \"Account Expert\", \"unexpected_2\": \"General Handler\"}}"""
    result = get_agent(json_text, default_agent)
    assert result == {"next": "Account Expert"}

    # case 4: default agent
    json_text = """{"""
    result = get_agent(json_text, default_agent)
    assert result == {"next": "General Handler"}


@pytest.mark.router
def test_agent_node(mock_agent):
    name = "Account Expert"
    state = AgentState(
        messages=[
            HumanMessage(content="สวัสดี"),
            AIMessage(content="สวัสดีค่ะ ฉันชื่อจินตนา ฉันเป็นผู้ช่วยดิจิทัล มีอะไรที่ฉันช่วยได้ไหม"),
            HumanMessage(content="FCD คืออะไร"),
        ],
        next=name,
    )
    mock_agent.invoke.return_value = "FCD ย่อมาจาก เงินฝากสกุลเงินต่างประเทศ"

    result = agent_node(state, mock_agent, "Account Expert")

    assert isinstance(result, dict)
    assert isinstance(result["messages"], list)
    assert result == {"messages": [HumanMessage(content="FCD ย่อมาจาก เงินฝากสกุลเงินต่างประเทศ", name=name)]}

