import pytest
from common.dto import PublishedMessageDTO
from internal.app.data_mapper import MQResponseDataMapper
from internal.domain.entity import LLMResponse


@pytest.mark.llm_response_datamapper
def test_datamapper_mapping_to_domain_entity():
    id, message = "message-id", {"results": "test"}

    mapper = MQResponseDataMapper()
    dto = PublishedMessageDTO(id=id, message=message)
    entity = mapper.to_domain_entity(dto)

    assert entity.id == id
    assert entity.results == message["results"]


@pytest.mark.llm_response_datamapper
def test_datamapper_mapping_to_dal_entity():
    id, results = "message-id", "test"

    mapper = MQResponseDataMapper()
    entity = LLMResponse(id=id, results=results)
    dto = mapper.to_dal_entity(entity)

    assert dto.id == id
    assert dto.message.results == results
    assert dto.error is None
