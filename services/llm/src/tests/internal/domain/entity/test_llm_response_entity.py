import pytest
from internal.domain.entity import LLMResponse


@pytest.mark.llm_request_entity
def test_llm_request_entity():
    id, results, destination, error = "message-id", "results-test", "destination-test", None

    entity = LLMResponse(
        id=id,
        results=results,
        destination=destination,
        error=error,
    )

    assert entity.id == id
    assert entity.results == results
    assert entity.destination == destination
    assert entity.error == error
