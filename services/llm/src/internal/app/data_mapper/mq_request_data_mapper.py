from common.data_mapper import IDataMapper
from common.dto import ConsumedMessageDTO, LLMRequestDTO
from internal.domain.entity import LLMRequest


class MQRequestDataMapper(IDataMapper[LLMRequest, ConsumedMessageDTO[LLMRequestDTO]]):
    def to_domain_entity(self, dal_entity: ConsumedMessageDTO[LLMRequestDTO]) -> LLMRequest:
        llm_payload = LLMRequestDTO.model_validate(dal_entity.message)
        prompt = llm_payload.text
        return LLMRequest(
            id=dal_entity.id,
            prompt=prompt,
            destination=dal_entity.destination,
        )

    def to_dal_entity(self, domain_entity: LLMRequest) -> ConsumedMessageDTO[LLMRequestDTO]:
        text = domain_entity.prompt
        entity = LLMRequestDTO(text=text)
        return ConsumedMessageDTO[LLMRequestDTO](
            id=domain_entity.id,
            message=entity,
            destination=domain_entity.destination,
        )
