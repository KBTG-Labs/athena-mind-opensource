from common.data_mapper import IDataMapper
from common.dto import PublishedMessageDTO, VectorResponseDTO
from internal.domain.entity import VectorResponse


class MQResponseDataMapper(IDataMapper[VectorResponse, PublishedMessageDTO[VectorResponseDTO]]):
    def to_domain_entity(self, dal_entity: PublishedMessageDTO[VectorResponseDTO]) -> VectorResponse:
        dto = VectorResponseDTO.model_validate(dal_entity.message)
        return VectorResponse(
            id=dal_entity.id,
            results=dto.results,
            destination=dal_entity.destination,
            error=dal_entity.error,
        )

    def to_dal_entity(self, domain_entity: VectorResponse) -> PublishedMessageDTO[VectorResponseDTO]:
        dto = VectorResponseDTO(results=domain_entity.results)
        return PublishedMessageDTO[VectorResponseDTO](
            id=domain_entity.id,
            message=dto,
            destination=domain_entity.destination,
            error=domain_entity.error,
        )
