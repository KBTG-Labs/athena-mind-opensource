import pytest

from common.dto import ConsumedMessageDTO
from internal.app.data_mapper import MQRequestDataMapper
from internal.domain.entity import VectorRequest


@pytest.mark.vector_request_datamapper
def test_datamapper_mapping_to_domain_entity():
    id = "message-id"
    message = {
        "texts": [
            "query: how much protein should a female eat",
            "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
        ]
    }

    mapper = MQRequestDataMapper()
    dto = ConsumedMessageDTO(
        id=id, 
        message=message,
    )

    entity = mapper.to_domain_entity(dto)

    assert entity.id == id
    assert entity.texts == message["texts"]

@pytest.mark.vector_request_datamapper
def test_datamapper_mapping_to_dal_entity():
    id = "message-id"
    texts = [
        "query: how much protein should a female eat",
        "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 i     s 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or traini     ng for a marathon. Check out the chart below to see how much protein you should be eating each day."
    ]

    mapper = MQRequestDataMapper()
    entity = VectorRequest(
        id=id,
        texts=texts,
    )
    dto = mapper.to_dal_entity(entity)

    assert dto.id == id
    assert dto.message.texts == texts