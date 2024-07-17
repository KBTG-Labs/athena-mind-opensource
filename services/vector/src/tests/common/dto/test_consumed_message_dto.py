import pytest

from common.exception import Error, ErrorCode

from common.dto import ConsumedMessageDTO


@pytest.mark.consumed_message_dto
def test_consumed_message_dto_serialize_model():
    id, message, source, destination, error = \
        "message-id", {"text": "test"}, "source-test", "destination-test", None
    dto = ConsumedMessageDTO(
        id=id,
        message=message,
        source=source,
        destination=destination,
        error=error
    )

    dto_dict = dto.model_dump()
    assert dto_dict["id"] == dto.id
    assert dto_dict["message"] == dto.message
    assert dto_dict["source"] == dto.source
    assert dto_dict["destination"] == dto.destination
    assert dto_dict["error"] == dto.error


@pytest.mark.consumed_message_dto
def test_consumed_message_dto_serialize_model_with_error():
    id, message, source, destination, = \
        "message-id", {"text": "test"}, "source-test", "destination-test"
    error = Error(
        code=ErrorCode.MAXIMUM_RETRIES_REACH,
        detail="test",
    )
    dto = ConsumedMessageDTO(
        id=id,
        message=message,
        source=source,
        destination=destination,
        error=error)

    dto_dict = dto.model_dump()
    assert dto_dict["error"] == error.model_dump()
