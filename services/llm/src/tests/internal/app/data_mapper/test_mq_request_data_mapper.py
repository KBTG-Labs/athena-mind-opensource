import pytest
from common.dto import ConsumedMessageDTO
from internal.app.data_mapper import MQRequestDataMapper
from internal.domain.entity import LLMRequest


@pytest.mark.llm_request_datamapper
def test_datamapper_mapping_to_domain_entity():
    id, message = "message-id", {"text": "test"}

    mapper = MQRequestDataMapper()
    dto = ConsumedMessageDTO(id=id, message=message)
    entity = mapper.to_domain_entity(dto)

    assert entity.id == id
    assert entity.prompt == "test"
    assert entity.destination == None


@pytest.mark.llm_request_datamapper
def test_datamapper_mapping_to_dal_entity():
    id, prompt = "message-id", "test"

    mapper = MQRequestDataMapper()
    entity = LLMRequest(id=id, prompt=prompt)
    dto = mapper.to_dal_entity(entity)

    assert dto.id == id
    assert dto.message.text == prompt
