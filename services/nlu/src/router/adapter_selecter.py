import functools
import json

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_agent(result, default_agent):
    """Simple sequential tool calling helper."""
    # json_text = result.content
    json_text = result
    if json_text.startswith('```json'):
        json_text = json_text[7:]
    if json_text.endswith('```'):
        json_text = json_text[:-3]

    try:
        content = json.loads(json_text)
        if isinstance(content["next"], dict): 
            if "worker" in content["next"]:
                return { "next": content["next"]["worker"] }
            elif "role" in content["next"]:
                return { "next": content["next"]["role"] }
            else:
                return { "next": list(content["next"].values())[0] }
    except Exception:
        return { "next": default_agent }
    
    return content

def create_supervisor(members, llm_supervisor, default_adapter_name):
    member_prompt = ""
    for m in members:
        member_prompt += 'NAME: ' + m['name'] + ' -- ROLE: ' + m['role'] + '\n'
    
    answer_format = '{{\"next\": ANSWER}}'
    system_prompt = f'''You are a supervisor tasked with managing a conversation between the following workers:  
{member_prompt}
Given the following user request, respond with the worker to act next. Each worker will perform a task and respond with their results and status. Answer in the raw JSON format ({answer_format})'''
    options = [k['name'] for k in members]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("messages"),
            # (
            #     "user",
            #     "Given the conversation above, who should act next?"
            #     "Select one of: {options}",
            # ),
        ]
    ).partial(options=str(options))
    get_agent_with_default = functools.partial(get_agent, default_agent=default_adapter_name)
    supervisor_chain = prompt | llm_supervisor | get_agent_with_default
    return supervisor_chain