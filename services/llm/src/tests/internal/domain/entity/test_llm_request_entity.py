import pytest
from internal.domain.entity import LLMRequest


@pytest.mark.llm_request_entity
def test_llm_request_entity():
    id, prompt, destination = "message-id", "test", "destination-test"

    entity = LLMRequest(id=id, prompt=prompt, destination=destination)

    assert entity.id == id
    assert entity.prompt == prompt
    assert entity.destination == destination
