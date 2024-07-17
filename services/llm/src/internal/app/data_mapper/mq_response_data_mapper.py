from common.data_mapper import IDataMapper
from common.dto import PublishedMessageDTO, LLMResponseDTO
from internal.domain.entity import LLMResponse


class MQResponseDataMapper(IDataMapper[LLMResponse, PublishedMessageDTO[LLMResponseDTO]]):
    def to_domain_entity(self, dal_entity: PublishedMessageDTO[LLMResponseDTO]) -> LLMResponse:
        dto = LLMResponseDTO.model_validate(dal_entity.message)
        return LLMResponse(
            id=dal_entity.id,
            results=dto.results,
            destination=dal_entity.destination,
            error=dal_entity.error,
        )

    def to_dal_entity(self, domain_entity: LLMResponse) -> PublishedMessageDTO[LLMResponseDTO]:
        dto = LLMResponseDTO(results=domain_entity.results)
        return PublishedMessageDTO[LLMResponseDTO](
            id=domain_entity.id,
            message=dto,
            destination=domain_entity.destination,
            error=domain_entity.error,
        )
