from common.data_mapper import IDataMapper
from common.dto import ConsumedMessageDTO, VectorRequestDTO
from internal.domain.entity import VectorRequest


class MQRequestDataMapper(IDataMapper[VectorRequest, ConsumedMessageDTO[VectorRequestDTO]]):
    def to_domain_entity(self, dal_entity: ConsumedMessageDTO[VectorRequestDTO]) -> VectorRequest:
        vector_payload = VectorRequestDTO.model_validate(dal_entity.message)
        return VectorRequest(
            id=dal_entity.id,
            texts=vector_payload.texts,
            destination=dal_entity.destination,
        )

    def to_dal_entity(self, domain_entity: VectorRequest) -> ConsumedMessageDTO[VectorRequestDTO]:
        dto = VectorRequestDTO(texts=domain_entity.texts)
        return ConsumedMessageDTO[VectorRequestDTO](
            id=domain_entity.id,
            message=dto,
            destination=domain_entity.destination,
        )
