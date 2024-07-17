import pytest

from internal.domain.entity import VectorRequest


@pytest.mark.vector_request_entity
def test_vector_request_entity():
    id = "message-id"
    texts = [
        "query: how much protein should a female eat",
        "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
    ]
    destination = "destination-test"

    entity = VectorRequest(
        id=id,
        texts=texts,
        destination=destination,
    )

    assert entity.id == id
    assert entity.texts == texts
    assert entity.destination == destination


@pytest.mark.vector_request_entity
def test_vector_request_entity_to_request():
    id = "message-id"
    texts = [
        "query: how much protein should a female eat",
        "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
    ]

    entity = VectorRequest(
        id=id,
        texts=texts,
    )

    assert entity.to_request() == texts
