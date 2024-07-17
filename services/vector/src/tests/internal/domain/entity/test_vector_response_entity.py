import pytest

from internal.domain.entity import VectorResponse


@pytest.mark.vector_response_entity
def test_vector_response_entity():
    id = "message-id"
    results = [[0.1]]
    destination = "destination-test"

    entity = VectorResponse(
        id=id,
        results=results,
        destination=destination,
    )

    assert entity.id == id
    assert entity.results == results
    assert entity.destination == destination
    assert entity.error == None
